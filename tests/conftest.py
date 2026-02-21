# project.py
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    applications = db.relationship('Application', backref='project', lazy='dynamic')
    tasks = db.relationship('Task', backref='project', lazy='dynamic')
    messages = db.relationship('Message', backref='project', lazy='dynamic')
    links = db.relationship('Link', backref='project', lazy='dynamic')
    notes = db.relationship('Note', backref='project', lazy='dynamic')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    projects = Project.query.filter_by(creator_id=current_user.id).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in projects])

@app.route('/api/project/<int:id>', methods=['GET'])
@login_required
def get_project(id):
    project = Project.query.get_or_404(id)
    if project.creator_id != current_user.id:
        abort(403)
    return jsonify({'id': project.id, 'name': project.name, 'description': project.description})

@app.route('/api/create_project', methods=['POST'])
@login_required
def create_project():
    data = request.get_json()
    name = data['name']
    description = data.get('description', '')
    if len(name) < 3:
        abort(400)
    project = Project(name=name, description=description, creator_id=current_user.id)
    db.session.add(project)
    db.session.commit()
    return jsonify({'id': project.id, 'name': project.name}), 201

@app.route('/api/apply/<int:project_id>', methods=['POST'])
@login_required
def apply_project(project_id):
    project = Project.query.get_or_404(project_id)
    application = Application(user_id=current_user.id, project_id=project.id)
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Application submitted'})

@app.route('/api/project/<int:id>/applicants', methods=['GET'])
@login_required
def get_project_applicants(id):
    project = Project.query.get_or_404(id)
    if project.creator_id != current_user.id:
        abort(403)
    applicants = Application.query.filter_by(project_id=id).all()
    return jsonify([{'id': a.user_id, 'username': a.user.username} for a in applicants])

if __name__ == '__main__':
    app.run(debug=True)