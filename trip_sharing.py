from datetime import datetime, timezone
from app import db

class TripSharing(db.Model):
    __tablename__ = 'trip_sharing'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission = db.Column(db.String(20), default='view')  # 'view' or 'edit'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'declined'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    trip = db.relationship('Trip', backref='shared_with')
    owner = db.relationship('User', foreign_keys=[owner_id], backref='trips_shared_by_me')
    shared_with = db.relationship('User', foreign_keys=[shared_with_id], backref='trips_shared_with_me')
    
    def __repr__(self):
        return f"<TripSharing {self.trip_id} shared by {self.owner_id} with {self.shared_with_id}>"
    
    @staticmethod
    def get_shared_trip(trip_id, user_id):
        """Check if a trip is shared with a user"""
        return TripSharing.query.filter_by(
            trip_id=trip_id, 
            shared_with_id=user_id, 
            status='accepted'
        ).first()
    
    @staticmethod
    def get_user_shared_trips(user_id):
        """Get all trips shared with a user"""
        return TripSharing.query.filter_by(
            shared_with_id=user_id, 
            status='accepted'
        ).all()
    
    @staticmethod
    def get_pending_invitations(user_id):
        """Get pending trip invitations for a user"""
        return TripSharing.query.filter_by(
            shared_with_id=user_id, 
            status='pending'
        ).all()
    
    def accept(self):
        """Accept trip sharing invitation"""
        self.status = 'accepted'
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def decline(self):
        """Decline trip sharing invitation"""
        self.status = 'declined'
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
