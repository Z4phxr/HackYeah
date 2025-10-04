from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from models import Trip
from users import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    trips = Trip.query.order_by(Trip.start_date.desc()).all()
    return render_template('index.html', trips=trips)

@main_bp.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    if request.method == 'POST':
        destination = request.form['destination']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        description = request.form['description']

        if start_date > end_date:
            flash('Data końcowa nie może być wcześniejsza niż data początkowa!', 'error')
            return render_template('add_trip.html')

        trip = Trip(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            description=description
        )

        db.session.add(trip)
        db.session.commit()
        flash('Podróż została dodana pomyślnie!', 'success')
        return redirect(url_for('main.index'))

    return render_template('add_trip.html')

@main_bp.route('/trip/<int:id>')
def trip_detail(id):
    trip = Trip.query.get_or_404(id)
    return render_template('trip_detail.html', trip=trip)

@main_bp.route('/delete_trip/<int:id>')
def delete_trip(id):
    trip = Trip.query.get_or_404(id)
    db.session.delete(trip)
    db.session.commit()
    flash('Podróż została usunięta!', 'success')
    return redirect(url_for('main.index'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Zalogowano pomyślnie!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Nieprawidłowa nazwa użytkownika/email lub hasło.', 'error')
    
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        # Validation
        if password != password_confirm:
            flash('Hasła nie są identyczne!', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Nazwa użytkownika już istnieje!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email już jest zarejestrowany!', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Rejestracja zakończona pomyślnie! Możesz się teraz zalogować.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/debug/database')
def debug_database():
    """Route do wyświetlania wszystkich obiektów z bazy danych"""
    from flask import jsonify
    
    # Pobierz wszystkie podróże
    trips = Trip.query.all()
    users = User.query.all()
    
    trips_data = []
    for trip in trips:
        trips_data.append({
            'id': trip.id,
            'destination': trip.destination,
            'start_date': trip.start_date.strftime('%Y-%m-%d') if trip.start_date else None,
            'end_date': trip.end_date.strftime('%Y-%m-%d') if trip.end_date else None,
            'description': trip.description,
            'created_at': trip.created_at.strftime('%Y-%m-%d %H:%M:%S') if trip.created_at else None
        })
    
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
            'is_active': user.is_active
        })
    
    return jsonify({
        'trips': {
            'count': len(trips_data),
            'data': trips_data
        },
        'users': {
            'count': len(users_data),
            'data': users_data
        }
    })