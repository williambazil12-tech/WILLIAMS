from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password = request.form.get('password')
        reg_no = request.form.get('reg_number')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Email already exists. Please login instead.', category='error')
            return redirect(url_for('auth.sign_up'))
        
        if  len(first_name) < 4:
            flash('Name must be at least 4 characters long.', category='error')
            return redirect(url_for('auth.sign_up'))
        
        if len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
            return redirect(url_for('auth.sign_up'))

        # 6. PASSWORD MATCH CHECK (If you have a password_confirm field)
        password_confirm = request.form.get('password_confirm')
        if password != password_confirm:
            flash('Passwords do not match.', category='error')
            return redirect(url_for('auth.sign_up'))

        user_by_name = User.query.filter_by(first_name=first_name).first()
        if user_by_name:
            flash('This name is already taken. Please add a second name.', category='error')
            return redirect(url_for('auth.sign_up'))

      # ... (other checks for name, email, etc.) ...

        # ONLY apply these checks if the user is registering as a student
        if user_type == 'student':
            # 1. Check for the "MUST" suffix
            if not reg_no.lower().endswith('must'):
                flash('Invalid registration format. Student IDs must end with "MUST".', category='error')
                return redirect(url_for('auth.sign_up'))

            # 2. Check for minimum length (18 characters)
            if len(reg_no) < 18:
                flash('Student registration number is too short.', category='error')
                return redirect(url_for('auth.sign_up'))

            # 3. Check if the Registration Number is already taken
            user_by_reg_no = User.query.filter_by(reg_number=reg_no).first()
            if user_by_reg_no:
                flash('This registration number is already in our system.', category='error')
                return redirect(url_for('auth.sign_up'))
        
        else:
            # Logic for Visitors: They don't need a MUST ID.
            # You can leave the reg_number blank or set it to 'N/A'
            reg_no = f"VISITOR-{email}" 

        # Now proceed to create the user
        new_user = User(
            email=email,
            first_name=first_name,
            reg_number=reg_no, # This will be the MUST ID for students or the Visitor ID
            user_type=user_type,
            password=generate_password_hash(password)
        )

        # Determine user type and save
        if user_type == 'student':
            new_user = User(email=email, first_name=first_name, user_type='student',
                            reg_number=reg_no.upper(), password=hashed_password)
        else:
            new_user = User(email=email, first_name=first_name, user_type='visitor',
                            reg_number=None, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Access Granted!', category='success')
            # Both types go to views.home; views.py will handle the split
            return redirect(url_for('views.home'))
        else:
            flash("We couldn't find an account  with that email. Please check your spelling or sign up.", category='error')

    return render_template("login.html", user=current_user)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))