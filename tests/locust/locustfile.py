import random
import json
from locust import HttpUser, task, between, tag
from datetime import datetime, timedelta

class CreateTaskUser(HttpUser):
    weight = 30
    wait_time = between(1, 5)
    
    @tag('write')
    @task
    def create_task(self):
        # Generate random due date between tomorrow and 30 days from now
        days_ahead = random.randint(1, 30)
        future_date = datetime.now() + timedelta(days=days_ahead)
        due_date = future_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Create random task data
        task_data = {
            "title": f"Locust Test Task {random.randint(1000, 9999)}",
            "description": f"Task created during load testing - {datetime.now().isoformat()}",
            "status": random.choice(["pending", "in-progress", "completed"]),
            "priority": random.randint(1, 5),
            "due_date": due_date
        }
        
        # Send POST request
        self.client.post("/api/tasks", json=task_data)


class GetAllTasksUser(HttpUser):
    weight = 40  # More common operation
    wait_time = between(1, 3)
    
    @tag('read')
    @task
    def get_all_tasks(self):
        # Randomly apply filters sometimes
        if random.random() < 0.3:  # 30% chance to use filter
            status = random.choice(["pending", "in-progress", "completed"])
            self.client.get(f"/api/tasks?status={status}")
        else:
            self.client.get("/api/tasks")


class GetSingleTaskUser(HttpUser):
    weight = 15
    wait_time = between(1, 3)
    
    @tag('read')
    @task
    def get_single_task(self):
        # Get a random task ID between 1 and 100
        # In a real scenario, you might want to get actual IDs from the API first
        task_id = random.randint(1, 100)
        self.client.get(f"/api/tasks/{task_id}")


class UpdateTaskUser(HttpUser):
    weight = 10
    wait_time = between(2, 6)
    
    @tag('write')
    @task
    def update_task(self):
        # Update a random task
        task_id = random.randint(1, 100)
        
        # Create update data - only updating status and priority
        update_data = {
            "status": random.choice(["pending", "in-progress", "completed"]),
            "priority": random.randint(1, 5)
        }
        
        # Send PUT request
        self.client.put(f"/api/tasks/{task_id}", json=update_data)


class DeleteTaskUser(HttpUser):
    weight = 5  # Least common operation
    wait_time = between(5, 10)
    
    @tag('write')
    @task
    def delete_task(self):
        # Delete a random task
        task_id = random.randint(1, 100)
        self.client.delete(f"/api/tasks/{task_id}") 