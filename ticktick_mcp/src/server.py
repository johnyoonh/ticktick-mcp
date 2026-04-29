import asyncio
import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from .ticktick_client import TickTickClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("ticktick")

# Create TickTick client
ticktick = None


def initialize_client():
    global ticktick
    try:
        # Check if .env file exists with access token
from pathlib import Path
from .ticktick_client import TickTickClient
from .db import TickTickDB

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("ticktick")

# Create TickTick clients
ticktick = None
db = None

def initialize_client():
    global ticktick, db
    try:
        env_path = Path(".env")
        if not env_path.exists():
            logger.error("No .env file found. Please set up authentication.")
            return False

        with open(env_path, "r") as f:
            content = f.read()
            if "TICKTICK_ACCESS_TOKEN" not in content:
                logger.error("No access token found in .env file.")
                return False

        ticktick = TickTickClient()
        try:
            db = TickTickDB()
        except Exception as e:
            logger.error(f"Failed to initialize local DB cache: {e}")
            logger.error("Make sure TICKTICK_USERNAME and TICKTICK_PASSWORD are set for web sync.")

        logger.info("TickTick client initialized successfully")

        test_response = ticktick._make_request("GET", "/project/test_connection")
        if isinstance(test_response, dict) and test_response.get("error", "").startswith("401"):
            logger.error("Failed to access TickTick API: Invalid or expired access token")
            return False

        return True
    except Exception as e:
        logger.error(f"Failed to initialize TickTick client: {e}")
        return False

# Format functions remain the same
def format_task(task: Dict) -> str:
    """Format a task into a human-readable string."""
    formatted = f"ID: {task.get('id', 'No ID')}\n"
    formatted += f"Title: {task.get('title', 'No title')}\n"
    formatted += f"Project ID: {task.get('projectId', 'None')}\n"

    if task.get("startDate"):
        formatted += f"Start Date: {task.get('startDate')}\n"
    if task.get("dueDate"):
        formatted += f"Due Date: {task.get('dueDate')}\n"

    priority_map = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    priority = task.get("priority", 0)
    formatted += f"Priority: {priority_map.get(priority, str(priority))}\n"

    tags = task.get("tags", [])
    if tags:
        formatted += f"Tags: {', '.join(tags)}\n"

    status = "Completed" if task.get("status") == 2 else "Active"
    formatted += f"Status: {status}\n"

    if task.get("content"):
        formatted += f"\nContent:\n{task.get('content')}\n"

    items = task.get("items", [])
    if items:
        formatted += f"\nSubtasks ({len(items)}):\n"
        for item in items:
            item_status = "✓" if item.get("status") == 1 else "□"
            formatted += f"[{item_status}] {item.get('title', 'No title')} (ID: {item.get('id', 'No ID')})\n"

    return formatted

def format_project(project: Dict) -> str:
    """Format a project into a human-readable string."""
    formatted = f"Name: {project.get('name', 'No name')}\n"
    formatted += f"ID: {project.get('id', 'No ID')}\n"

    if project.get("color"):
        formatted += f"Color: {project.get('color')}\n"
    if project.get("viewMode"):
        formatted += f"View Mode: {project.get('viewMode')}\n"
    if "closed" in project:
        formatted += f"Closed: {'Yes' if project.get('closed') else 'No'}\n"
    if project.get("kind"):
        formatted += f"Kind: {project.get('kind')}\n"

    return formatted

# MCP Tools
@mcp.tool()
async def sync_cache() -> str:
    """Force a delta sync with TickTick to update the local SQLite cache."""
    if not db:
        if not initialize_client() or not db:
            return "Failed to initialize DB. Make sure TICKTICK_USERNAME and PASSWORD are set."
    
    success = db.sync()
    if success:
        return f"Cache synced successfully. Checkpoint: {db.get_checkpoint()}"
    return "Failed to sync cache."

@mcp.tool()
async def get_projects() -> str:
    """Get all projects from TickTick."""
    if not db:
        if not initialize_client() or not db:
            return "Failed to initialize DB. Make sure TICKTICK_USERNAME and PASSWORD are set."

    try:
        db.sync() # Auto sync before read
        projects = db.get_projects()

        if not projects:
            return "No projects found."

        result = f"Found {len(projects)} projects:\n\n"
        for i, project in enumerate(projects, 1):
            result += f"Project {i}:\n" + format_project(project) + "\n"

        return result
    except Exception as e:
        logger.error(f"Error in get_projects: {e}")
        return f"Error retrieving projects: {str(e)}"

@mcp.tool()
async def get_project(project_id: str) -> str:
    """
    Get details about a specific project.
    """
    if not db:
        if not initialize_client() or not db:
            return "Failed to initialize DB."

    try:
        db.sync()
        project = db.get_project(project_id)
        if not project:
            return f"Project {project_id} not found."

        return format_project(project)
    except Exception as e:
        return f"Error retrieving project: {str(e)}"

@mcp.tool()
async def get_project_tasks(project_id: str) -> str:
    """
    Get all tasks in a specific project.
    """
    if not db:
        if not initialize_client() or not db:
            return "Failed to initialize DB."

    try:
        db.sync()
        tasks = db.get_project_tasks(project_id)
        
        project = db.get_project(project_id)
        p_name = project.get("name") if project else project_id
        
        if not tasks:
            return f"No tasks found in project '{p_name}'."

        result = f"Found {len(tasks)} tasks in project '{p_name}':\n\n"
        for task in tasks:
            result += "---\n" + format_task(task) + "\n"

        return result
    except Exception as e:
        logger.error(f"Error in get_project_tasks: {e}")
        return f"Error retrieving project tasks: {str(e)}"


@mcp.tool()
async def get_task(task_id: str) -> str:
    """
    Get details about a specific task.

    Args:
        task_id: ID of the task
    """
    if not db:
        if not initialize_client() or not db:
            return "Failed to initialize DB."

    try:
        db.sync()
        task = db.get_task(task_id)
        if not task:
            return f"Task {task_id} not found."

        return format_task(task)
    except Exception as e:
        logger.error(f"Error in get_task: {e}")
        return f"Error retrieving task: {str(e)}"

@mcp.tool()
async def search_tasks(query: str) -> str:
    """
    Search tasks by their title using a local database cache.

    Args:
        query: Substring of the title to search for
    """
    if not db:
        if not initialize_client() or not db:
            return "Failed to initialize DB."

    try:
        db.sync()
        tasks = db.find_tasks_by_title(query)
        if not tasks:
            return f"No tasks found matching '{query}'."

        result = f"Found {len(tasks)} tasks matching '{query}':\n\n"
        for task in tasks:
            result += "---\n" + format_task(task) + "\n"
        return result
    except Exception as e:
        logger.error(f"Error searching tasks: {e}")
        return f"Error searching tasks: {str(e)}"


@mcp.tool()
async def create_task(
    title: str,
    project_id: str,
    content: str = None,
    start_date: str = None,
    due_date: str = None,
    priority: int = 0,
    tags: str = None,  # New parameter for tags
) -> str:
    """
    Create a new task in TickTick.

    Args:
        title: Task title
        project_id: ID of the project to add the task to
        content: Task description/content (optional)
        start_date: Start date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        due_date: Due date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        priority: Priority level (0: None, 1: Low, 3: Medium, 5: High) (optional)
        tags: Comma-separated list of tags (optional)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate priority
    if priority not in [0, 1, 3, 5]:
        return "Invalid priority. Must be 0 (None), 1 (Low), 3 (Medium), or 5 (High)."

    try:
        # Process tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]

        # Validate dates if provided
        for date_str, date_name in [(start_date, "start_date"), (due_date, "due_date")]:
            if date_str:
                try:
                    datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    return f"Invalid {date_name} format. Use ISO format: YYYY-MM-DDThh:mm:ss+0000"

        task = ticktick.create_task(
            title=title,
            project_id=project_id,
            content=content,
            start_date=start_date,
            due_date=due_date,
            priority=priority,
            tags=tag_list,
        )

        if "error" in task:
            return f"Error creating task: {task['error']}"

        return f"Task created successfully:\n\n" + format_task(task)
    except Exception as e:
        logger.error(f"Error in create_task: {e}")
        return f"Error creating task: {str(e)}"


@mcp.tool()
async def update_task(
    task_id: str,
    project_id: str,
    title: str = None,
    content: str = None,
    start_date: str = None,
    due_date: str = None,
    priority: int = None,
    tags: str = None,  # New parameter for tags
) -> str:
    """
    Update an existing task in TickTick.

    Args:
        task_id: ID of the task to update
        project_id: ID of the project the task belongs to
        title: New task title (optional)
        content: New task description/content (optional)
        start_date: New start date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        due_date: New due date in ISO format YYYY-MM-DDThh:mm:ss+0000 (optional)
        priority: New priority level (0: None, 1: Low, 3: Medium, 5: High) (optional)
        tags: Comma-separated list of tags (optional)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate priority if provided
    if priority is not None and priority not in [0, 1, 3, 5]:
        return "Invalid priority. Must be 0 (None), 1 (Low), 3: Medium, 5: High)."

    try:
        # Process tags if provided
        tag_list = None
        if tags is not None:  # Allow empty string to clear tags
            tag_list = [tag.strip() for tag in tags.split(",")] if tags else []

        # Validate dates if provided
        for date_str, date_name in [(start_date, "start_date"), (due_date, "due_date")]:
            if date_str:
                try:
                    datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    return f"Invalid {date_name} format. Use ISO format: YYYY-MM-DDThh:mm:ss+0000"

        task = ticktick.update_task(
            task_id=task_id,
            project_id=project_id,
            title=title,
            content=content,
            start_date=start_date,
            due_date=due_date,
            priority=priority,
            tags=tag_list,
        )

        if "error" in task:
            return f"Error updating task: {task['error']}"

        return f"Task updated successfully:\n\n" + format_task(task)
    except Exception as e:
        logger.error(f"Error in update_task: {e}")
        return f"Error updating task: {str(e)}"


@mcp.tool()
async def complete_task(project_id: str, task_id: str) -> str:
    """
    Mark a task as complete.

    Args:
        project_id: ID of the project
        task_id: ID of the task
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    try:
        result = ticktick.complete_task(project_id, task_id)
        if "error" in result:
            return f"Error completing task: {result['error']}"

        return f"Task {task_id} marked as complete."
    except Exception as e:
        logger.error(f"Error in complete_task: {e}")
        return f"Error completing task: {str(e)}"


@mcp.tool()
async def delete_task(project_id: str, task_id: str) -> str:
    """
    Delete a task.

    Args:
        project_id: ID of the project
        task_id: ID of the task
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    try:
        result = ticktick.delete_task(project_id, task_id)
        if "error" in result:
            return f"Error deleting task: {result['error']}"

        return f"Task {task_id} deleted successfully."
    except Exception as e:
        logger.error(f"Error in delete_task: {e}")
        return f"Error deleting task: {str(e)}"


@mcp.tool()
async def create_project(
    name: str, color: str = "#F18181", view_mode: str = "list"
) -> str:
    """
    Create a new project in TickTick.

    Args:
        name: Project name
        color: Color code (hex format) (optional)
        view_mode: View mode - one of list, kanban, or timeline (optional)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate view_mode
    if view_mode not in ["list", "kanban", "timeline"]:
        return "Invalid view_mode. Must be one of: list, kanban, timeline."

    try:
        project = ticktick.create_project(name=name, color=color, view_mode=view_mode)

        if "error" in project:
            return f"Error creating project: {project['error']}"

        return f"Project created successfully:\n\n" + format_project(project)
    except Exception as e:
        logger.error(f"Error in create_project: {e}")
        return f"Error creating project: {str(e)}"


@mcp.tool()
async def delete_project(project_id: str) -> str:
    """
    Delete a project.

    Args:
        project_id: ID of the project
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    try:
        result = ticktick.delete_project(project_id)
        if "error" in result:
            return f"Error deleting project: {result['error']}"

        return f"Project {project_id} deleted successfully."
    except Exception as e:
        logger.error(f"Error in delete_project: {e}")
        return f"Error deleting project: {str(e)}"


def main():
    """Main entry point for the MCP server."""
    # Initialize the TickTick client
    if not initialize_client():
        logger.error(
            "Failed to initialize TickTick client. Please check your API credentials."
        )
        return

    # Run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
