from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import secrets

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    api_keys = db.relationship('ApiKey', backref='user', lazy=True, cascade='all, delete-orphan')


class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    mode = db.Column(db.Integer, default=0)  # 0 for RAG mode, 1 for LLM-only mode
    title = db.Column(db.String(255), nullable=True) 
    messages = db.relationship('Messages', backref='chat', lazy=True, cascade='all, delete-orphan')
    
class Messages(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    sender = db.Column(db.Integer, nullable=False)  # 0 for 'user' or 1 for 'bot'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def generate_key():
        return secrets.token_urlsafe(32)