from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from app import db

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Snippet model with vector search support
class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.JSON, nullable=False)
    embedding = db.Column(Vector(1536), nullable=False) 
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('snippets', lazy=True))


class SnippetSession(db.Model):
    __tablename__ = "snippet_session"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    responses = db.Column(MutableList.as_mutable(db.JSON), nullable=False, default=[])
    question_count = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SnippetSession user_id={self.user_id} active={self.active}>"


class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diary_content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('diary_entries', lazy=True))