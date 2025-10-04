from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app import db
from models import Trip

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
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