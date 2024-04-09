from apps.app import db
from datetime import datetime
from flask_login import current_user

class Notice(db.Model):
    __tablename__ = "notices"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    user = db.relationship('User', backref=db.backref('notices', lazy=True))
    author = db.Column(db.String(100), nullable=False)


    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author
        self.user_id = current_user.id  
