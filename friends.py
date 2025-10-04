from datetime import datetime
from app import db

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    addressee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_requests')
    addressee = db.relationship('User', foreign_keys=[addressee_id], backref='received_requests')
    
    __table_args__ = (
        db.UniqueConstraint('requester_id', 'addressee_id', name='unique_friendship'),
    )
    
    def __repr__(self):
        return f'<Friendship {self.requester.username} -> {self.addressee.username} ({self.status})>'
    
    @staticmethod
    def get_friendship(user1_id, user2_id):
        """Get friendship between two users (regardless of who sent the request)"""
        return Friendship.query.filter(
            ((Friendship.requester_id == user1_id) & (Friendship.addressee_id == user2_id)) |
            ((Friendship.requester_id == user2_id) & (Friendship.addressee_id == user1_id))
        ).first()
    
    @staticmethod
    def are_friends(user1_id, user2_id):
        """Check if two users are friends"""
        friendship = Friendship.get_friendship(user1_id, user2_id)
        return friendship and friendship.status == 'accepted'
    
    @staticmethod
    def get_user_friends(user_id):
        """Get all friends of a user"""
        from users import User
        
        # Get all accepted friendships where user is either requester or addressee
        friendships = Friendship.query.filter(
            ((Friendship.requester_id == user_id) | (Friendship.addressee_id == user_id)) &
            (Friendship.status == 'accepted')
        ).all()
        
        friends = []
        for friendship in friendships:
            friend_id = friendship.addressee_id if friendship.requester_id == user_id else friendship.requester_id
            friend = User.query.get(friend_id)
            if friend:
                friends.append(friend)
        
        return friends
    
    @staticmethod
    def get_pending_requests(user_id):
        """Get all pending friend requests received by a user"""
        return Friendship.query.filter(
            (Friendship.addressee_id == user_id) & (Friendship.status == 'pending')
        ).all()
    
    @staticmethod
    def get_sent_requests(user_id):
        """Get all pending friend requests sent by a user"""
        return Friendship.query.filter(
            (Friendship.requester_id == user_id) & (Friendship.status == 'pending')
        ).all()
    
    def accept(self):
        """Accept the friend request"""
        self.status = 'accepted'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def decline(self):
        """Decline the friend request"""
        self.status = 'declined'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def block(self):
        """Block the user"""
        self.status = 'blocked'
        self.updated_at = datetime.utcnow()
        db.session.commit()
