from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from models import Trip
from users import User
from friends import Friendship

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    if current_user.is_authenticated:
        trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.desc()).all()
    else:
        trips = []
    return render_template('index.html', trips=trips)

@main_bp.route('/add_trip', methods=['GET', 'POST'])
@login_required
def add_trip():
    if request.method == 'POST':
        destination = request.form['destination']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        description = request.form['description']

        if start_date > end_date:
            flash('End date cannot be earlier than start date!', 'error')
            return render_template('add_trip.html')

        trip = Trip(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            description=description,
            user_id=current_user.id
        )

        db.session.add(trip)
        db.session.commit()
        flash('Trip added successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('add_trip.html')

@main_bp.route('/trip/<int:id>')
@login_required
def trip_detail(id):
    trip = Trip.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('trip_detail.html', trip=trip)

@main_bp.route('/delete_trip/<int:id>')
@login_required
def delete_trip(id):
    trip = Trip.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(trip)
    db.session.commit()
    flash('Trip deleted!', 'success')
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
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username/email or password.', 'error')
    
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
            flash('Passwords are not identical!', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email is already registered!', 'error')
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
        
        flash('Registration completed successfully! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/debug/database')
def debug_database():
    """Route to display all objects from the database"""
    from flask import jsonify
    
    # Get all trips
    trips = Trip.query.all()
    users = User.query.all()
    friendships = Friendship.query.all()
    
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
    
    friendships_data = []
    for friendship in friendships:
        friendships_data.append({
            'id': friendship.id,
            'requester_id': friendship.requester_id,
            'requester_name': friendship.requester.full_name if friendship.requester else 'Unknown',
            'addressee_id': friendship.addressee_id,
            'addressee_name': friendship.addressee.full_name if friendship.addressee else 'Unknown',
            'status': friendship.status,
            'created_at': friendship.created_at.strftime('%Y-%m-%d %H:%M:%S') if friendship.created_at else None,
            'updated_at': friendship.updated_at.strftime('%Y-%m-%d %H:%M:%S') if friendship.updated_at else None
        })
    
    return jsonify({
        'trips': {
            'count': len(trips_data),
            'data': trips_data
        },
        'users': {
            'count': len(users_data),
            'data': users_data
        },
        'friendships': {
            'count': len(friendships_data),
            'data': friendships_data
        }
    })

@main_bp.route('/debug/view')
def debug_view():
    """Route to display database contents in a readable web page"""
    trips = Trip.query.all()
    users = User.query.all()
    friendships = Friendship.query.all()
    
    return render_template('debug.html', 
                         trips=trips, 
                         users=users, 
                         friendships=friendships)


@main_bp.route('/friends')
@login_required
def friends():
    # Get user's friends
    user_friends = Friendship.get_user_friends(current_user.id)
    
    # Get pending requests (received)
    pending_requests = Friendship.get_pending_requests(current_user.id)
    
    # Get sent requests
    sent_requests = Friendship.get_sent_requests(current_user.id)
    
    return render_template('friends.html', 
                         friends=user_friends,
                         pending_requests=pending_requests,
                         sent_requests=sent_requests)

@main_bp.route('/send_friend_request', methods=['POST'])
@login_required
def send_friend_request():
    email = request.form.get('email', '').strip()
    
    if not email:
        flash('Please enter an email address.', 'error')
        return redirect(url_for('main.friends'))
    
    # Check if user exists
    target_user = User.query.filter_by(email=email).first()
    if not target_user:
        flash('No user found with that email address.', 'error')
        return redirect(url_for('main.friends'))
    
    # Check if trying to add themselves
    if target_user.id == current_user.id:
        flash('You cannot send a friend request to yourself.', 'error')
        return redirect(url_for('main.friends'))
    
    # Check if friendship already exists
    existing_friendship = Friendship.get_friendship(current_user.id, target_user.id)
    if existing_friendship:
        if existing_friendship.status == 'accepted':
            flash(f'You are already friends with {target_user.full_name}.', 'info')
        elif existing_friendship.status == 'pending':
            if existing_friendship.requester_id == current_user.id:
                flash(f'You already sent a friend request to {target_user.full_name}.', 'info')
            else:
                flash(f'{target_user.full_name} already sent you a friend request. Check your pending requests.', 'info')
        elif existing_friendship.status == 'blocked':
            flash('Unable to send friend request.', 'error')
        return redirect(url_for('main.friends'))
    
    # Create new friendship request
    friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=target_user.id,
        status='pending'
    )
    
    db.session.add(friendship)
    db.session.commit()
    
    flash(f'Friend request sent to {target_user.full_name}!', 'success')
    return redirect(url_for('main.friends'))

@main_bp.route('/respond_friend_request/<int:friendship_id>/<action>')
@login_required
def respond_friend_request(friendship_id, action):
    friendship = Friendship.query.get_or_404(friendship_id)
    
    # Check if current user is the addressee
    if friendship.addressee_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('main.friends'))
    
    if action == 'accept':
        friendship.accept()
        flash(f'You are now friends with {friendship.requester.full_name}!', 'success')
    elif action == 'decline':
        friendship.decline()
        flash(f'Friend request from {friendship.requester.full_name} declined.', 'info')
    else:
        flash('Invalid action.', 'error')
    
    return redirect(url_for('main.friends'))

@main_bp.route('/remove_friend/<int:user_id>')
@login_required
def remove_friend(user_id):
    friendship = Friendship.get_friendship(current_user.id, user_id)
    
    if not friendship or friendship.status != 'accepted':
        flash('This user is not your friend.', 'error')
        return redirect(url_for('main.friends'))
    
    # Remove the friendship
    db.session.delete(friendship)
    db.session.commit()
    
    flash('Friend removed.', 'info')
    return redirect(url_for('main.friends'))