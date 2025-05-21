import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from google.cloud import pubsub_v1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get database path - use /app/data/minitasks.db in container
# or a local path for development
db_path = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), '..', 'data', 'minitasks.db'))
os.makedirs(os.path.dirname(db_path), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Pub/Sub client
project_id = os.getenv('GCP_PROJECT')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, 'task-reminders')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, in-progress, completed
    priority = db.Column(db.Integer, default=1)  # 1 (low) to 5 (high)
    due_date = db.Column(db.Date, nullable=True)  # New field for due date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        task_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if self.due_date:
            task_dict['due_date'] = self.due_date.isoformat()
            
        return task_dict

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    logger.info(f"Database initialized at {db_path}")

def publish_reminder(task):
    """Publish reminder message to Pub/Sub if task has a due date"""
    if task.due_date:
        message_data = {
            'task_id': task.id,
            'description': task.description,
            'due_date': task.due_date.isoformat() if task.due_date else None
        }
        
        # Convert message to JSON string and then to bytes
        message_json = json.dumps(message_data)
        message_bytes = message_json.encode('utf-8')
        
        try:
            # Publish message
            future = publisher.publish(topic_path, data=message_bytes)
            message_id = future.result()
            logger.info(f"Published reminder for task {task.id}, message ID: {message_id}")
        except Exception as e:
            logger.error(f"Error publishing reminder: {e}")

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = Task.query
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=int(priority))
        
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 1)
    )
    
    # Add due_date if provided
    if 'due_date' in data and data['due_date']:
        try:
            new_task.due_date = datetime.fromisoformat(data['due_date']).date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
    
    db.session.add(new_task)
    db.session.commit()
    
    # Publish reminder if task has due date
    if new_task.due_date:
        publish_reminder(new_task)
    
    return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    
    # Update due_date if provided
    due_date_updated = False
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.fromisoformat(data['due_date']).date()
                due_date_updated = True
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
        else:
            task.due_date = None
    
    db.session.commit()
    
    # Publish reminder if due date was updated and task has a due date
    if due_date_updated and task.due_date:
        publish_reminder(task)
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task {task_id} deleted successfully'}), 200

@app.route('/api/tasks/status/<status>', methods=['GET'])
def get_tasks_by_status(status):
    """Get tasks filtered by status"""
    tasks = Task.query.filter_by(status=status).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks/priority/<int:priority>', methods=['GET'])
def get_tasks_by_priority(priority):
    """Get tasks filtered by priority"""
    tasks = Task.query.filter_by(priority=priority).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000))) 