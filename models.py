from datetime import datetime, timezone
from app import db

class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # relacje do "dzieci" - ordered by creation sequence
    accommodations = db.relationship('Accomodation', back_populates="trip", cascade="all, delete-orphan", lazy="selectin", order_by="Accomodation.order_index")
    travels = db.relationship('Travel', back_populates="trip", cascade="all, delete-orphan", lazy="selectin", order_by="Travel.order_index")
    
    # Relationship to User
    user = db.relationship('User', backref='trips')

    def __repr__(self):
        return f"<Trip {self.id}->{self.destination} {self.start_date} {self.end_date}>"
    
    def get_all_items_ordered(self):
        """Get all accommodations and travels in the order they were added"""
        items = []
        
        # Add accommodations with type indicator
        for acc in self.accommodations:
            items.append({
                'type': 'accommodation',
                'order_index': acc.order_index,
                'item': acc
            })
        
        # Add travels with type indicator
        for travel in self.travels:
            items.append({
                'type': 'travel',
                'order_index': travel.order_index,
                'item': travel
            })
        
        # Sort by order_index to maintain creation order
        items.sort(key=lambda x: x['order_index'])
        return items

class Accomodation(db.Model):
    __tablename__ = 'accommodations'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    standard = db.Column(db.String(50))
    link = db.Column(db.String(500))
    order_index = db.Column(db.Integer, nullable=False, default=0)
    trip = db.relationship('Trip', back_populates='accommodations')

    def __repr__(self):
        return f"<Accomodation {self.id} {self.location} {self.check_in} - {self.check_out}>"

class Travel(db.Model):
    __tablename__ = 'travels'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    trip = db.relationship('Trip', back_populates='travels')

    def __repr__(self):
        return f"<Travel {self.id} {self.from_location} -> {self.to_location}>"
