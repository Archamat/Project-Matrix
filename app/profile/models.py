from app.extensions import db
from datetime import datetime, timezone

class Demo(db.Model):
    __tablename__ = "demos"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True, nullable=False)
    key = db.Column(db.String(512), nullable=False)   # S3 object key
    title = db.Column(db.String(200))
    mime = db.Column(db.String(120))
    duration_seconds = db.Column(db.Integer)
    visibility = db.Column(db.String(16), default="private")
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    user = db.relationship("User", back_populates="demos")