from app.extensions import db

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
