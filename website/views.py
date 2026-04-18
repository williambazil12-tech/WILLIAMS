from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Result, User
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # If the user is a visitor, they should see William's Dashboard
    if current_user.user_type == 'visitor':
        # We look for the first 'student' in the database (William)
        william = User.query.filter_by(user_type='student').first()
        return render_template("home.html", user=william)
    
    return render_template("home.html", user=current_user)

@views.route('/student-profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Determine whose data to show
    if current_user.user_type == 'visitor':
        # Fetch the student whose progress is being tracked
        display_user = User.query.filter_by(user_type='student').first()
    else:
        display_user = current_user

    if request.method == 'POST':
        # Security: Block visitors from submitting the form
        if current_user.user_type == 'visitor':
            flash('Visitors are in Read-Only mode.', category='error')
            return redirect(url_for('views.profile'))

        # Create the new record for the logged-in student
        new_record = Result(
            subject_name=request.form.get('subject'),
            ca_score=request.form.get('ca'),
            final_score=request.form.get('exam'),
            semester=int(request.form.get('semester') or 1),
            year_of_study=int(request.form.get('year') or 1),
            semester_gpa=request.form.get('gpa'),
            assignment_notes=request.form.get('notes'),
            daily_score=request.form.get('daily_score'),
            user_id=current_user.id
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Academic record synchronized successfully!', category='success')
        return redirect(url_for('views.profile'))

    # CRITICAL: We pass display_user as 'user'. 
    # student_profile.html loops through user.results
    return render_template("student_profile.html", user=display_user)

@views.route('/visitor-view/<int:id>')
@login_required
def visitor_view(id): 
    # This allows viewing a specific student by their ID
    student = User.query.get_or_404(id)
    return render_template("student_profile.html", user=student)