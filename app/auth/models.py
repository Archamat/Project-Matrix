from ..extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.aws.s3 import presigned_get_url


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    contact_info = db.Column(db.String(256), nullable=True)
    avatar_url = db.Column(db.String(256), nullable=True)
    demos = db.relationship(
        "Demo",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="desc(Demo.updated_at)",
    )
    skills = db.relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def avatar_presigned(self):
        if not self.avatar_url:
            return None
        return presigned_get_url(self.avatar_url, 3600)

    bio = db.Column(db.Text, nullable=True)

    # Method to hash the password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Method to check the hashed password
    def check_password(self, password):
        return check_password_hash(self.password, password)
