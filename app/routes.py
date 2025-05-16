from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from flask import current_app as app
from datetime import datetime

from urllib.parse import urlparse as url_parse
from app.forms import (
    RegistrationForm,
    LoginForm,
    AddUserForm,
    AddTeamForm,
    DeleteTeamForm,
    DeleteUserForm,
    BookMeetingForm,
    CancelBookingForm,
    RoomAvailableForm,
    RoomOccupationForm,
    MeetingParticipantsForm,
    CostAccruedForm,
)
from app.models import (
    Team,
    Booking,
    Room,
    User,
    CostLog,
    ParticipantsUser,
    ParticipantsPartner,
    BusinessPartner,
)

bp = Blueprint("main", __name__)

@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            fullname=form.fullname.data,
            position=form.position.data,
            teamId=form.teamId.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        team = Team.query.filter_by(id=user.teamId).first()
        if team is None:
            newTeam = Team(id=user.teamId, teamName=form.teamName.data)
            db.session.add(newTeam)
            db.session.commit()
            flash("Registered with a new team created")
            return redirect(url_for("login"))
        else:
            db.session.commit()
            flash("Registered to an existing team")
            return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@bp.route("/adduser", methods=["GET", "POST"])
@login_required
def adduser():
    if not current_user.is_authenticated:
        flash("Please Log in as admin to add user")
        return redirect(url_for("login"))
    if current_user.username != "admin":
        flash("Please Log in as admin to add user")
        return redirect(url_for("index"))
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            fullname=form.fullname.data,
            position=form.position.data,
            teamId=form.teamId.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        team = Team.query.filter_by(id=user.teamId).first()
        if team is None:
            newTeam = Team(id=user.teamId, teamName=form.teamName.data)
            db.session.add(newTeam)
            db.session.commit()
            flash(f"Added user {form.username.data} with a new team created")
            return redirect(url_for("adduser"))
        else:
            db.session.commit()
            flash(f"Added user {form.username.data} to an existing team")
            return redirect(url_for("adduser"))
    return render_template("adduser.html", title="Add User", form=form)


@bp.route("/addteam", methods=["GET", "POST"])
@login_required
def addteam():
    if not current_user.is_authenticated:
        flash("Please Log in as admin to add team")
        return redirect(url_for("login"))
    if current_user.username != "admin":
        flash("Please Log in as admin to add team")
        return redirect(url_for("index"))
    form = AddTeamForm()
    if form.validate_on_submit():
        team = Team(id=form.id.data, teamName=form.teamName.data)
        db.session.add(team)
        db.session.commit()
        flash(f"Team {form.teamName.data} successfully added!")
        return redirect(url_for("addteam"))
    return render_template("addteam.html", title="Add Team", form=form)


@bp.route("/deleteteam", methods=["GET", "POST"])
@login_required
def deleteteam():
    if not current_user.is_authenticated:
        flash("Please Log in as admin to delete team")
        return redirect(url_for("login"))
    if current_user.username != "admin":
        flash("Please Log in as admin to delete team")
        return redirect(url_for("index"))
    form = DeleteTeamForm()

    if form.validate_on_submit():
        team = Team.query.filter_by(id=form.ids.data).first()

        bookings = Booking.query.filter_by(teamId=team.id).all()
        has_future_booking = False
        for booking in bookings:
            if booking.date > datetime.now():
                has_future_booking = True
                break
        if has_future_booking:
            flash("You cannot delete a team that holds future bookings!")
            return redirect(url_for("deleteteam"))

        # delete all users in a deleted team
        userInTeam = User.query.filter_by(teamId=form.ids.data).all()
        for user in userInTeam:
            db.session.delete(user)
        db.session.delete(team)
        db.session.commit()
        flash(
            f"Team {team.teamName} and team members successfully deleted! Please register member again to other team"
        )
        return redirect(url_for("index"))
    form = DeleteTeamForm()
    return render_template("deleteteam.html", title="Delete Team", form=form)


@bp.route("/deleteuser", methods=["GET", "POST"])
@login_required
def deleteuser():
    if not current_user.is_authenticated:
        flash("Please Log in as admin to delete user")
        return redirect(url_for("login"))
    if current_user.username != "admin":
        flash("Please Log in as admin to delete user")
        return redirect(url_for("index"))

    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.ids.data).first()

        bookings = Booking.query.filter_by(bookerId=user.id).all()
        has_future_booking = False
        for booking in bookings:
            if booking.date > datetime.now():
                has_future_booking = True
                break
        if has_future_booking:
            flash("You cannot delete a user that holds future bookings!")
            return redirect(url_for("deleteuser"))

        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} successfully deleted! ")
        return redirect(url_for("index"))
    return render_template("deleteuser.html", title="Delete User", form=form)


@bp.route("/book", methods=["GET", "POST"])
@login_required
def book():
    form = BookMeetingForm()
    if form.validate_on_submit():
        # check time collision
        bookingcollisions = (
            Booking.query.filter_by(
                date=datetime.combine(form.date.data, datetime.min.time())
            )
            .filter_by(roomId=form.rooms.data)
            .all()
        )
        print(len(bookingcollisions))
        for bookingcollision in bookingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if (
                form.startTime.data < bookingcollision.endTime
                and (form.startTime.data + form.duration.data)
                > bookingcollision.startTime
            ):
                flash(
                    f"The time from {bookingcollision.startTime} to {bookingcollision.endTime} is already booked by {User.query.filter_by(id=bookingcollision.bookerId).first().fullname}."
                )
                return redirect(url_for("book"))

        # make booking
        booker = current_user

        team = Team.query.filter_by(id=current_user.teamId).first()
        room = Room.query.filter_by(id=form.rooms.data).first()
        cost = room.cost
        endTime = form.startTime.data + form.duration.data

        participants_user = form.participants_user.data
        participants_partner = form.participants_partner.data

        booking = Booking(
            title=form.title.data,
            teamId=team.id,
            roomId=room.id,
            bookerId=booker.id,
            date=form.date.data,
            startTime=form.startTime.data,
            endTime=endTime,
            duration=form.duration.data,
        )
        db.session.add(booking)

        # Add booking log
        log = CostLog(
            title=form.title.data,
            teamId=team.id,
            teamName=team.teamName,
            date=form.date.data,
            cost=cost * form.duration.data,
        )
        db.session.add(log)

        # Add participants records
        for participant in participants_user:
            participating = ParticipantsUser(
                meeting=form.title.data, userId=participant
            )
            db.session.add(participating)
        for participant in participants_partner:
            participating = ParticipantsPartner(
                meeting=form.title.data, partnerId=participant
            )
            db.session.add(participating)

        db.session.commit()
        flash("Booking success!")
        return redirect(url_for("index"))
    return render_template("book.html", title="Book Meeting", form=form)


@bp.route("/cancelbooking", methods=["GET", "POST"])
@login_required
def cancelbooking():
    if not current_user.is_authenticated:
        flash("Please Log in to cancel booking")
        return redirect(url_for("login"))

    form = CancelBookingForm()
    if form.validate_on_submit():
        booking = Booking.query.filter_by(id=form.ids.data).first()

        if booking.date <= datetime.now():
            flash("Past booking cannot be canceled")
            return redirect(url_for("cancelbooking"))

        participants_user = ParticipantsUser.query.filter_by(
            meeting=booking.title
        ).all()
        for part in participants_user:
            db.session.delete(part)
        participants_partner = ParticipantsPartner.query.filter_by(
            meeting=booking.title
        ).all()
        for part in participants_partner:
            db.session.delete(part)

        costlog = CostLog.query.filter_by(title=booking.title).first()
        db.session.delete(costlog)

        db.session.delete(booking)
        db.session.commit()
        flash(f"Meeting {booking.title} successfully deleted! ")
        return redirect(url_for("index"))
    return render_template("cancelbooking.html", title="Cancel Booking", form=form)


@bp.route("/roomavailable", methods=["GET", "POST"])
def roomavailable():
    form = RoomAvailableForm()
    if form.validate_on_submit():
        bookings = Booking.query.filter_by(
            date=datetime.combine(form.date.data, datetime.min.time())
        ).all()
        roomsOccupied = set()
        for booking in bookings:
            if (
                form.startTime.data < booking.endTime
                and (form.startTime.data + form.duration.data) > booking.startTime
            ):
                roomsOccupied.add(Room.query.filter_by(id=booking.roomId).first())
        rooms = Room.query.all()
        roomsavailable = []
        for room in rooms:
            if room not in roomsOccupied:
                roomsavailable.append(room)
        return render_template(
            "roomavailablelist.html", title="Room available", rooms=roomsavailable
        )
    return render_template(
        "roomavailable.html", title="Room availability check", form=form
    )


@bp.route("/roomoccupation", methods=["GET", "POST"])
def roomoccupation():
    form = RoomOccupationForm()
    if form.validate_on_submit():
        # meetings=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
        roomoccus = []
        hours = range(9, 23)
        rooms = Room.query.all()
        allrooms = []
        for room in rooms:
            roomoccu = dict()
            roomoccu["roomName"] = room.roomName
            roomoccu["roomhours"] = [False] * 14
            for hour in hours:
                bookings = (
                    Booking.query.filter_by(
                        date=datetime.combine(form.date.data, datetime.min.time())
                    )
                    .filter_by(roomId=room.id)
                    .all()
                )

                for booking in bookings:
                    if (hour + 0.5) < booking.endTime and (
                        hour + 0.5
                    ) > booking.startTime:
                        roomoccu["roomhours"][hour - 9] = True
                        break
            roomoccus.append(roomoccu)

            allrooms.append(
                {
                    "roomName": room.roomName,
                    "tel": "Yes" if room.telephone else "No",
                    "pro": "Yes" if room.projector else "No",
                    "wb": "Yes" if room.whiteboard else "No",
                    "cost": room.cost,
                }
            )
        return render_template(
            "roomoccupationlist.html",
            title="Room Occupation",
            roomoccus=roomoccus,
            date=form.date.data,
            hours=[str(hour) for hour in hours],
            allrooms=allrooms,
        )
    return render_template(
        "roomoccupation.html", title="Room Occupation Status", form=form
    )


@bp.route("/meetingbooker")
def meetingbooker():
    bookings = Booking.query.order_by(Booking.date).all()
    bookingreturns = []
    for booking in bookings:
        bookingreturn = dict()
        bookingreturn["title"] = booking.title
        bookingreturn["team"] = Team.query.filter_by(id=booking.teamId).first().teamName
        bookingreturn["room"] = Room.query.filter_by(id=booking.roomId).first().roomName
        bookingreturn["booker"] = (
            User.query.filter_by(id=booking.bookerId).first().fullname
        )
        bookingreturn["date"] = booking.date.date()
        bookingreturn["time"] = f"{booking.startTime} to {booking.endTime}"
        bookingreturns.append(bookingreturn)
    return render_template("meetingbooker.html", meetings=bookingreturns)


@bp.route("/meetingparticipants", methods=["GET", "POST"])
def meetingparticipants():
    form = MeetingParticipantsForm()
    if form.validate_on_submit():
        booking = Booking.query.filter_by(id=form.ids.data).first()
        participants = []
        participants_user = ParticipantsUser.query.filter_by(
            meeting=booking.title
        ).all()
        participants_partner = ParticipantsPartner.query.filter_by(
            meeting=booking.title
        ).all()
        for part in participants_user:
            participants.append(
                f"{User.query.filter_by(id=part.userId).first().fullname} from {Team.query.filter_by(id=User.query.filter_by(id=part.userId).first().teamId).first().teamName}"
            )
        for part in participants_partner:
            participants.append(
                f"partner {BusinessPartner.query.filter_by(id=part.partnerId).first().name} from {BusinessPartner.query.filter_by(id=part.partnerId).first().representing}"
            )
        return render_template(
            "meetingparticipants.html",
            title="Meeting Participants",
            meetingtitle=booking.title,
            participants=participants,
        )
    return render_template(
        "meetingparticipantscheck.html", title="Booking Participants", form=form
    )


@bp.route("/costs", methods=["GET", "POST"])
def costs():
    form = CostAccruedForm()
    if form.validate_on_submit():
        costlogs = (
            CostLog.query.filter(
                CostLog.date
                >= datetime.combine(form.startdate.data, datetime.min.time())
            )
            .filter(
                CostLog.date <= datetime.combine(form.enddate.data, datetime.min.time())
            )
            .all()
        )
        teams = list(set([costlog.teamName for costlog in costlogs]))
        teamcosts = []
        # slow implementation, can be optimized
        for team in teams:
            teamcost = dict()
            teamcost["teamName"] = team
            teamcost["total"] = 0
            for costlog in costlogs:
                if costlog.teamName == team:
                    teamcost["total"] += costlog.cost
            teamcosts.append(teamcost)
        return render_template(
            "costs.html",
            title="Cost Accrued",
            startdate=form.startdate.data,
            enddate=form.enddate.data,
            teamcosts=teamcosts,
        )
    return render_template("costcheck.html", title="Cost Accrued check", form=form)
