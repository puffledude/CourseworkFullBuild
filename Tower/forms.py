from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user, login_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, SelectField, IntegerField
from wtforms.widgets import HiddenInput
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from Tower.models import User



class RegistrationForm(FlaskForm): #Form used for registration
    name= StringField("Name",
                          validators=[DataRequired(), Length(min=2, max=55)])

    phone_number=StringField("Phone Number",
                             validators=[DataRequired(), Length(min=8, max= 13)])

    email = StringField('Email', validators=[DataRequired(), Email()])

    role = SelectField("Role", coerce=str, choices=[("Tenant", "Tenant"), ("Landlord", "Landlord"),
                                                   ("Contractor", "Contractor"), ("Admin", "Admin")],
                       validators=[DataRequired()])

    business = StringField("Business Name (Only for Contractors)", validators=[Optional(),Length(max=170)])

    password = PasswordField('Password',
                             validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Create user')


    def validate_email(self, email): #Ensures the Email used is unique
    
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("The email entered is taken. Please choose a different one.")
    




class Update_User_Form(FlaskForm):


    name = StringField("Update Name",
                       validators=[DataRequired(), Length(min=2, max=55)])

    phone_number = StringField("Update Phone Number",
                               validators=[DataRequired(), Length(min=8, max= 13)])

    email = StringField('Update Email', validators=[Optional(), Email()])



    submit = SubmitField("Update User")

    def validate_email(self, email):  # Ensures the Email used is unique

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("The email entered is taken. Please choose a different one.")

class Update_Contractor_Form(FlaskForm):
    user_id = IntegerField(widget=HiddenInput())
    name = StringField("Name",
                       validators=[DataRequired(), Length(min=2, max=55)])

    phone_number = StringField("Phone Number",
                               validators=[DataRequired(), Length(min=8, max= 13)])

    business_name = StringField("Business Name", validators=[DataRequired(), Length(max=170)])

    email = StringField('Email', validators=[Optional(), Email()])

    submit = SubmitField("Update User")

    def validate_email(self, email):  # Ensures the Email used is unique

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("The email entered is taken. Please choose a different one.")


class Delete_Form(FlaskForm):
    submit = SubmitField("Delete")

class PropertiesForm(FlaskForm):

    address_line_1 = StringField("Address Line 1",
                                 validators=[DataRequired(), Length(min=2, max= 60)])
    address_line_2 = StringField("Address Line 2",
                                 validators=[Length(max=60)])
    postcode = StringField("Post code",
                           validators=[DataRequired(), Length(min=5, max=10)])
    Landlord = SelectField("Landlord", coerce=str)

    submit = SubmitField('Register property')

class Update_Properties_form(FlaskForm):
    address_line_1 = StringField("Address Line 1",
                                 validators=[DataRequired(), Length(min=2, max=60)])
    address_line_2 = StringField("Address Line 2",
                                 validators=[Length(max=60)])
    postcode = StringField("Post code",
                           validators=[DataRequired(), Length(min=5, max=10)])
    Landlord = SelectField("Landlord", coerce=str)

    submit = SubmitField('Update property')

#def edit_landlord(request, landlord_id):
    #landlord = landlords.query.get(landlord_id)
    #form = PropertiesForm(request.POST, obj=landlord)
    #form.Landlord.choices =[(g.landlord.id, g.forename+ " "+ g.surname)for g in Group.query.order_by("forename")]

class User_search_Form(FlaskForm):

    name = StringField("Name",
                           validators=[DataRequired(), Length(min=1, max=55)])

    submit = SubmitField("Search name")


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class IssueForm(FlaskForm):
    summary = StringField("Summary", validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField("Issue", validators=[DataRequired(), Length(min=2, max=500)])
    submit = SubmitField("Create Issue")


class New_tenancy_Form(FlaskForm):
    property = SelectField("Addresss", coerce=str)
    start_date = DateField("Start Date", format="%Y-%m-%d" ,validators=[DataRequired()])
    submit = SubmitField("Create Tenancy")
    
class Add_Tenant_Form(FlaskForm):
    Tenant = SelectField("Tenant", coerce=str)
    Tenancy = SelectField("Tenancy", coerce=str)
    submit = SubmitField("Add Tenant to Tenancy")


class Property_search_Form(FlaskForm):
    address_line_1 = StringField("Address", validators=[DataRequired(), Length(max=20)])
    submit = SubmitField("Search Property")

class note_form(FlaskForm):
    title= StringField("Title", validators=[DataRequired(), Length(max=100)])
    content = TextAreaField("Content", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Add note")


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):  # Ensures the Email used is unique

        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email.")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")

class Invite_Form(FlaskForm):
    contractor = SelectField("Contractor", coerce=str)
    submit = SubmitField("Invite contractor")

class Quote_Form(FlaskForm):
    content = TextAreaField("Quote details")
    submit = SubmitField("Give Quote")

class Approve_Form(FlaskForm):
    submit = SubmitField("Approve Quote")



# class UpdateAccountForm(FlaskForm):
#     username = StringField("Username",
#                            validators=[DataRequired(), Length(min=2, max=20)])
#
#     email = StringField('Email',
#                         validators=[DataRequired(), Email()])
#
#     picture = FileField("Update Profile Picture", validators=[FileAllowed(["jpg", "png"])])
#
#     submit = SubmitField('Update')
#
#     def validate_username(self, username):
#         if username.data != current_user.username:
#
#             user = User.query.filter_by(username=username.data).first()
#             if user:
#                 raise ValidationError("The username entered is taken. Please choose a different one.")
#
#     def validate_email(self, email):
#         if email.data != current_user.email:
#             user = User.query.filter_by(email=email.data).first()
#             if user:
#                 raise ValidationError("The email entered is taken. Please choose a different one.")
#
#
# class PostForm(FlaskForm):
#     title = StringField("Title", validators=[DataRequired()])
#     content = TextAreaField("Content", validators=[DataRequired()])
#     submit = SubmitField("Post")
