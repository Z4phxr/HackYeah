from datetime import datetime
from app import db

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Temporarily remove user_id to fix the schema issue
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f'<Trip {self.destination}>'
    
    def duration_days(self):
        """Calculate trip duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def is_upcoming(self):
        """Check if trip is in the future"""
        from datetime import date
        return self.start_date > date.today()
    
    def is_current(self):
        """Check if trip is currently happening"""
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    def is_past(self):
        """Check if trip is in the past"""
        from datetime import date
        return self.end_date < date.today()
    
    def to_dict(self):
        """Convert trip object to dictionary"""
        return {
            'id': self.id,
            'destination': self.destination,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_days': self.duration_days(),
            'is_upcoming': self.is_upcoming(),
            'is_current': self.is_current(),
            'is_past': self.is_past()
        }
    


