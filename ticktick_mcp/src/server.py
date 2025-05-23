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

        env_path = Path(".env")
        if not env_path.exists():
            logger.error(
                "No .env file found. Please run 'uv run -m ticktick_mcp.cli auth' to set up authentication."
            )
            return False

        # Check if we have valid credentials
        with open(env_path, "r") as f:
            content = f.read()
            if "TICKTICK_ACCESS_TOKEN" not in content:
                logger.error(
                    "No access token found in .env file. Please run 'uv run -m ticktick_mcp.cli auth' to authenticate."
                )
                return False

        # Initialize the client
        ticktick = TickTickClient()
        logger.info("TickTick client initialized successfully")

        # Test API connectivity with a lightweight call
        # We'll use the /project endpoint with a non-existent ID to test auth
        # This will return 404 if auth is valid, or 401 if token is invalid
        test_response = ticktick._make_request("GET", "/project/test_connection")
        if isinstance(test_response, dict) and test_response.get(
            "error", ""
        ).startswith("401"):
            logger.error(
                "Failed to access TickTick API: Invalid or expired access token"
            )
            logger.error(
                "Your access token may have expired. Please run 'uv run -m ticktick_mcp.cli auth' to refresh it."
            )
            return False

        logger.info("Successfully connected to TickTick API")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize TickTick client: {e}")
        return False


# Format a task object from TickTick for better display
def format_task(task: Dict) -> str:
    """Format a task into a human-readable string."""
    # Debug logging
    logger.info(f"Formatting task with ID: {task.get('id')}")
    logger.info(f"Full task object: {json.dumps(task, indent=2)}")

    # Start with ID and title as they're most important
    formatted = f"ID: {task.get('id', 'No ID')}\n"
    formatted += f"Title: {task.get('title', 'No title')}\n"
    formatted += f"Project ID: {task.get('projectId', 'None')}\n"

    # Add dates if available
    if task.get("startDate"):
        formatted += f"Start Date: {task.get('startDate')}\n"
    if task.get("dueDate"):
        formatted += f"Due Date: {task.get('dueDate')}\n"

    # Add priority if available
    priority_map = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    priority = task.get("priority", 0)
    formatted += f"Priority: {priority_map.get(priority, str(priority))}\n"

    # Add tags if available
    tags = task.get("tags", [])
    if tags:
        formatted += f"Tags: {', '.join(tags)}\n"

    # Add status if available
    status = "Completed" if task.get("status") == 2 else "Active"
    formatted += f"Status: {status}\n"

    # Add content if available
    if task.get("content"):
        formatted += f"\nContent:\n{task.get('content')}\n"

    # Add subtasks if available
    items = task.get("items", [])
    if items:
        formatted += f"\nSubtasks ({len(items)}):\n"
        for item in items:
            status = "✓" if item.get("status") == 1 else "□"
            formatted += f"[{status}] {item.get('title', 'No title')} (ID: {item.get('id', 'No ID')})\n"

    return formatted


# Format a project object from TickTick for better display
def format_project(project: Dict) -> str:
    """Format a project into a human-readable string."""
    formatted = f"Name: {project.get('name', 'No name')}\n"
    formatted += f"ID: {project.get('id', 'No ID')}\n"

    # Add color if available
    if project.get("color"):
        formatted += f"Color: {project.get('color')}\n"

    # Add view mode if available
    if project.get("viewMode"):
        formatted += f"View Mode: {project.get('viewMode')}\n"

    # Add closed status if available
    if "closed" in project:
        formatted += f"Closed: {'Yes' if project.get('closed') else 'No'}\n"

    # Add kind if available
    if project.get("kind"):
        formatted += f"Kind: {project.get('kind')}\n"

    return formatted


# MCP Tools


@mcp.tool()
async def get_projects() -> str:
    """Get all projects from TickTick."""
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    try:
        projects = ticktick.get_projects()
        if "error" in projects:
            return f"Error fetching projects: {projects['error']}"

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

    Args:
        project_id: ID of the project
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    try:
        project = ticktick.get_project(project_id)
        if "error" in project:
            return f"Error fetching project: {project['error']}"

        return format_project(project)
    except Exception as e:
        logger.error(f"Error in get_project: {e}")
        return f"Error retrieving project: {str(e)}"


@mcp.tool()
async def get_project_tasks(project_id: str) -> str:
    """
    Get all tasks in a specific project.

    Args:
        project_id: ID of the project
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    try:
        project_data = ticktick.get_project_with_data(project_id)
        if "error" in project_data:
            return f"Error fetching project data: {project_data['error']}"

        tasks = project_data.get("tasks", [])
        if not tasks:
            return f"No tasks found in project '{project_data.get('project', {}).get('name', project_id)}'."

        # Debug logging
        logger.info(f"Project data structure: {json.dumps(project_data, indent=2)}")
        for task in tasks:
            logger.info(f"Task ID: {task.get('id')}")
            logger.info(f"Full task data: {json.dumps(task, indent=2)}")

        result = f"Found {len(tasks)} tasks in project '{project_data.get('project', {}).get('name', project_id)}':\n\n"
        for task in tasks:
            result += "---\n" + format_task(task) + "\n"

        return result
    except Exception as e:
        logger.error(f"Error in get_project_tasks: {e}")
        return f"Error retrieving project tasks: {str(e)}"


@mcp.tool()
async def get_task(project_id: str, task_id: str) -> str:
    """
    Get details about a specific task.

    Args:
        project_id: ID of the project
        task_id: ID of the task
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    try:
        task = ticktick.get_task(project_id, task_id)
        if "error" in task:
            return f"Error fetching task: {task['error']}"

        return format_task(task)
    except Exception as e:
        logger.error(f"Error in get_task: {e}")
        return f"Error retrieving task: {str(e)}"


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
