from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .Branch import db, login_manager , app
from flask_login import UserMixin
from datetime import datetime


# These are the models corresponding tables in the database. These are used to create tables and used by the ORM
# SQLAlchmey uses.


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


occupants = db.Table("occupants",
                     db.Column("user_id", db.Integer, db.ForeignKey("user.user_id")),  # Helper table used for the many to many relationship
                     db.Column("tenancy_id", db.Integer, db.ForeignKey("tenancies.tenancy_id")))


class User(db.Model, UserMixin):  # User table
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(55), nullable=False)
    phone_number= db.Column(db.String(15), nullable=False)
    role= db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    business= db.Column(db.String(150), nullable=True)
    password = db.Column(db.String(64), nullable=False)
    properties = db.relationship("Properties",cascade="all, delete-orphan" ,backref="User", lazy=True)
    # The cascades determine that if the user is deleted, all data related to them (i.e any properties linked to them)
    # will also be deletedd
    occupants = db.relationship("Tenancies", backref="User", secondary=occupants, lazy=True)
    contractor = db.relationship("Quotes", cascade="all, delete-orphan",backref="User", lazy=True)

    def get_reset_token(self, expires_sec=1800):  # Creates a user token for password recovery
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.user_id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):  # Verifies user token for password recovery
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.name}', '{self.phone_number}', '{self.role}', '{self.email}')"

    def get_id(self):
        return (self.user_id)

class Properties(db.Model):  # Properties table
    property_id = db.Column(db.Integer, primary_key=True)
    address_line_1 = db.Column(db.String(35), nullable=False)
    address_line_2 = db.Column(db.String(20), nullable=True, default=" ")
    postcode = db.Column(db.String(10), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    issue = db.relationship("Issue",cascade="all, delete-orphan", backref="Properties", lazy=True)

    def __repr__(self):
        return f"Properties(f'{self.address_line_1}', '{self.address_line_2}', '{self.postcode}')"



class Tenancies(db.Model):  # Tenancies table
    tenancy_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.property_id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    occupants = db.relationship("User", backref="Tenancies", secondary=occupants, lazy=True)

    def __repr__(self):
        return f"Tenancies(f' {self.start_date}')"

class Issue(db.Model):  # Issue table
    issue_id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    opened = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    closed = db.Column(db.Boolean, default=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.property_id"), nullable=False)
    jobs = db.relationship("Jobs", backref="Issue", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("Issue_Notes", backref="Issue", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Issue(f'{self.summary}', '{self.closed}')"

class Issue_Notes(db.Model):  # notes for issues table
    note_id = db.Column(db.Integer, primary_key=True)
    issue = db.Column(db.Integer, db.ForeignKey("issue.issue_id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    post_time = db.Column(db.DateTime, default=datetime.utcnow)

class Jobs(db.Model):  # Jobs table
    job_id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    opened = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    closed = db.Column(db.Boolean, default=False)
    issue = db.Column(db.Integer, db.ForeignKey("issue.issue_id"), nullable=False)
    quotes = db.relationship("Quotes", backref="Jobs", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("Jobs_Notes", backref="Jobs", lazy=True, cascade="all, delete-orphan")

class Jobs_Notes(db.Model):  # Notes for Jobs table
    note_id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.Integer, db.ForeignKey("jobs.job_id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    post_time = db.Column(db.DateTime, default=datetime.utcnow)


class Quotes(db.Model):  # Quotes for jobs table
    quote_id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.String(500), nullable=False)
    chosen = db.Column(db.Boolean, default=False)
    job = db.Column(db.Integer, db.ForeignKey("jobs.job_id"), nullable=False)
    contractor = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
