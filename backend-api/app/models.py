from datetime import datetime
from app import db

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# DiaryEntry model to store diary entries and embeddings
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.PickleType, nullable=False)  # Store the embeddings
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('diary_entries', lazy=True))
