import sqlite3
import json
import logging
from pathlib import Path
from .web_client import TickTickWebClient

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "ticktick_cache.db"

class TickTickDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self.web_client = TickTickWebClient()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    title TEXT,
                    data_json TEXT,
                    is_deleted INTEGER DEFAULT 0
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    data_json TEXT,
                    is_closed INTEGER DEFAULT 0
                )
            """)

    def get_checkpoint(self):
        cur = self.conn.execute("SELECT value FROM sync_state WHERE key = 'checkpoint'")
        row = cur.fetchone()
        if row:
            return int(row["value"])
        return 0

    def set_checkpoint(self, checkpoint):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO sync_state (key, value) VALUES ('checkpoint', ?)",
                (str(checkpoint),)
            )

    def is_sync_ready(self):
        return self.web_client.username is not None and self.web_client.password is not None

    def sync(self):
        if not self.is_sync_ready():
            logger.error("Web sync credentials not configured. Skipping sync.")
            return False

        checkpoint = self.get_checkpoint()
        logger.info(f"Syncing from checkpoint {checkpoint}...")
        
        try:
            batch_data = self.web_client.batch_check(checkpoint)
            if not batch_data:
                logger.error("Failed to fetch batch data (login might have failed).")
                return False
        except Exception as e:
            logger.error(f"Exception during web sync: {e}")
            return False

        new_checkpoint = batch_data.get("checkPoint", checkpoint)
        
        with self.conn:
            # Process Projects
            project_profiles = batch_data.get("projectProfiles") or []
            for p in project_profiles:
                p_id = p.get("id")
                is_closed = 1 if p.get("closed") else 0
                self.conn.execute(
                    "INSERT OR REPLACE INTO projects (id, name, data_json, is_closed) VALUES (?, ?, ?, ?)",
                    (p_id, p.get("name", ""), json.dumps(p), is_closed)
                )

            # Process Tasks
            sync_task_bean = batch_data.get("syncTaskBean") or {}
            tasks_update = sync_task_bean.get("update") or []
            for t in tasks_update:
                t_id = t.get("id")
                status = t.get("status", 0)
                # status 2 = completed, status -1 or deleted=1 could mean deleted. 
                # Let's keep them all but mark deleted.
                is_deleted = 1 if t.get("deleted") == 1 else 0
                
                self.conn.execute(
                    "INSERT OR REPLACE INTO tasks (id, project_id, title, data_json, is_deleted) VALUES (?, ?, ?, ?, ?)",
                    (t_id, t.get("projectId"), t.get("title", ""), json.dumps(t), is_deleted)
                )
            
            # The API might return explicit deletes in `delete` arrays, but usually `deleted: 1` flag is used in `update`.
            tasks_delete = sync_task_bean.get("delete") or []
            for del_item in tasks_delete:
                t_id = del_item.get("taskId")
                if t_id:
                    self.conn.execute("UPDATE tasks SET is_deleted = 1 WHERE id = ?", (t_id,))

        self.set_checkpoint(new_checkpoint)
        logger.info(f"Sync complete. New checkpoint: {new_checkpoint}")
        return True

    def get_projects(self):
        cur = self.conn.execute("SELECT data_json FROM projects WHERE is_closed = 0")
        return [json.loads(row["data_json"]) for row in cur.fetchall()]

    def get_project(self, project_id):
        cur = self.conn.execute("SELECT data_json FROM projects WHERE id = ?", (project_id,))
        row = cur.fetchone()
        return json.loads(row["data_json"]) if row else None

    def get_project_tasks(self, project_id):
        cur = self.conn.execute("SELECT data_json FROM tasks WHERE project_id = ? AND is_deleted = 0", (project_id,))
        return [json.loads(row["data_json"]) for row in cur.fetchall()]

    def get_task(self, task_id):
        cur = self.conn.execute("SELECT data_json FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        return json.loads(row["data_json"]) if row else None
        
    def find_tasks_by_title(self, title_substring):
        cur = self.conn.execute(
            "SELECT data_json FROM tasks WHERE title LIKE ? AND is_deleted = 0", 
            (f"%{title_substring}%",)
        )
        return [json.loads(row["data_json"]) for row in cur.fetchall()]

    def get_pinned_tasks(self):
        cur = self.conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
        tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
        pinned_tasks = [
            task
            for task in tasks
            if task.get("pinnedTime") and task.get("status") != 2
        ]
        return sorted(
            pinned_tasks,
            key=lambda task: task.get("pinnedTime") or "",
            reverse=True,
        )
