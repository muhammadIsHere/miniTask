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

# Initialize Pub/Sub publisher
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
publisher = pubsub_v1.PublisherClient()
topic_name = f'projects/{project_id}/topics/task-reminders'

def publish_reminder(task_id, due_date, description):
    """Publish a task reminder to Pub/Sub"""
    if not due_date:
        return
    
    try:
        message_data = json.dumps({
            'task_id': task_id,
            'due_date': due_date.isoformat() if isinstance(due_date, datetime) else due_date,
            'description': description
        }).encode('utf-8')
        
        future = publisher.publish(topic_name, message_data)
        message_id = future.result()
        logger.info(f"Published reminder for task {task_id} with message ID: {message_id}")
    except Exception as e:
        logger.error(f"Error publishing reminder: {e}")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, in-progress, completed
    priority = db.Column(db.Integer, default=1)  # 1 (low) to 5 (high)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    logger.info(f"Database initialized at {db_path}")

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
    
    # Process due_date if provided
    due_date = None
    if 'due_date' in data and data['due_date']:
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 1),
        due_date=due_date
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    # Publish reminder if due_date is set
    if due_date:
        publish_reminder(new_task.id, due_date, new_task.description)
    
    return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    due_date_changed = False
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        if data['due_date']:
            try:
                new_due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                due_date_changed = task.due_date != new_due_date
                task.due_date = new_due_date
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        else:
            due_date_changed = task.due_date is not None
            task.due_date = None
    
    db.session.commit()
    
    # Publish reminder if due_date was changed and is set
    if due_date_changed and task.due_date:
        publish_reminder(task.id, task.due_date, task.description)
    
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