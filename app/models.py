from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login, db


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    fullname = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    position = db.Column(db.String(64), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    bookings_made = db.relationship('Booking', backref='booker', lazy='dynamic')
    participations = db.relationship('ParticipantsUser', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.position})>'


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    members = db.relationship('User', backref='team', lazy='dynamic')
    bookings = db.relationship('Booking', backref='team', lazy='dynamic')

    def __repr__(self):
        return f'<Team {self.name}>'


class BusinessPartner(db.Model):
    __tablename__ = 'business_partner'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    representing = db.Column(db.String(64), nullable=False)
    position = db.Column(db.String(64), nullable=False)

    participations = db.relationship('ParticipantsPartner', backref='partner', lazy='dynamic')

    def __repr__(self):
        return f'<BusinessPartner {self.name} ({self.representing})>'


class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    projector = db.Column(db.Boolean, nullable=True)
    whiteboard = db.Column(db.Boolean, nullable=True)
    cost = db.Column(db.Integer, nullable=True)

    bookings = db.relationship('Booking', backref='room', lazy='dynamic')

    def __repr__(self):
        return f'<Room {self.name}>'


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False, unique=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Booking {self.title} on {self.date.date()}>'


class CostLog(db.Model):
    __tablename__ = 'cost_log'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, nullable=False)
    team_name = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    cost = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<CostLog {self.title} - {self.cost}>'


class ParticipantsUser(db.Model):
    __tablename__ = 'participants_user'

    id = db.Column(db.Integer, primary_key=True)
    booking_title = db.Column(db.String(64), db.ForeignKey('booking.title'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<ParticipantsUser user_id={self.user_id} booking={self.booking_title}>'


class ParticipantsPartner(db.Model):
    __tablename__ = 'participants_partner'

    id = db.Column(db.Integer, primary_key=True)
    booking_title = db.Column(db.String(64), db.ForeignKey('booking.title'))
    partner_id = db.Column(db.Integer, db.ForeignKey('business_partner.id'))

    def __repr__(self):
        return f'<ParticipantsPartner partner_id={self.partner_id} booking={self.booking_title}>'
