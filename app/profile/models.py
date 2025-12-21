from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    user_skills = db.relationship("UserSkill", back_populates="skill")


class UserSkill(db.Model):
    __tablename__ = "user_skills"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    skill_id = db.Column(
        db.Integer, db.ForeignKey("skills.id"), nullable=False, index=True
    )
    level = db.Column(db.String(50))  # e.g., Beginner, Intermediate, Expert
    years = db.Column(db.Integer)  # Years of experience
    user = db.relationship("User", back_populates="skills")
    skill = db.relationship("Skill", back_populates="user_skills")
    __table_args__ = (db.UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)
