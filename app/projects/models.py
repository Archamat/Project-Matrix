from app.extensions import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sector = db.Column(db.String(50), nullable=False)  # e.g., 'Web', 'AI', etc.
    people_count = db.Column(db.Integer, nullable=False)
    skills = db.Column(db.Text)  # Store skills as a comma-separated string
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    creator = db.relationship('User', backref=db.backref('projects', lazy=True))



    def __init__(self, name, description, sector, people_count, skills,creator):
        self.name = name
        self.description = description
        self.sector = sector
        self.people_count = people_count
        self.skills = skills
        self.creator = creator

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    information = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    contact_info = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('applications', lazy=True))
    applicant = db.relationship('User', backref=db.backref('applications', lazy=True))
    
    def __init__(self, project_id, applicant_id, information, skills, contact_info):
        self.project_id = project_id
        self.applicant_id = applicant_id
        self.information = information
        self.skills = skills
        self.contact_info = contact_info
