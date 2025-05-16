from app import create_app, db
from app.models import User, Team, Room, Booking
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time


app = create_app()

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    # Create new tables
    db.create_all()

    # Example teams
    team1 = Team(name="Development")
    team2 = Team(name="Marketing")
    db.session.add_all([team1, team2])
    db.session.commit()

    # Example users
    user1 = User(
        username="alice",
        fullname="Alice Smith",
        position="Developer",
        team_id=team1.id,
        password_hash=generate_password_hash("password123"),
    )
    user2 = User(
        username="bob",
        fullname="Bob Jones",
        position="Marketer",
        team_id=team2.id,
        password_hash=generate_password_hash("securepass"),
    )

    db.session.add_all([user1, user2])
    db.session.commit()

    # Example rooms
    room1 = Room(name="Room A", capacity=10, telephone="123-456-7890")
    room2 = Room(name="Room B", capacity=20, telephone="987-654-3210")
    db.session.add_all([room1, room2])
    db.session.commit()

    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("10:00", "%H:%M")
    duration = (end_time - start_time).seconds // 60  # duration in minutes

    # Optional: example booking
    booking = Booking(
        title="Team Sync",
        user_id=user1.id,
        room_id=room1.id,
        team_id=team1.id,
        date=date(2025, 5, 20),
        start_time=start_time,
        end_time=end_time,
        duration=duration
    )

    db.session.add(booking)
    db.session.commit()

    print("✅ Database successfully recreated and populated.")
