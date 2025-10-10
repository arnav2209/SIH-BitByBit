from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Database configuration - Use PostgreSQL in production, SQLite locally
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Fix for Heroku/Render PostgreSQL URL format
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development with SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Association table for many-to-many relationship between subjects and faculty
subject_faculty = db.Table('subject_faculty',
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True),
    db.Column('faculty_id', db.Integer, db.ForeignKey('faculty.id'), primary_key=True)
)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='admin')  # admin, student
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=True)  # For students
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with batch for students
    batch = db.relationship('Batch', backref='students')

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), default='regular')  # regular, lab, auditorium
    is_available = db.Column(db.Boolean, default=True)

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    department = db.Column(db.String(50))
    max_hours_per_day = db.Column(db.Integer, default=6)
    avg_leaves_per_month = db.Column(db.Integer, default=2)
    
    # Many-to-many relationship with subjects (defined in Subject model)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    hours_per_week = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), default='theory')  # theory, practical, tutorial
    
    # Many-to-many relationship with faculty
    faculty = db.relationship('Faculty', secondary=subject_faculty, backref='subjects')

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    strength = db.Column(db.Integer, nullable=False)

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    time_slot = db.Column(db.String(20), nullable=False)  # 09:00-10:00
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring services"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Redirect students to their dashboard
    if session.get('user_role') == 'student':
        return redirect(url_for('student_dashboard'))
    
    # Get statistics for admin dashboard
    stats = {
        'classrooms': Classroom.query.count(),
        'faculty': Faculty.query.count(),
        'subjects': Subject.query.count(),
        'batches': Batch.query.count()
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session['batch_id'] = user.batch_id if user.role == 'student' else None
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
    
    batch_id = session.get('batch_id')
    if not batch_id:
        flash('No batch assigned to your account. Please contact administrator.', 'error')
        return redirect(url_for('logout'))
    
    batch = Batch.query.get(batch_id)
    if not batch:
        flash('Batch not found. Please contact administrator.', 'error')
        return redirect(url_for('logout'))
    
    # Get timetable for the student's batch
    timetable_entries = db.session.query(Timetable, Subject, Faculty, Classroom).join(
        Subject, Timetable.subject_id == Subject.id
    ).join(
        Faculty, Timetable.faculty_id == Faculty.id
    ).join(
        Classroom, Timetable.classroom_id == Classroom.id
    ).filter(Timetable.batch_id == batch_id).all()
    
    # Organize timetable by day and time
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = ['09:15-10:15', '10:15-11:15', '11:15-12:15', '12:15-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00']
    
    # Include all possible time slots including 2-hour lab slots
    all_time_slots = time_slots + ['09:15-11:15', '10:15-12:15', '01:00-03:00', '02:00-04:00']
    
    timetable = {}
    for day in days:
        timetable[day] = {}
        for time_slot in all_time_slots:
            timetable[day][time_slot] = None
    
    for entry, subject, faculty, classroom in timetable_entries:
        timetable[entry.day_of_week][entry.time_slot] = {
            'subject': subject.name,
            'faculty': faculty.name,
            'classroom': classroom.name,
            'type': subject.type
        }
    
    # Calculate statistics (count actual hours - lab sessions are 2 hours)
    total_hours = 0
    theory_count = 0
    practical_count = 0
    tutorial_count = 0
    
    for entry, subject, _, _ in timetable_entries:
        if subject.type == 'theory':
            theory_count += 1
            total_hours += 1  # Theory classes are 1 hour
        elif subject.type == 'practical':
            practical_count += 1
            # Check if it's a 2-hour lab session
            if entry.time_slot in ['09:15-11:15', '10:15-12:15', '01:00-03:00', '02:00-04:00']:
                total_hours += 2  # Lab sessions are 2 hours
            else:
                total_hours += 1  # Regular practical is 1 hour
        elif subject.type == 'tutorial':
            tutorial_count += 1
            total_hours += 1  # Tutorial classes are 1 hour
    
    return render_template('student_dashboard.html', 
                          batch=batch, 
                          timetable=timetable, 
                          days=days, 
                          time_slots=time_slots,
                          total_hours=total_hours,
                          theory_count=theory_count,
                          practical_count=practical_count,
                          tutorial_count=tutorial_count)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/setup')
def setup():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    return render_template('setup.html')

@app.route('/manage/<string:entity>')
def manage_entity(entity):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    data = {}
    if entity == 'classrooms':
        data['items'] = Classroom.query.all()
    elif entity == 'faculty':
        data['items'] = Faculty.query.all()
    elif entity == 'subjects':
        data['items'] = Subject.query.all()
        data['faculty'] = Faculty.query.all()
    elif entity == 'batches':
        data['items'] = Batch.query.all()
    elif entity == 'students':
        # Add student management for admin
        data['items'] = User.query.filter_by(role='student').all()
        data['batches'] = Batch.query.all()
    
    # Ensure data has items key
    if 'items' not in data:
        data['items'] = []
    
    return render_template('manage.html', entity=entity, data=data)

@app.route('/add/<string:entity>', methods=['POST'])
def add_entity(entity):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    try:
        if entity == 'classroom':
            classroom = Classroom(
                name=request.form['name'],
                capacity=int(request.form['capacity']),
                type=request.form.get('type', 'regular')
            )
            db.session.add(classroom)
        
        elif entity == 'faculty':
            email = request.form.get('email', '').strip()
            faculty = Faculty(
                name=request.form['name'],
                email=email if email else None,  # Set to None if empty to avoid unique constraint issues
                department=request.form['department'],
                max_hours_per_day=int(request.form.get('max_hours_per_day', 6)),
                avg_leaves_per_month=int(request.form.get('avg_leaves_per_month', 2))
            )
            db.session.add(faculty)
        
        elif entity == 'subject':
            subject = Subject(
                name=request.form['name'],
                code=request.form['code'],
                semester=int(request.form['semester']),
                department=request.form['department'],
                hours_per_week=int(request.form['hours_per_week']),
                type=request.form.get('type', 'theory')
            )
            db.session.add(subject)
            db.session.flush()  # To get the subject ID
            
            # Add faculty assignments
            faculty_ids = request.form.getlist('faculty_ids')
            print(f"DEBUG: Received faculty_ids: {faculty_ids}")  # Debug print
            for faculty_id in faculty_ids:
                if faculty_id:
                    faculty = Faculty.query.get(int(faculty_id))
                    if faculty:
                        subject.faculty.append(faculty)
                        print(f"DEBUG: Added faculty {faculty.name} to subject {subject.name}")  # Debug print
        
        elif entity == 'batch':
            batch = Batch(
                name=request.form['name'],
                year=int(request.form['year']),
                semester=int(request.form['semester']),
                department=request.form['department'],
                strength=int(request.form['strength'])
            )
            db.session.add(batch)
        
        elif entity == 'student':
            student = User(
                username=request.form['username'],
                password_hash=generate_password_hash(request.form['password']),
                role='student',
                batch_id=int(request.form['batch_id']) if request.form.get('batch_id') else None
            )
            db.session.add(student)
        
        db.session.commit()
        flash(f'{entity.title()} added successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding {entity}: {str(e)}', 'error')
    
    # Handle proper pluralization for redirect
    entity_plurals = {
        'classroom': 'classrooms',
        'faculty': 'faculty',  # faculty is already plural
        'subject': 'subjects',
        'batch': 'batches',
        'student': 'students'
    }
    
    plural_entity = entity_plurals.get(entity, entity + 's')
    return redirect(url_for('manage_entity', entity=plural_entity))

@app.route('/delete_all/<string:entity>', methods=['POST'])
def delete_all_entities(entity):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    try:
        if entity == 'classrooms':
            # Check if any classrooms are being used in timetables
            if Timetable.query.first():
                flash('Cannot delete all classrooms. Some are being used in timetables.', 'error')
                return redirect(url_for('manage_entity', entity='classrooms'))
            Classroom.query.delete()
            flash('All classrooms deleted successfully!', 'success')
        
        elif entity == 'faculty':
            # Check if any faculty are assigned to subjects
            faculty_with_subjects = Faculty.query.join(subject_faculty).first()
            if faculty_with_subjects:
                flash('Cannot delete all faculty. Some are assigned to subjects.', 'error')
                return redirect(url_for('manage_entity', entity='faculty'))
            Faculty.query.delete()
            flash('All faculty deleted successfully!', 'success')
        
        elif entity == 'subjects':
            # Check if any subjects are being used in timetables
            if Timetable.query.first():
                flash('Cannot delete all subjects. Some are being used in timetables.', 'error')
                return redirect(url_for('manage_entity', entity='subjects'))
            Subject.query.delete()
            flash('All subjects deleted successfully!', 'success')
        
        elif entity == 'batches':
            # Check if any batches have students or timetables
            if User.query.filter_by(role='student').first() or Timetable.query.first():
                flash('Cannot delete all batches. Some have students or timetables assigned.', 'error')
                return redirect(url_for('manage_entity', entity='batches'))
            Batch.query.delete()
            flash('All batches deleted successfully!', 'success')
        
        elif entity == 'students':
            User.query.filter_by(role='student').delete()
            flash('All students deleted successfully!', 'success')
        
        elif entity == 'timetables':
            Timetable.query.delete()
            flash('All timetables deleted successfully!', 'success')
        
        else:
            flash('Invalid entity type.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting all {entity}: {str(e)}', 'error')
    
    # Handle proper pluralization for redirect
    entity_plurals = {
        'classrooms': 'classrooms',
        'faculty': 'faculty',
        'subjects': 'subjects',
        'batches': 'batches',
        'students': 'students',
        'timetables': 'admin_dashboard'
    }
    
    if entity == 'timetables':
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('manage_entity', entity=entity))

@app.route('/delete/<string:entity>/<int:item_id>', methods=['POST'])
def delete_entity(entity, item_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    try:
        if entity == 'classroom':
            item = Classroom.query.get_or_404(item_id)
            # Check if classroom is being used in any timetable
            if Timetable.query.filter_by(classroom_id=item_id).first():
                flash('Cannot delete classroom. It is being used in timetables.', 'error')
                return redirect(url_for('manage_entity', entity='classrooms'))
        
        elif entity == 'faculty':
            item = Faculty.query.get_or_404(item_id)
            # Check if faculty is assigned to any subjects
            if item.subjects:
                flash('Cannot delete faculty. They are assigned to subjects.', 'error')
                return redirect(url_for('manage_entity', entity='faculty'))
        
        elif entity == 'subject':
            item = Subject.query.get_or_404(item_id)
            # Check if subject is being used in any timetable
            if Timetable.query.filter_by(subject_id=item_id).first():
                flash('Cannot delete subject. It is being used in timetables.', 'error')
                return redirect(url_for('manage_entity', entity='subjects'))
        
        elif entity == 'batch':
            item = Batch.query.get_or_404(item_id)
            # Check if batch has students or timetables
            if User.query.filter_by(batch_id=item_id).first() or Timetable.query.filter_by(batch_id=item_id).first():
                flash('Cannot delete batch. It has students or timetables assigned.', 'error')
                return redirect(url_for('manage_entity', entity='batches'))
        
        elif entity == 'student':
            item = User.query.filter_by(id=item_id, role='student').first_or_404()
        
        else:
            flash('Invalid entity type.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        db.session.delete(item)
        db.session.commit()
        flash(f'{entity.title()} deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting {entity}: {str(e)}', 'error')
    
    # Handle proper pluralization for redirect
    entity_plurals = {
        'classroom': 'classrooms',
        'faculty': 'faculty',
        'subject': 'subjects',
        'batch': 'batches',
        'student': 'students'
    }
    
    plural_entity = entity_plurals.get(entity, entity + 's')
    return redirect(url_for('manage_entity', entity=plural_entity))

@app.route('/generate_timetable', methods=['GET', 'POST'])
def generate_timetable():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Simple timetable generation logic
        batch_id = request.form['batch_id']
        max_classes_per_day = int(request.form.get('max_classes_per_day', 6))
        
        # Clear existing timetable for this batch
        Timetable.query.filter_by(batch_id=batch_id).delete()
        
        # Get subjects for this batch
        batch = Batch.query.get(batch_id)
        subjects = Subject.query.filter_by(semester=batch.semester, department=batch.department).all()
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        time_slots = ['09:15-10:15', '10:15-11:15', '11:15-12:15', '12:15-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00']
        
        # Get faculty assignments from form
        faculty_assignments = {}
        for key, value in request.form.items():
            if key.startswith('subject_faculty_') and value:
                subject_id = int(key.replace('subject_faculty_', ''))
                faculty_assignments[subject_id] = int(value)
        
        # Define 2-hour lab time slots (matching the image layout)
        lab_time_slots = ['09:15-11:15', '10:15-12:15', '01:00-03:00', '02:00-04:00']
        scheduled_slots = set()  # Track occupied slots to avoid conflicts
        
        # Import random for randomized scheduling
        import random
        
        # Create list of all available time slots (excluding lunch)
        available_slots = []
        for day in days:
            for time_slot in time_slots:
                if time_slot != '12:15-01:00':  # Skip lunch break
                    available_slots.append((day, time_slot))
        
        # Shuffle the available slots for randomization
        random.shuffle(available_slots)
        
        # Randomized assignment with free periods
        for subject in subjects:
            # Get assigned faculty for this subject
            faculty_id = faculty_assignments.get(subject.id)
            if not faculty_id:
                # If no faculty assigned, skip this subject or use first available faculty
                if subject.faculty:
                    faculty_id = subject.faculty[0].id
                else:
                    flash(f'No faculty assigned for {subject.name}. Skipping this subject.', 'warning')
                    continue
            
            classes_needed = subject.hours_per_week
            
            # Handle lab/practical subjects (2-hour continuous slots like in the image)
            if subject.type == 'practical':
                lab_sessions_needed = (classes_needed + 1) // 2  # Round up for 2-hour blocks
                
                # Create list of available lab slots and shuffle them
                available_lab_slots = []
                for day in days:
                    for lab_slot in lab_time_slots:
                        available_lab_slots.append((day, lab_slot))
                random.shuffle(available_lab_slots)
                
                for lab_session in range(lab_sessions_needed):
                    scheduled = False
                    # Try to find an available 2-hour slot randomly
                    for day, lab_slot in available_lab_slots:
                        slot_key = f"{day}_{lab_slot}"
                        
                        # Check for conflicts with existing bookings
                        conflict = False
                        if lab_slot == '09:15-11:15':
                            if f"{day}_09:15-10:15" in scheduled_slots or f"{day}_10:15-11:15" in scheduled_slots:
                                conflict = True
                        elif lab_slot == '10:15-12:15':
                            if f"{day}_10:15-11:15" in scheduled_slots or f"{day}_11:15-12:15" in scheduled_slots:
                                conflict = True
                        elif lab_slot == '01:00-03:00':
                            if f"{day}_01:00-02:00" in scheduled_slots or f"{day}_02:00-03:00" in scheduled_slots:
                                conflict = True
                        elif lab_slot == '02:00-04:00':
                            if f"{day}_02:00-03:00" in scheduled_slots or f"{day}_03:00-04:00" in scheduled_slots:
                                conflict = True
                        
                        if not conflict and slot_key not in scheduled_slots:
                            # Find suitable classroom (prefer lab type)
                            classroom = Classroom.query.filter_by(type='lab', is_available=True).first()
                            if not classroom:
                                classroom = Classroom.query.filter_by(is_available=True).first()
                            
                            if classroom:
                                # Create the 2-hour lab entry
                                timetable_entry = Timetable(
                                    batch_id=batch_id,
                                    subject_id=subject.id,
                                    faculty_id=faculty_id,
                                    classroom_id=classroom.id,
                                    day_of_week=day,
                                    time_slot=lab_slot
                                )
                                db.session.add(timetable_entry)
                                
                                # Block the 2-hour slot and constituent 1-hour slots
                                scheduled_slots.add(slot_key)
                                if lab_slot == '09:15-11:15':
                                    scheduled_slots.add(f"{day}_09:15-10:15")
                                    scheduled_slots.add(f"{day}_10:15-11:15")
                                elif lab_slot == '10:15-12:15':
                                    scheduled_slots.add(f"{day}_10:15-11:15")
                                    scheduled_slots.add(f"{day}_11:15-12:15")
                                elif lab_slot == '01:00-03:00':
                                    scheduled_slots.add(f"{day}_01:00-02:00")
                                    scheduled_slots.add(f"{day}_02:00-03:00")
                                elif lab_slot == '02:00-04:00':
                                    scheduled_slots.add(f"{day}_02:00-03:00")
                                    scheduled_slots.add(f"{day}_03:00-04:00")
                                
                                scheduled = True
                                print(f"DEBUG: Scheduled lab {subject.name} on {day} {lab_slot}")
                                
                                # Remove used slots from available list
                                available_lab_slots = [(d, s) for d, s in available_lab_slots if f"{d}_{s}" != slot_key]
                                break
                    
                    if not scheduled:
                        flash(f'Could not schedule all lab sessions for {subject.name}', 'warning')
                        break
            
            # Handle regular 1-hour subjects
            else:
                # Create a copy of available slots for this subject
                subject_available_slots = [slot for slot in available_slots if f"{slot[0]}_{slot[1]}" not in scheduled_slots]
                
                # Limit scheduling to create free periods (schedule only 60-80% of needed classes randomly)
                max_classes_to_schedule = max(1, int(classes_needed * random.uniform(0.6, 0.9)))
                classes_to_schedule = min(classes_needed, max_classes_to_schedule)
                
                for _ in range(classes_to_schedule):
                    if not subject_available_slots:
                        flash(f'No more available slots for {subject.name}', 'warning')
                        break
                    
                    # Pick a random slot from available slots
                    slot_index = random.randint(0, len(subject_available_slots) - 1)
                    day, time_slot = subject_available_slots[slot_index]
                    slot_key = f"{day}_{time_slot}"
                    
                    # Find available classroom
                    classroom = Classroom.query.filter_by(is_available=True).first()
                    if classroom:
                        timetable_entry = Timetable(
                            batch_id=batch_id,
                            subject_id=subject.id,
                            faculty_id=faculty_id,
                            classroom_id=classroom.id,
                            day_of_week=day,
                            time_slot=time_slot
                        )
                        db.session.add(timetable_entry)
                        scheduled_slots.add(slot_key)
                        
                        # Remove the used slot from available slots
                        subject_available_slots.pop(slot_index)
                        print(f"DEBUG: Scheduled {subject.name} on {day} {time_slot}")
                    else:
                        flash(f'No available classroom for {subject.name}', 'warning')
                        break
        
        db.session.commit()
        flash('Timetable generated successfully!', 'success')
        return redirect(url_for('view_timetable', batch_id=batch_id))
    
    # Calculate statistics for the dashboard
    batches = Batch.query.all()
    subjects = Subject.query.all()
    faculties = Faculty.query.all()
    classrooms = Classroom.query.all()
    
    # Count active timetables
    active_timetables = db.session.query(Batch).join(Timetable).distinct().count()
    
    # Count total classes scheduled
    total_classes = Timetable.query.count()
    
    # Count different types of classes
    theory_count = db.session.query(Timetable).join(Subject).filter(Subject.type == 'theory').count()
    practical_count = db.session.query(Timetable).join(Subject).filter(Subject.type == 'practical').count()
    tutorial_count = db.session.query(Timetable).join(Subject).filter(Subject.type == 'tutorial').count()
    
    # Calculate stats for checklist
    stats = {
        'batches_count': len(batches),
        'subjects_count': len(subjects),
        'faculties_count': len(faculties),
        'classrooms_count': len(classrooms),
        'active_timetables': active_timetables,
        'total_classes': total_classes,
        'theory_count': theory_count,
        'practical_count': practical_count,
        'tutorial_count': tutorial_count,
        'subjects_with_faculty': db.session.query(Subject).filter(Subject.faculty.any()).count(),
        'available_classrooms': Classroom.query.filter_by(is_available=True).count()
    }
    
    return render_template('generate_timetable.html', batches=batches, stats=stats)

@app.route('/view_timetable/<int:batch_id>')
def view_timetable(batch_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Students can only view their own batch timetable
    if session.get('user_role') == 'student':
        if session.get('batch_id') != batch_id:
            flash('Access denied. You can only view your own timetable.', 'error')
            return redirect(url_for('student_dashboard'))
    
    batch = Batch.query.get_or_404(batch_id)
    timetable_entries = db.session.query(Timetable, Subject, Faculty, Classroom).join(
        Subject, Timetable.subject_id == Subject.id
    ).join(
        Faculty, Timetable.faculty_id == Faculty.id
    ).join(
        Classroom, Timetable.classroom_id == Classroom.id
    ).filter(Timetable.batch_id == batch_id).all()
    
    # Organize by day and time
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = ['09:15-10:15', '10:15-11:15', '11:15-12:15', '12:15-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00']
    lab_time_slots = ['09:15-11:15', '10:15-12:15', '01:00-03:00', '02:00-04:00']
    
    timetable = {}
    for day in days:
        timetable[day] = {}
        # Initialize regular time slots
        for time_slot in time_slots:
            timetable[day][time_slot] = None
        # Initialize lab time slots
        for lab_slot in lab_time_slots:
            timetable[day][lab_slot] = None

    for entry, subject, faculty, classroom in timetable_entries:
        timetable[entry.day_of_week][entry.time_slot] = {
            'subject': subject.name,
            'faculty': faculty.name,
            'classroom': classroom.name,
            'type': subject.type
        }

    # Check if timetable is approved
    is_approved = False
    if timetable_entries:
        # Check if all entries are approved
        is_approved = all(entry.is_approved for entry, _, _, _ in timetable_entries)

    # Calculate statistics for this specific batch
    # Count actual hours (lab sessions count as 2 hours each)
    total_hours = 0
    theory_count = 0
    practical_count = 0
    tutorial_count = 0
    
    for entry, subject, _, _ in timetable_entries:
        if subject.type == 'theory':
            theory_count += 1
            total_hours += 1  # Theory classes are 1 hour
        elif subject.type == 'practical':
            practical_count += 1
            # Check if it's a 2-hour lab session
            if entry.time_slot in ['09:15-11:15', '10:15-12:15', '01:00-03:00', '02:00-04:00']:
                total_hours += 2  # Lab sessions are 2 hours
            else:
                total_hours += 1  # Regular practical is 1 hour
        elif subject.type == 'tutorial':
            tutorial_count += 1
            total_hours += 1  # Tutorial classes are 1 hour

    return render_template('view_timetable.html', batch=batch, timetable=timetable, 
                         days=days, time_slots=time_slots, lab_time_slots=lab_time_slots, 
                         is_approved=is_approved, total_hours=total_hours,
                         theory_count=theory_count, practical_count=practical_count,
                         tutorial_count=tutorial_count)

@app.route('/view_all_timetables')
def view_all_timetables():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    # Get all batches that have timetables
    batches_with_timetables = db.session.query(Batch).join(Timetable).distinct().all()
    
    # If there's only one batch, redirect directly to its detailed view
    if len(batches_with_timetables) == 1:
        return redirect(url_for('view_timetable', batch_id=batches_with_timetables[0].id))
    
    # Create simplified batch list for selection instead of showing incomplete previews
    batches_data = []
    for batch in batches_with_timetables:
        # Get basic stats for each batch
        total_classes = db.session.query(Timetable).filter(Timetable.batch_id == batch.id).count()
        
        # Count class types
        class_types = db.session.query(Subject.type, db.func.count(Timetable.id)).join(
            Timetable, Subject.id == Timetable.subject_id
        ).filter(Timetable.batch_id == batch.id).group_by(Subject.type).all()
        
        type_counts = {type_name: count for type_name, count in class_types}
        
        batches_data.append({
            'batch': batch,
            'total_classes': total_classes,
            'theory_count': type_counts.get('theory', 0),
            'practical_count': type_counts.get('practical', 0),
            'tutorial_count': type_counts.get('tutorial', 0)
        })
    
    return render_template('batch_selection.html', batches_data=batches_data)

@app.route('/suggest_changes/<int:batch_id>')
def suggest_changes(batch_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    batch = Batch.query.get_or_404(batch_id)
    
    # Get current timetable data
    timetable_entries = db.session.query(Timetable, Subject, Faculty, Classroom).join(
        Subject, Timetable.subject_id == Subject.id
    ).join(
        Faculty, Timetable.faculty_id == Faculty.id
    ).join(
        Classroom, Timetable.classroom_id == Classroom.id
    ).filter(Timetable.batch_id == batch_id).all()
    
    # Get all available resources for dropdowns
    subjects = Subject.query.all()
    faculties = Faculty.query.all()
    classrooms = Classroom.query.all()
    
    # Organize timetable by day and time
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = ['09:15-10:15', '10:15-11:15', '11:15-12:15', '12:15-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00']
    all_time_slots = time_slots + ['09:15-11:15', '10:15-12:15', '01:00-03:00', '02:00-04:00']
    
    timetable = {}
    for day in days:
        timetable[day] = {}
        for time_slot in all_time_slots:
            timetable[day][time_slot] = None
    
    for entry, subject, faculty, classroom in timetable_entries:
        timetable[entry.day_of_week][entry.time_slot] = {
            'id': entry.id,
            'subject': subject.name,
            'subject_id': subject.id,
            'faculty': faculty.name,
            'faculty_id': faculty.id,  
            'classroom': classroom.name,
            'classroom_id': classroom.id,
            'type': subject.type
        }
    
    return render_template('edit_timetable.html', 
                         batch=batch, 
                         timetable=timetable, 
                         days=days, 
                         time_slots=time_slots,
                         subjects=subjects,
                         faculties=faculties,
                         classrooms=classrooms)

@app.route('/update_timetable_entry', methods=['POST'])
def update_timetable_entry():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        data = request.get_json()
        batch_id = data.get('batch_id')
        day = data.get('day')
        time_slot = data.get('time_slot')
        subject_id = data.get('subject_id')
        faculty_id = data.get('faculty_id')
        classroom_id = data.get('classroom_id')
        action = data.get('action')  # 'add', 'update', 'delete'
        
        if action == 'delete' and data.get('entry_id'):
            # Delete existing entry
            entry = Timetable.query.get(data.get('entry_id'))
            if entry:
                db.session.delete(entry)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Entry deleted successfully'})
        
        elif action in ['add', 'update']:
            if not all([batch_id, day, time_slot, subject_id, faculty_id, classroom_id]):
                return jsonify({'success': False, 'message': 'Missing required fields'})
            
            # Check for conflicts (except for the entry being updated)
            existing_entry = None
            if action == 'update' and data.get('entry_id'):
                existing_entry = Timetable.query.get(data.get('entry_id'))
            
            # Faculty conflict check
            faculty_conflict = db.session.query(Timetable).filter(
                Timetable.faculty_id == faculty_id,
                Timetable.day_of_week == day,
                Timetable.time_slot == time_slot,
                Timetable.id != (existing_entry.id if existing_entry else 0)
            ).first()
            
            if faculty_conflict:
                return jsonify({'success': False, 'message': 'Faculty is already scheduled for this time slot'})
            
            # Classroom conflict check
            classroom_conflict = db.session.query(Timetable).filter(
                Timetable.classroom_id == classroom_id,
                Timetable.day_of_week == day,
                Timetable.time_slot == time_slot,
                Timetable.id != (existing_entry.id if existing_entry else 0)
            ).first()
            
            if classroom_conflict:
                return jsonify({'success': False, 'message': 'Classroom is already booked for this time slot'})
            
            if action == 'update' and existing_entry:
                # Update existing entry
                existing_entry.subject_id = subject_id
                existing_entry.faculty_id = faculty_id
                existing_entry.classroom_id = classroom_id
            else:
                # Add new entry
                new_entry = Timetable(
                    batch_id=batch_id,
                    subject_id=subject_id,
                    faculty_id=faculty_id,
                    classroom_id=classroom_id,
                    day_of_week=day,
                    time_slot=time_slot
                )
                db.session.add(new_entry)
            
            db.session.commit()
            
            # Get updated entry data for response
            subject = Subject.query.get(subject_id)
            faculty = Faculty.query.get(faculty_id)
            classroom = Classroom.query.get(classroom_id)
            
            return jsonify({
                'success': True, 
                'message': 'Timetable updated successfully',
                'entry': {
                    'subject': subject.name,
                    'faculty': faculty.name,
                    'classroom': classroom.name,
                    'type': subject.type
                }
            })
        
        return jsonify({'success': False, 'message': 'Invalid action'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_batch_timetable/<int:batch_id>', methods=['POST'])
def delete_batch_timetable(batch_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    try:
        # Get batch name for the flash message
        batch = Batch.query.get_or_404(batch_id)
        batch_name = batch.name
        
        # Delete all timetable entries for this batch
        deleted_count = Timetable.query.filter_by(batch_id=batch_id).delete()
        db.session.commit()
        
        flash(f'Timetable for {batch_name} deleted successfully! ({deleted_count} classes removed)', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting timetable: {str(e)}', 'error')
    
    return redirect(url_for('view_all_timetables'))

@app.route('/get_batch_subjects_faculty/<int:batch_id>')
def get_batch_subjects_faculty(batch_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get batch details
        batch = Batch.query.get_or_404(batch_id)
        
        # Get subjects for this batch (same semester and department)
        subjects = Subject.query.filter_by(
            semester=batch.semester, 
            department=batch.department
        ).all()
        
        # Format response data
        subjects_data = []
        for subject in subjects:
            faculty_data = []
            for faculty in subject.faculty:
                faculty_data.append({
                    'id': faculty.id,
                    'name': faculty.name,
                    'department': faculty.department
                })
            
            subjects_data.append({
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'hours_per_week': subject.hours_per_week,
                'type': subject.type,
                'faculty': faculty_data
            })
        
        return jsonify({
            'subjects': subjects_data,
            'batch': {
                'id': batch.id,
                'name': batch.name,
                'department': batch.department,
                'semester': batch.semester
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database
@app.route('/approve_timetable/<int:batch_id>', methods=['POST'])
def approve_timetable(batch_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    try:
        # Update all timetable entries for this batch to approved status
        timetable_entries = Timetable.query.filter_by(batch_id=batch_id).all()
        
        if not timetable_entries:
            flash('No timetable found for this batch.', 'error')
            return redirect(url_for('view_timetable', batch_id=batch_id))
        
        # Set all entries as approved
        for entry in timetable_entries:
            entry.is_approved = True
        
        db.session.commit()
        
        batch = Batch.query.get(batch_id)
        flash(f'Timetable for {batch.name} has been successfully approved!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving timetable: {str(e)}', 'error')
    
    return redirect(url_for('view_timetable', batch_id=batch_id))

def init_db():
    with app.app_context():
        # Only create tables, don't drop existing ones
        db.create_all()
        print("Database tables initialized")
        
        # Check if we have any existing data (beyond the default users)
        existing_data_count = (
            Classroom.query.count() + 
            Faculty.query.count() + 
            Subject.query.count() + 
            Batch.query.count() + 
            Timetable.query.count()
        )
        
        # Only create sample data if database is completely empty
        if existing_data_count == 0:
            print("Creating initial sample data...")
            create_sample_data()
        else:
            print(f"Existing data found ({existing_data_count} records). Skipping sample data creation.")
        
        # Always ensure default users exist (but don't recreate if they exist)
        ensure_default_users()

def ensure_default_users():
    """Ensure default admin and student users exist without overwriting existing data"""
    # Create default admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: admin/admin123")
    
    # Only create sample student if no students exist and we have batches
    if not User.query.filter_by(role='student').first() and Batch.query.first():
        first_batch = Batch.query.first()
        student_user = User(
            username='student1',
            password_hash=generate_password_hash('password123'),
            role='student',
            batch_id=first_batch.id
        )
        db.session.add(student_user)
        db.session.commit()
        print("Default student user created: student1/password123")

def create_sample_data():
    """Create minimal sample data only when database is empty"""
    try:
        # Create sample batch first
        sample_batch = Batch(
            name='CS-2024-A',
            year=2,
            semester=3,
            department='Computer Science',
            strength=60
        )
        db.session.add(sample_batch)
        
        # Create sample classrooms
        sample_classrooms = [
            Classroom(name='Room 101', capacity=60, type='regular', is_available=True),
            Classroom(name='Lab A', capacity=30, type='lab', is_available=True),
            Classroom(name='Auditorium', capacity=200, type='auditorium', is_available=True)
        ]
        for classroom in sample_classrooms:
            db.session.add(classroom)
        
        # Create sample faculty
        sample_faculty = [
            Faculty(name='Dr. John Smith', email='john.smith@college.edu', department='Computer Science', max_hours_per_day=6),
            Faculty(name='Prof. Sarah Johnson', email='sarah.johnson@college.edu', department='Computer Science', max_hours_per_day=5),
            Faculty(name='Dr. Michael Brown', email='michael.brown@college.edu', department='Mathematics', max_hours_per_day=6)
        ]
        for faculty in sample_faculty:
            db.session.add(faculty)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create sample subjects and assign faculty
        faculty_members = Faculty.query.all()
        sample_subjects = [
            Subject(name='Data Structures', code='CS201', semester=3, department='Computer Science', hours_per_week=4, type='theory'),
            Subject(name='Database Systems', code='CS301', semester=3, department='Computer Science', hours_per_week=3, type='theory'),
            Subject(name='Programming Lab', code='CS202', semester=3, department='Computer Science', hours_per_week=2, type='practical')
        ]
        
        for i, subject in enumerate(sample_subjects):
            db.session.add(subject)
            db.session.flush()  # To get the subject ID
            
            # Assign faculty to subjects
            for j, faculty in enumerate(faculty_members):
                if j <= i:  # First subject gets first faculty, second gets first two, etc.
                    subject.faculty.append(faculty)
        
        db.session.commit()
        print("Minimal sample data created successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {e}")
        raise

@app.route('/backup_data')
def backup_data():
    """Create a backup of current database data"""
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    try:
        import json
        import os
        from datetime import datetime
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'batches': [],
            'subjects': [],
            'faculty': [],
            'classrooms': [],
            'users': [],
            'timetables': []
        }
        
        # Backup all data
        for batch in Batch.query.all():
            backup_data['batches'].append({
                'name': batch.name,
                'year': batch.year,
                'semester': batch.semester,
                'department': batch.department,
                'strength': batch.strength
            })
        
        for subject in Subject.query.all():
            backup_data['subjects'].append({
                'name': subject.name,
                'code': subject.code,
                'semester': subject.semester,
                'department': subject.department,
                'hours_per_week': subject.hours_per_week,
                'type': subject.type
            })
        
        for faculty in Faculty.query.all():
            backup_data['faculty'].append({
                'name': faculty.name,
                'email': faculty.email,
                'department': faculty.department,
                'max_hours_per_day': faculty.max_hours_per_day
            })
        
        for classroom in Classroom.query.all():
            backup_data['classrooms'].append({
                'name': classroom.name,
                'capacity': classroom.capacity,
                'type': classroom.type,
                'is_available': classroom.is_available
            })
        
        # Save backup file
        backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'timetable_backup_{timestamp}.json')
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        flash(f'Data backup created successfully: {backup_file}', 'success')
        
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)