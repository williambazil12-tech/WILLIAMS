from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Change nullable=True so you can save a GPA without a subject name
    subject_name = db.Column(db.String(150), nullable=True) 
    ca_score = db.Column(db.String(20)) 
    final_score = db.Column(db.String(20)) 
    credits = db.Column(db.Integer) 
    semester = db.Column(db.Integer) 
    year_of_study = db.Column(db.Integer) 
    semester_gpa = db.Column(db.String(10)) 
    assignment_notes = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    daily_score = db.Column(db.String(20))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    # New Fields
    reg_number = db.Column(db.String(50), unique=True, nullable=True) # For Students
    user_type = db.Column(db.String(20)) # 'student' or 'visitor'
    
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    results = db.relationship('Result', backref='user', lazy=True)