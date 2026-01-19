import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, or_
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from flask_mail import Mail, Message
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

import os
from dotenv import load_dotenv # Added dotenv import

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Database Configuration (Supabase/PostgreSQL vs SQLite)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///food_redistribution.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'harshanani576@gmail.com'
app.config['MAIL_PASSWORD'] = 'gfwo qhlv uqha lapi'
app.config['MAIL_DEFAULT_SENDER'] = 'harshanani576@gmail.com'

mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'donor', 'receiver', 'admin'
    organization_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    unique_id = db.Column(db.String(10), unique=True, nullable=True)  # New 10-digit UID
    
    # Relationships
    donations = db.relationship('Donation', foreign_keys='Donation.donor_id', backref='donor', lazy=True)
    requests = db.relationship('FoodRequest', backref='receiver', lazy=True)
    claimed_donations = db.relationship('Donation', foreign_keys='Donation.claimed_by', backref='claimer', lazy=True)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    quantity_unit = db.Column(db.String(20), default='kg')
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='available')  # 'available', 'claimed', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    claimed_at = db.Column(db.DateTime, nullable=True)

class FoodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type_needed = db.Column(db.String(100), nullable=False)
    quantity_needed = db.Column(db.Integer, nullable=False)
    quantity_unit = db.Column(db.String(20), default='kg')
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'fulfilled', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fulfilled_at = db.Column(db.DateTime, nullable=True)

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        # Check if user exists in DB
        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            flash('Session expired or invalid. Please login again.', 'warning')
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

# Decorator for role-based access
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' not in session or session['user_type'] != role:
                flash('Access denied. You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper Functions
def generate_unique_id():
    """Generates a random 10-digit unique ID."""
    while True:
        # Generate 10 random digits
        uid = ''.join(random.choices(string.digits, k=10))
        # Check if it already exists
        if not User.query.filter_by(unique_id=uid).first():
            return uid

def send_uid_email(email, username, uid):
    """
    Mock function to send an email.
    In production, this would use an SMTP server.
    """
    print("="*50)
    print(f" [MOCK EMAIL SENT]")
    print(f" To: {email}")
    print(f" Subject: Welcome to FoodShare! Your Unique ID")
    print("-" * 30)
    print(f" Dear {username},")
    print(f" Welcome to FoodShare! Your account has been created.")
    print(f" Your Unique ID (UID) is: {uid}")
    print(f" You can use this UID or your username to login.")
    print("="*50)

def backfill_unique_ids():
    """Assigns unique IDs to existing users who don't have one."""
    users_without_id = User.query.filter_by(unique_id=None).all()
    if users_without_id:
        print(f"Backfilling UIDs for {len(users_without_id)} users...")
        for user in users_without_id:
            user.unique_id = generate_unique_id()
            print(f"Assigned UID {user.unique_id} to user {user.username}")
        try:
            db.session.commit()
            print("Backfill complete.")
        except Exception as e:
            db.session.rollback()
            print(f"Error backfilling UIDs: {e}")

def generate_confirmation_pdf(donation, receiver):
    """Generates a PDF confirmation for the claimed donation."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "FoodShare Donation Confirmation")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, height - 100, f"Confirmation ID: #{donation.id}")

    c.line(50, height - 110, width - 50, height - 110)

    # Donation Details
    y = height - 150
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Donation Details:")
    y -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Food Type: {donation.food_type}")
    y -= 25
    c.drawString(50, y, f"Quantity: {donation.quantity} {donation.quantity_unit}")
    y -= 25
    c.drawString(50, y, f"Location: {donation.location}")
    y -= 25
    if donation.description:
        c.drawString(50, y, f"Description: {donation.description}")
        y -= 25
    
    # Donor Details
    y -= 20
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Donor Details:")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Donor Name: {donation.donor.username}")
    y -= 25
    if donation.donor.organization_name:
        c.drawString(50, y, f"Organization: {donation.donor.organization_name}")
        y -= 25
    c.drawString(50, y, f"Contact: {donation.donor.email}") # Use email as contact for now
    
    # Receiver Details
    y -= 20
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Claimed By:")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Receiver Name: {receiver.username}")
    y -= 25
    if receiver.organization_name:
        c.drawString(50, y, f"Organization: {receiver.organization_name}")
        y -= 25
    c.drawString(50, y, f"Email: {receiver.email}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Thank you for using FoodShare. Together we reduce waste and feed the needy.")
    
    c.save()
    buffer.seek(0)
    return buffer

# Routes

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        organization_name = request.form.get('organization_name', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        uid = generate_unique_id() # Generate UID
        
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type=user_type,
            organization_name=organization_name,
            phone=phone,
            address=address,
            unique_id=uid
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send email with UID
        send_uid_email(email, username, uid)
        
        flash(f'Registration successful! Your Unique ID is {uid}. Please check your email.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username_input = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']
    
    # Check by Username OR Unique ID
    user = User.query.filter(
        (User.username == username_input) | (User.unique_id == username_input),
        User.user_type == user_type
    ).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['user_type'] = user.user_type
        flash(f'Welcome, {user.username}!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials or user type!', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    
    if user.user_type == 'donor':
        return redirect(url_for('donor_dashboard'))
    elif user.user_type == 'receiver':
        return redirect(url_for('receiver_dashboard'))
    elif user.user_type == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('index'))

@app.route('/donor/dashboard')
@login_required
@role_required('donor')
def donor_dashboard():
    user = db.session.get(User, session['user_id'])
    
    # Get statistics
    total_donations = Donation.query.filter_by(donor_id=user.id).count()
    total_quantity = db.session.query(db.func.sum(Donation.quantity)).filter_by(donor_id=user.id).scalar() or 0
    claimed_donations = Donation.query.filter_by(donor_id=user.id, status='claimed').count()
    completed_donations = Donation.query.filter_by(donor_id=user.id, status='completed').count()
    
    # Recent donations
    recent_donations = Donation.query.filter_by(donor_id=user.id).order_by(Donation.created_at.desc()).limit(10).all()
    
    # Monthly donations (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_data = db.session.query(
        db.func.strftime('%Y-%m', Donation.created_at).label('month'),
        db.func.sum(Donation.quantity).label('total')
    ).filter(
        Donation.donor_id == user.id,
        Donation.created_at >= six_months_ago
    ).group_by('month').all()
    
    return render_template('donor_dashboard.html', 
                         user=user,
                         total_donations=total_donations,
                         total_quantity=total_quantity,
                         claimed_donations=claimed_donations,
                         completed_donations=completed_donations,
                         recent_donations=recent_donations,
                         monthly_data=monthly_data)

@app.route('/donor/donate', methods=['POST'])
@login_required
@role_required('donor')
def donate_food():
    user = db.session.get(User, session['user_id'])
    
    food_type = request.form['food_type']
    quantity = int(request.form['quantity'])
    quantity_unit = request.form.get('quantity_unit', 'kg')
    description = request.form.get('description', '')
    location = request.form['location']
    expiry_date_str = request.form.get('expiry_date', '')
    
    expiry_date = None
    if expiry_date_str:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    
    new_donation = Donation(
        donor_id=user.id,
        food_type=food_type,
        quantity=quantity,
        quantity_unit=quantity_unit,
        description=description,
        location=location,
        expiry_date=expiry_date,
        status='available'
    )
    
    db.session.add(new_donation)
    db.session.commit()
    
    flash('Food donation posted successfully!', 'success')
    return redirect(url_for('donor_dashboard'))

@app.route('/receiver/dashboard')
@login_required
@role_required('receiver')
def receiver_dashboard():
    user_id = session['user_id']
    
    # Get user and refresh to ensure we have latest data
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    
    # Commit any pending transactions to ensure fresh data
    db.session.commit()
    
    # Get statistics with fresh queries
    # My Claimed Donations
    claimed_donations = db.session.query(Donation).filter_by(
        claimed_by=user_id, status='claimed'
    ).order_by(
        Donation.claimed_at.desc()
    ).limit(20).all()
    
    # Available donations
    available_donations = db.session.query(Donation).filter_by(
        status='available'
    ).order_by(
        Donation.expiry_date.asc(),  # Priority: Sooner expiry = Higher priority (Lower serial no)
        Donation.created_at.desc()
    ).limit(20).all()
    
    response = make_response(render_template('receiver_dashboard.html',
                         user=user,
                         available_donations=available_donations,
                         claimed_donations=claimed_donations))
    # Prevent caching to ensure fresh data
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/receiver/request', methods=['POST'])
@login_required
@role_required('receiver')
def request_food():
    user = db.session.get(User, session['user_id'])
    
    food_type_needed = request.form['food_type_needed']
    quantity_needed = int(request.form['quantity_needed'])
    quantity_unit = request.form.get('quantity_unit', 'kg')
    description = request.form.get('description', '')
    location = request.form['location']
    
    new_request = FoodRequest(
        receiver_id=user.id,
        food_type_needed=food_type_needed,
        quantity_needed=quantity_needed,
        quantity_unit=quantity_unit,
        description=description,
        location=location,
        status='pending'
    )
    
    try:
        db.session.add(new_request)
        db.session.commit()
        flash('Food request submitted successfully!', 'success')
        # Use redirect with cache-busting parameter to force fresh page load
        return redirect(url_for('receiver_dashboard') + '?submitted=true&_=' + str(datetime.utcnow().timestamp()), code=302)
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting request: {str(e)}', 'danger')
        return redirect(url_for('receiver_dashboard'))

@app.route('/receiver/claim/<int:donation_id>')
@login_required
@role_required('receiver')
def claim_donation(donation_id):
    user = db.session.get(User, session['user_id'])
    donation = db.get_or_404(Donation, donation_id)
    
    if donation.status == 'available':
        donation.status = 'claimed'
        donation.claimed_by = user.id
        donation.claimed_at = datetime.utcnow()
        db.session.commit()
        
        # --- Email Sending Logic ---
        try:
            # Generate PDF
            pdf_buffer = generate_confirmation_pdf(donation, user)
            pdf_data = pdf_buffer.getvalue()
            pdf_filename = f"FoodShare_Confirmation_{donation.id}.pdf"

            # 1. Email to Receiver
            msg_receiver = Message(
                subject=f"FoodShare Donation Confirmation (#{donation.id})",
                recipients=[user.email],
                body=f"Dear {user.username},\n\nYou have successfully claimed a donation of {donation.food_type}. A confirmation PDF is attached.\n\nPlease contact the donor to arrange pickup.\n\nThank you,\nFoodShare Team"
            )
            msg_receiver.attach(pdf_filename, "application/pdf", pdf_data)
            mail.send(msg_receiver)

            # 2. Email to Donor
            # Fetch donor email (need to access donor object via relationship)
            donor = donation.donor # Assuming relationship is set up
            if donor:
                msg_donor = Message(
                    subject=f"FoodShare: Your Donation Claimed (#{donation.id})",
                    recipients=[donor.email],
                    body=f"Dear {donor.username},\n\nYour donation of {donation.food_type} has been claimed by {user.username}.\n\nA confirmation PDF is attached for your records.\n\nThank you,\nFoodShare Team"
                )
                msg_donor.attach(pdf_filename, "application/pdf", pdf_data)
                mail.send(msg_donor)
                
            flash('Donation claimed successfully! Confirmation email sent.', 'success')
            
        except Exception as e:
            print(f"Email error: {e}")
            flash('Donation claimed, but failed to send confirmation email.', 'warning')
        # ---------------------------

    else:
        flash('This donation is no longer available.', 'danger')
    
    return redirect(url_for('receiver_dashboard'))

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    # Get current user for display
    user = db.session.get(User, session['user_id'])
    
    # Overall statistics
    total_donations = Donation.query.count()
    total_quantity = db.session.query(db.func.sum(Donation.quantity)).scalar() or 0
    total_receivers = User.query.filter_by(user_type='receiver').count()
    total_donors = User.query.filter_by(user_type='donor').count()
    
    # Daily statistics
    today = datetime.utcnow().date()
    today_donations = Donation.query.filter(
        db.func.date(Donation.created_at) == today
    ).count()
    today_quantity = db.session.query(db.func.sum(Donation.quantity)).filter(
        db.func.date(Donation.created_at) == today
    ).scalar() or 0
    today_claims = Donation.query.filter(
        Donation.claimed_at.isnot(None),
        db.func.date(Donation.claimed_at) == today
    ).count()
    today_requests = FoodRequest.query.filter(
        db.func.date(FoodRequest.created_at) == today
    ).count()
    today_completed = Donation.query.filter(
        Donation.claimed_at.isnot(None),
        db.func.date(Donation.claimed_at) == today,
        Donation.status == 'completed'
    ).count()
    
    # Weekly statistics (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_donations = Donation.query.filter(Donation.created_at >= week_ago).count()
    week_quantity = db.session.query(db.func.sum(Donation.quantity)).filter(
        Donation.created_at >= week_ago
    ).scalar() or 0
    # Count distinct receivers who made requests this week
    week_receiver_ids = db.session.query(FoodRequest.receiver_id).filter(
        FoodRequest.created_at >= week_ago
    ).distinct().all()
    week_receivers = len(week_receiver_ids) if week_receiver_ids else 0
    
    # Status breakdown
    available_donations = Donation.query.filter_by(status='available').count()
    claimed_donations = Donation.query.filter_by(status='claimed').count()
    completed_donations = Donation.query.filter_by(status='completed').count()
    
    # Food type breakdown (top 10)
    try:
        food_type_stats = db.session.query(
            Donation.food_type,
            db.func.count(Donation.id).label('count'),
            db.func.sum(Donation.quantity).label('total_quantity')
        ).group_by(Donation.food_type).order_by(desc('count')).limit(10).all()
    except Exception:
        food_type_stats = []
    
    # Recent donations
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(20).all()
    
    # Recent requests
    recent_requests = FoodRequest.query.order_by(FoodRequest.created_at.desc()).limit(10).all()
    
    # Top donors (by quantity)
    try:
        top_donors = db.session.query(
            User.username,
            User.id,
            User.email,
            db.func.sum(Donation.quantity).label('total_quantity'),
            db.func.count(Donation.id).label('donation_count')
        ).join(Donation, User.id == Donation.donor_id).filter(
            User.user_type == 'donor'
        ).group_by(User.id, User.username, User.email).order_by(desc('total_quantity')).limit(10).all()
    except Exception:
        top_donors = []
    
    # Active receivers
    try:
        active_receivers = db.session.query(
            User.username,
            User.id,
            User.organization_name,
            db.func.count(FoodRequest.id).label('request_count')
        ).join(FoodRequest, User.id == FoodRequest.receiver_id).filter(
            User.user_type == 'receiver'
        ).group_by(User.id, User.username, User.organization_name).order_by(desc('request_count')).limit(10).all()
    except Exception:
        active_receivers = []
    
    # Daily data for last 7 days
    daily_stats = []
    max_donations = 0
    max_quantity = 0
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_donations = Donation.query.filter(
            db.func.date(Donation.created_at) == day
        ).count()
        day_quantity = db.session.query(db.func.sum(Donation.quantity)).filter(
            db.func.date(Donation.created_at) == day
        ).scalar() or 0
        day_claims = Donation.query.filter(
            Donation.claimed_at.isnot(None),
            db.func.date(Donation.claimed_at) == day
        ).count()
        max_donations = max(max_donations, day_donations)
        max_quantity = max(max_quantity, day_quantity or 0)
        daily_stats.append({
            'date': day.strftime('%Y-%m-%d'),
            'day_name': day.strftime('%a'),
            'donations': day_donations,
            'quantity': day_quantity or 0,
            'claims': day_claims
        })
    
    # Calculate percentages for chart (minimum 5% to show the bar)
    for stat in daily_stats:
        if max_donations > 0:
            donations_pct = (stat['donations'] / max_donations) * 100
            stat['donations_percent'] = max(donations_pct, 5) if stat['donations'] > 0 else 0
        else:
            stat['donations_percent'] = 0
        
        if max_quantity > 0:
            quantity_pct = (stat['quantity'] / max_quantity) * 100
            stat['quantity_percent'] = max(quantity_pct, 5) if stat['quantity'] > 0 else 0
        else:
            stat['quantity_percent'] = 0
    
    # Monthly statistics (last 6 months)
    try:
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_stats = db.session.query(
            db.func.strftime('%Y-%m', Donation.created_at).label('month'),
            db.func.count(Donation.id).label('donations'),
            db.func.sum(Donation.quantity).label('quantity')
        ).filter(
            Donation.created_at >= six_months_ago
        ).group_by('month').order_by('month').all()
    except Exception:
        monthly_stats = []
    
    # Request status breakdown
    pending_requests = FoodRequest.query.filter_by(status='pending').count()
    fulfilled_requests = FoodRequest.query.filter_by(status='fulfilled').count()
    cancelled_requests = FoodRequest.query.filter_by(status='cancelled').count()
    
    return render_template('admin_dashboard.html',
                         user=user,
                         total_donations=total_donations,
                         total_quantity=total_quantity,
                         total_receivers=total_receivers,
                         total_donors=total_donors,
                         today_donations=today_donations,
                         today_quantity=today_quantity,
                         today_claims=today_claims,
                         today_requests=today_requests,
                         today_completed=today_completed,
                         week_donations=week_donations,
                         week_quantity=week_quantity,
                         week_receivers=week_receivers,
                         available_donations=available_donations,
                         claimed_donations=claimed_donations,
                         completed_donations=completed_donations,
                         food_type_stats=food_type_stats,
                         recent_donations=recent_donations,
                         recent_requests=recent_requests,
                         top_donors=top_donors,
                         active_receivers=active_receivers,
                         daily_stats=daily_stats,
                         monthly_stats=monthly_stats,
                         pending_requests=pending_requests,
                         fulfilled_requests=fulfilled_requests,
                         cancelled_requests=cancelled_requests)

@app.route('/admin/badge/<int:user_id>')
@login_required
@role_required('admin')
def view_donor_badges(user_id):
    user = db.get_or_404(User, user_id)
    if user.user_type != 'donor':
        flash('This user is not a donor.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Get donor statistics
    total_donations = Donation.query.filter_by(donor_id=user.id).count()
    total_quantity = db.session.query(db.func.sum(Donation.quantity)).filter_by(donor_id=user.id).scalar() or 0
    completed_donations = Donation.query.filter_by(donor_id=user.id, status='completed').count()
    
    # Calculate badges
    badges = []
    if total_donations >= 1:
        badges.append({'name': 'First Donation', 'icon': '🥉', 'unlocked': True})
    if total_donations >= 5:
        badges.append({'name': 'Regular Donor', 'icon': '🥈', 'unlocked': True})
    if total_donations >= 10:
        badges.append({'name': 'Super Donor', 'icon': '🥇', 'unlocked': True})
    if total_quantity >= 100:
        badges.append({'name': 'Century Club', 'icon': '💯', 'unlocked': True})
    if total_quantity >= 500:
        badges.append({'name': 'Hero Donor', 'icon': '🌟', 'unlocked': True})
    if completed_donations >= 20:
        badges.append({'name': 'Impact Maker', 'icon': '🏆', 'unlocked': True})
    
    return render_template('donor_badges.html', user=user, badges=badges,
                         total_donations=total_donations,
                         total_quantity=total_quantity,
                         completed_donations=completed_donations)

if __name__ == '__main__':
    with app.app_context():
        # Create all tables first
        db.create_all()
        
        # Run migration to add unique_id column if it doesn't exist
        # Note: SQLite doesn't strictly enforce schema changes like this easily in raw SQL without migration tools,
        # but since we are modifying the model, we attempt to backfill.
        # Ideally, we would use Flask-Migrate. For this simple setup,
        # we assume the column exists (if recreate) or we hope sqlite accepts the model change if it was just created.
        # A robust way without tools is difficult. 
        # However, `db.create_all()` typically only creates missing tables, not missing columns.
        # We will try a manual column addition for safety if it fails.
        try:
            # Check if column exists by trying to select it. Rough check.
            db.session.execute(db.text('SELECT unique_id FROM user LIMIT 1'))
        except Exception:
            print("Adding unique_id column to user table...")
            try:
                db.session.execute(db.text('ALTER TABLE user ADD COLUMN unique_id VARCHAR(10)'))
                db.session.commit()
            except Exception as e:
                print(f"Column creation warning: {e}")

        # Check for admin
        if not User.query.filter_by(username='admin').first():
             # ... (admin creation code)
             pass 

        # Now backfill IDs
        backfill_unique_ids()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@foodredist.org',
                password=generate_password_hash('admin123'),
                user_type='admin',
                organization_name='Food Redistribution NGO'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)

