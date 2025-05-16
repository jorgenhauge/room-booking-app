from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    IntegerField,
    SelectField,
    DateField,
    SelectMultipleField,
    widgets,
)
from wtforms.validators import ValidationError, DataRequired, EqualTo
from flask_login import current_user
from app.models import Team, Booking, Room, BusinessPartner, User
import datetime


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Password", validators=[DataRequired(), EqualTo("password")])
    fullname = StringField("Full Name", validators=[DataRequired()])
    position = StringField("Position", validators=[DataRequired()])
    team_id = IntegerField("Team number", validators=[DataRequired()])
    team_name = StringField("Team name", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_team_id(self, team_id):
        team = Team.query.filter_by(id=team_id.data).first()
        if team is not None and team.name != self.team_name.data:
            raise ValidationError("Team name does not match, try again.")


class AddTeamForm(FlaskForm):
    id = IntegerField("Team number", validators=[DataRequired()])
    name = StringField("Team name", validators=[DataRequired()])
    submit = SubmitField("Add")

    def validate_id(self, id):
        if Team.query.filter_by(id=id.data).first():
            raise ValidationError("Team exists, try again")

    def validate_name(self, name):
        if Team.query.filter_by(name=name.data).first():
            raise ValidationError("Team name exists, try again")


class AddUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    fullname = StringField("Full Name", validators=[DataRequired()])
    position = StringField("Position", validators=[DataRequired()])
    team_id = IntegerField("Team number", validators=[DataRequired()])
    team_name = StringField("Team name", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        if User.query.filter_by(username=self.username.data).first():
            raise ValidationError("Please use a different username.")

    def validate_team_id(self, team_id):
        team = Team.query.filter_by(id=team_id.data).first()
        if team is not None and team.name != self.team_name.data:
            raise ValidationError("Team name does not match, try again.")


class TeamChoiceIterable:
    def __iter__(self):
        teams = Team.query.filter(Team.name != "Admin").all()
        return iter([(team.id, team.name) for team in teams])


class DeleteTeamForm(FlaskForm):
    ids = SelectField("Choose Team", choices=TeamChoiceIterable(), coerce=int)
    submit = SubmitField("Delete")


class UserChoiceIterable:
    def __iter__(self):
        users = User.query.all()
        choices = [
            (user.id, f"{user.fullname}, team {user.team.name}")
            for user in users
            if "admin" not in user.username.lower()
        ]
        return iter(choices)


class PartnerChoiceIterable:
    def __iter__(self):
        partners = BusinessPartner.query.all()
        return iter([(partner.id, f"{partner.name} from {partner.representing}") for partner in partners])


class DeleteUserForm(FlaskForm):
    ids = SelectField("Choose User", coerce=int, choices=UserChoiceIterable())
    submit = SubmitField("Delete")


class RoomChoiceIterable:
    def __iter__(self):
        rooms = Room.query.all()
        return iter([(room.id, room.name) for room in rooms])


class BookMeetingForm(FlaskForm):
    title = StringField("Meeting title", validators=[DataRequired()])
    room_id = SelectField("Choose room", coerce=int, choices=RoomChoiceIterable())
    date = DateField("Choose date", format="%m/%d/%Y", validators=[DataRequired()])
    start_time = SelectField("Choose starting time", coerce=int, choices=[(i, i) for i in range(9, 19)])
    duration = SelectField("Choose duration", coerce=int, choices=[(i, i) for i in range(1, 6)])
    participants_user = SelectMultipleField(
        "Company Participants",
        coerce=int,
        choices=UserChoiceIterable(),
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[DataRequired()],
    )
    participants_partner = SelectMultipleField(
        "Partner Participants",
        coerce=int,
        choices=PartnerChoiceIterable(),
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )
    submit = SubmitField("Book")

    def validate_title(self, title):
        if Booking.query.filter_by(title=self.title.data).first():
            raise ValidationError("Please use another meeting title.")

    def validate_date(self, date):
        if self.date.data < datetime.date.today():
            raise ValidationError("You can only book for a day after today.")


class MeetingChoiceIterable:
    def __iter__(self):
        bookings = Booking.query.filter_by(booker_id=current_user.id).all()
        return iter([
            (b.id, f"{b.title} in {b.room.name} on {b.date.date()} from {b.start_time}")
            for b in bookings
        ])


class CancelBookingForm(FlaskForm):
    ids = SelectField("Choose meeting to cancel", coerce=int, choices=MeetingChoiceIterable())
    submit = SubmitField("Cancel")


class RoomAvailableForm(FlaskForm):
    date = DateField("Choose date", format="%m/%d/%Y", validators=[DataRequired()])
    start_time = SelectField("Choose starting time", coerce=int, choices=[(i, i) for i in range(9, 19)])
    duration = SelectField("Choose duration", coerce=int, choices=[(i, i) for i in range(1, 6)])
    submit = SubmitField("Check")


class RoomOccupationForm(FlaskForm):
    date = DateField("Choose date", format="%m/%d/%Y", validators=[DataRequired()])
    submit = SubmitField("Check")


class MeetingChoiceAllIterable:
    def __iter__(self):
        bookings = Booking.query.all()
        return iter([
            (b.id, f"{b.title} in {b.room.name} on {b.date.date()} from {b.start_time}")
            for b in bookings
        ])


class MeetingParticipantsForm(FlaskForm):
    ids = SelectField("Choose meeting", coerce=int, choices=MeetingChoiceAllIterable())
    submit = SubmitField("Check")


class CostAccruedForm(FlaskForm):
    start_date = DateField("Start Date", format="%m/%d/%Y", validators=[DataRequired()])
    end_date = DateField("End Date", format="%m/%d/%Y", validators=[DataRequired()])
    submit = SubmitField("Check")

    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data:
            raise ValidationError("End Date must be after Start Date")
