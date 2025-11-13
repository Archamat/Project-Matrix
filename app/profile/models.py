from app.extensions import db
from datetime import datetime, timezone


class Demo(db.Model):
    __tablename__ = "demos"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), 
                        index=True, nullable=False)
    key = db.Column(db.String(512), nullable=False)   
    title = db.Column(db.String(200))
    mime = db.Column(db.String(120))
    duration_seconds = db.Column(db.Integer)
    visibility = db.Column(db.String(16), default="private")
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc),
                           nullable=False)
    
    user = db.relationship("User", back_populates="demos")

    def to_dict(self, include_url=False, presigned_url=None):
        """
        Serialize demo to dictionary.
        
        Args:
            include_url: Whether to include presigned URL
            presigned_url: The presigned S3 URL (if available)
        
        Returns:
            dict: Demo data ready for JSON serialization
        """
        data = {
            "id": self.id,
            "title": self.title or "Untitled",  # ← Default value in ONE place
            "mime": self.mime,
            "visibility": self.visibility or "Private",
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Optionally include URL (for API responses)
        if include_url and presigned_url:
            data["url"] = presigned_url
        
        return data


class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    user_skills = db.relationship("UserSkill", back_populates="skill")


class UserSkill(db.Model):
    __tablename__ = "user_skills"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index = True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False, index = True)
    level = db.Column(db.String(50))  # e.g., Beginner, Intermediate, Expert
    years = db.Column(db.Integer)  # Years of experience
    user = db.relationship("User", back_populates="skills")
    skill = db.relationship("Skill", back_populates="user_skills")
    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='uq_user_skill'),)
