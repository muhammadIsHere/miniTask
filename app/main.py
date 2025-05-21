import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime

# Create Flask application
app = Flask(__name__)

# Configure database path - handle both local and container environments
db_path = os.environ.get('DB_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
os.makedirs(db_path, exist_ok=True)  # Ensure the directory exists
db_file = os.path.join(db_path, 'minitasks.db')

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

# API Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks or filter by completion status"""
    completed = request.args.get('completed')
    
    try:
        if completed is not None:
            completed = completed.lower() == 'true'
            tasks = Task.query.filter_by(completed=completed).all()
        else:
            tasks = Task.query.all()
            
        return jsonify({
            'status': 'success',
            'tasks': [task.to_dict() for task in tasks]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a single task by ID"""
    try:
        task = Task.query.get(task_id)
        if task is None:
            return jsonify({
                'status': 'error',
                'message': f'Task with ID {task_id} not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'task': task.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Title is required'
        }), 400
        
    try:
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
        
    try:
        task = Task.query.get(task_id)
        if task is None:
            return jsonify({
                'status': 'error',
                'message': f'Task with ID {task_id} not found'
            }), 404
            
        # Update fields if they exist in the request
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'completed' in data:
            task.completed = data['completed']
            
        task.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.query.get(task_id)
        if task is None:
            return jsonify({
                'status': 'error',
                'message': f'Task with ID {task_id} not found'
            }), 404
            
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Task with ID {task_id} deleted successfully'
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is running'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 