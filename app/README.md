# MiniTasks Flask API

This directory contains a RESTful Flask API for managing to-do tasks.

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

## API Endpoints

- `GET /api/tasks` - Get all tasks (with optional filtering)
- `GET /api/tasks/<id>` - Get a specific task
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task
- `GET /api/tasks/status/<status>` - Filter tasks by status
- `GET /api/tasks/priority/<priority>` - Filter tasks by priority
- `GET /api/health` - Health check endpoint

## Task Model

Tasks have the following properties:
- `id`: Unique identifier (auto-generated)
- `title`: Task title (required)
- `description`: Task description
- `status`: Task status (pending, in-progress, completed)
- `priority`: Task priority (1-5, where 5 is highest)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Database

SQLite database will be automatically created at `../data/minitasks.db` (relative to this directory)
or can be specified using the `DB_PATH` environment variable. 