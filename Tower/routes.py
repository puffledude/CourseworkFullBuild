from Tower import app, bcrypt, mail
from .Branch import db, login_manager
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from Tower.models import User, Properties, Tenancies, Issue, Issue_Notes, Jobs, Jobs_Notes, Quotes
from Tower.forms import RegistrationForm, PropertiesForm, User_search_Form, LoginForm, IssueForm, New_tenancy_Form, \
    Property_search_Form, Add_Tenant_Form, Update_User_Form, Update_Contractor_Form, note_form, Update_Properties_form, \
    Delete_Form, RequestResetForm, ResetPasswordForm, Invite_Form, Quote_Form, Approve_Form, Close_Form
from flask_mail import Message


@app.route("/")
@app.route("/home")  # Home page for the web app
def home():
    return render_template("home.html")


@app.errorhandler(404) #If a 404 error is triggered
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(403) #IF a 403 error is triggered
def unauthorised(e):
    return render_template("403.html")


@app.route("/about")  # About Page
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])  # Register user page.
@login_required
def register():
    if current_user.role != "Admin":
        abort(403)
    form = RegistrationForm()  # Loads registration form from forms
    if form.validate_on_submit():  # Checks if the form is valid
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(name=form.name.data, phone_number=form.phone_number.data, email=form.email.data,
                    role=form.role.data, business=form.business.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()  # Commits new entry to the database
        flash("The account has been created!", "success")
        msg = Message("Registration", sender="noreply@Towercoursework.com", recipients=[user.email])
        msg.body = f''' Dear {user.name}
        You have been successfully registered to the Tower Estates online management system.
With this you can register any issues you have with your property'''  # Body of email
        mail.send(msg)  # Sends email
        return redirect(url_for("home"))

    return render_template("register.html", title="Register", form=form)  # Renders template for the user


@app.route("/new_property", methods=["GET", "POST"])  # Adds a new property to the database
@login_required
def new_property():
    if current_user.role != ("Admin"):  # Ensures only admins can use this route
        abort(403)  # Redirects to a 403 error
    landlords = db.session.query(User).filter(User.role == "Landlord")
    form = PropertiesForm()
    landlord_list = [(i.user_id, i.name) for i in landlords]
    form.Landlord.choices = landlord_list  # Fills in the landlord choices box
    if form.validate_on_submit():
        property = Properties(address_line_1=form.address_line_1.data, address_line_2=form.address_line_2.data,
                              postcode=form.postcode.data, landlord_id=form.Landlord.data)
        db.session.add(property)
        db.session.commit()
        flash("The property has been added!", "success")
        return redirect(url_for("home"))  # Redirects to home
    return render_template("new_property.html", title="New Property", form=form)   # Renders the page


@app.route("/search_users", methods=["GET", "POST"])
@login_required
def search_users():
    if current_user.role != ("Admin"):  # Ensures only admins can use this route
        abort(403)  # Redirects to a 403 error
    form = User_search_Form()
    if form.validate_on_submit():  # If the form is valid on submission
        SearchData = db.session.query(User).filter(
            User.name.like('%' + form.name.data + '%')).all()  # Queries the Searched Data
        return render_template("Search_Users.html", SearchData=SearchData, form=form)
    return render_template("Search_Users.html", title="Search Users", form=form)  # Renders the page


@app.route("/all_users") # Output all users
@login_required
def all_users():
    if current_user.role != ("Admin"):  # Ensures only admins can use this route
        abort(403)  # Redirects to a 403 error
    page = request.args.get("page", 1, type=int)
    users = db.session.query(User).order_by(User.role.desc())  # Gets all users from the database
    all = users.paginate(page, per_page=8)  # Paginates the query, allowing it to be shown over multiple pages
    next_url = url_for("all_users", page=all.next_num) \
        if all.has_next else None  # The url for the next page of users
    prev_url = url_for("all_users", page=all.prev_num) \
        if all.has_prev else None  # The url for the previous page of users
    return render_template("all_users.html", all=all, next_url=next_url, prev_url = prev_url)


@app.route("/login", methods=["GET", "POST"])  # Login page
def login():
    if current_user.is_authenticated:  # Prevents user's logging in twice
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # If the password on the form and
            # the password recorded are equal
            login_user(user, remember=form.remember.data)  # Logs in user
            flash("Login Successful", "success")
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful, check your email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")  # Logs out users
def logout():
    logout_user()
    return redirect(url_for("home"))


# @app.route("/emergency", methods=["GET", "POST"])  # Disable before deployment !!!!!!!
# def emergency():
#     form = RegistrationForm()  # Loads registration form from forms
#     if form.validate_on_submit():  # Checks if the form is valid
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
#         user = User(name=form.name.data, phone_number=form.phone_number.data, email=form.email.data,
#                     role=form.role.data, business=form.business.data, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()  # Commits new entry to the database
#         flash("The account has been created!", "success")
#         return redirect(url_for("home"))
#
#     return render_template("register.html", title="Register", form=form)  # Renders template for the user


@app.route("/new_tenancy", methods=["GET", "POST"])  # Creates a new open tenancy on a property
@login_required
def new_tenancy():
    if current_user.role != "Admin":
        abort(403)
    form = New_tenancy_Form()  # Form used
    current_tenancies = db.session.query(Tenancies.property_id)  # Gets property ids
    properties = db.session.query(Properties).filter(Properties.property_id.notin_(current_tenancies))  # gets all properties not already linked to tenancies
    choice_list = [(i.property_id, i.address_line_1 + " " + i.address_line_2) for i in properties]
    form.property.choices = choice_list  # Adds choices to choice list
    if form.validate_on_submit():  # If the form is valid
        tenancy = Tenancies(property_id=form.property.data, start_date=form.start_date.data)
        db.session.add(tenancy)
        db.session.commit()
        flash("The tenancy has been created successfully.", "success")
        return redirect(url_for("home"))
    return render_template("new_tenancy.html", title="New Tenancy", form=form)


@app.route("/add_tenant", methods=["GET", "POST"])  # Adds tenant to open Tenancy
@login_required
def add_tenant():
    if current_user.role != "Admin":
        abort(403)
    form = Add_Tenant_Form()
    tenants = db.session.query(User).filter(User.role == "Tenant")  # Gets all Tenants
    tenant_choice_list = [(i.user_id, i.name) for i in tenants]
    form.Tenant.choices = tenant_choice_list
    locations = db.session.query(Tenancies, Properties).filter(Tenancies.property_id == Properties.property_id).all()
    location_choices = [(j.Tenancies.tenancy_id, j.Properties.address_line_1 + " " + j.Properties.address_line_2) for j
                        in locations]
    form.Tenancy.choices = location_choices
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.user_id == form.Tenant.data).first()
        tenancy = db.session.query(Tenancies).filter(Tenancies.tenancy_id == form.Tenancy.data).first()
        tenancy.occupants.append(user)  # Adds tenant to tenancy
        db.session.commit()
        flash("Tenant added", "success")
        return redirect(url_for("home"))
    return render_template("add_tenant.html", title="Add Tenant", form=form)

@app.route("/remove_tenant/<int:user_id>/<int:property_id>", methods=["GET", "POST"])  # Removes tenant from tenancy
@login_required
def remove_tenant(user_id, property_id):
    if current_user.role != "Admin":
        abort(403)
    user = db.session.query(User).filter_by(user_id=user_id).first()
    tenancy = db.session.query(Tenancies).filter_by(property_id=property_id).first()
    tenancy.occupants.remove(user)
    db.session.commit()
    found = False
    for current in tenancy.occupants:
        print(current)
        if current is not None:
            found = True
    if found == False:
        db.session.delete(tenancy)  # If there is no one else left in the tenancy, it is deleted
        db.session.commit()

    return redirect(url_for("Property", property_id=property_id))


@app.route("/search_properties", methods=["GET", "Post"])  # Search properties
@login_required
def search_properties():
    if current_user.role != ("Admin"):
        abort(403)
    form = Property_search_Form()
    if form.validate_on_submit():
        SearchData = db.session.query(User, Properties).outerjoin(Properties, User.user_id == Properties.landlord_id). \
            filter(Properties.address_line_1.like('%' + form.address_line_1.data + '%')).all()  # Searches data
        return render_template("Search_Properties.html", SearchData=SearchData, form=form)
    return render_template("Search_Properties.html", title="Property Searching", form=form)


@app.route("/Tenant/<int:user_id>")  # Tenant Profile page
@login_required
def Tenant(user_id):
    if current_user.role != ("Admin") and current_user.user_id != user_id:
        abort(403)
    users = db.session.query(User).filter(User.user_id == user_id).first()  # Tenants details
    if users.role != ("Tenant"):
        abort(404)
    tenancies = []
    for tenancy in users.Tenancies:  # Gets all places where  the Tenant is an occupant
        data = db.session.query(Properties, User).outerjoin(Properties, User.user_id == Properties.landlord_id). \
            filter(tenancy.property_id == Properties.property_id).all()
        tenancies = tenancies + data
    return render_template("Tenant.html", title="User Profile", users=users, tenancies=tenancies)


@app.route("/Delete_user/<int:user_id>", methods=["GET", "POST"])  # Deletes a user
@login_required
def Delete_user(user_id):
    if current_user.role != ("Admin"):
        abort(403)
    form = Delete_Form()
    user = db.session.query(User).filter(User.user_id == user_id).first()
    if form.validate_on_submit():  # If the form validates on submission
        for present in user.Tenancies:  # Unlinks a user from a Tenancy
            user.Tenancies.remove(present)
        db.session.delete(user)  # Deletes the user
        db.session.commit()
        flash("The user and their associated data has been deleted", "success")
        return redirect(url_for('home'))
    return render_template("Delete_page.html", form=form)


@app.route("/Update_User/<int:user_id>", methods=["GET", "POST"])  # Updates a Users data
@login_required
def Update_User(user_id):
    if current_user.role != ("Admin"):
        abort(403)
    user = db.session.query(User).filter(User.user_id == user_id).first()
    # if user.role == ("Contractor"):
    #     form = Update_Contractor_Form()
    #     form.user_id.data = user.user_id
    #     form.name.data = user.name
    #     form.phone_number = user.phone_number
    #     form.business_name = user.business
    #     if form.validate_on_submit():
    #         if form.email.d
    #         user.phone_number = form.email.data
    #         user.name = form.name.data
    #         flash("The user has been updated")
    #         return redirect(url_for("home"))
    #         db.session.commit()
    #     elif request.method == "GET":
    #         form.name.data = user.name  # Loads the users name into the form
    #         form.phone_number.data = user.phone_number  # Loads the user's phone number into the form.
    #         form.business_name = user.business  # Loads the user's business name into the form
    #     return render_template("Update_Contractor.html", legend=("Update a User"), user=user, form=form)
    # else:
    form = Update_User_Form()  # Loads the form
    if form.validate_on_submit():
        if form.email.data:  # Only if an email is entered on the form, it is saved
            user.email = form.email.data
        user.phone_number = form.phone_number.data  # Updates the data
        user.business_name = form.business_name.data
        user.name = form.name.data
        db.session.commit()
        print(user)
        flash("The user has been updated", "success")
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == "GET":  # If a GET request is received
        form.name.data = user.name  # Loads the users name into the form
        form.phone_number.data = user.phone_number  # Loads the user's phone number into the form.
        form.business_name.data = user.business
    return render_template("Update_User.html", legend=("Update a User"), user=user, form=form)


@app.route("/Property/<int:property_id>", methods=["GET", "POST"])  # The homepage for each property
@login_required
def Property(property_id):
    property = db.session.query(Properties, User).outerjoin(Properties, User.user_id == Properties.landlord_id). \
        filter(Properties.property_id == property_id).first()  # Gets the properties details
    tenancy = db.session.query(Tenancies).filter(Tenancies.property_id == property_id).first()
    occupancies = db.session.query(User).outerjoin(Tenancies.occupants).filter(Tenancies.property_id == property_id)  # Gets all the occupants of a property
    issues = db.session.query(Issue).filter(Issue.property_id == property_id).order_by(Issue.opened.desc())
    return render_template("Property.html", title="Property", property=property, occupancies=occupancies,
                           tenancy=tenancy, issues=issues)


@app.route("/Delete_property/<int:property_id>")  # Delete Property function
@login_required
def Delete_property(property_id):
    if current_user.role != ("Admin"):
        abort(403)
    form = Delete_Form()
    place = db.session.query(Properties).filter(Properties.property_id == property_id).first()  # Gets property
    if form.validate_on_submit():
        db.session.delete(place)  # Deletes property
        db.session.commit()
        flash("The property has been successfully deleted", "success")
        return redirect(url_for("home"))
    return render_template("Delete_page.html", form=form, title="Delete Property")

@app.route("/Property_update/<int:property_id>", methods=["GET", "POST"])  # Update Property function
@login_required
def Update_Property(property_id):
    if current_user.role != ("Admin"):
        abort(403)
    landlords = db.session.query(User).filter(User.role == "Landlord")
    landlord_list = [(i.user_id, i.name) for i in landlords]
    landlord = db.session.query(User).filter(User.user_id == Properties.landlord_id).first()
    form = Update_Properties_form()
    property = db.session.query(Properties).filter(Properties.property_id == property_id).first()

    form.Landlord.choices = landlord_list  # Fills in the landlord choices box




    if form.validate_on_submit():
        property.address_line_1 = form.address_line_1.data
        property.address_line_2 = form.address_line_2.data
        property.landlord_id = form.Landlord.data
        db.session.commit()
        flash("The property has been updated!", "success")
        return redirect(url_for("home"))
    elif request.method == "GET":  # Fills in the choices
        form.Landlord.default = property.landlord_id
        form.process()
        form.postcode.data = property.postcode
        form.address_line_1.data = property.address_line_1
        form.address_line_2.data = property.address_line_2
    return render_template("Update_Property.html", title="New Property", form=form)


@app.route("/Landlord/<int:user_id>")  # Profile page for landlords
@login_required  # Login required
def Landlord(user_id):
    landlord = db.session.query(User).filter(User.user_id == user_id).first()  # Get's landlord's details
    if landlord.role != ("Landlord"):
        abort(404)
    if current_user.role != ("Admin") and current_user.user_id != user_id:
        abort(403)
    properties = db.session.query(Properties).filter(Properties.landlord_id == user_id).all()
    return render_template("Landlord.html", title="User Profile", landlord=landlord, properties=properties)


@app.route("/Admin/<int:user_id>")  # Admin page
@login_required
def Admin(user_id):
    if current_user.role != ("Admin"):
        abort(403)
    user = db.session.query(User).filter(User.user_id == user_id).first()  # Gets user's details
    if user.role != ("Admin"):
        abort(404)
    return render_template("Admin.html", title="User Profile", user=user)


@app.route("/create_issue/<int:property_id>", methods=["GET", "POST"])  # Creates a new issue
@login_required
def create_issue(property_id):
    form = IssueForm()
    if form.validate_on_submit():
        property = db.session.query(Properties).filter(Properties.property_id == property_id).first()
        issue = Issue(summary=form.summary.data, content=form.content.data, property_id=property_id)
        db.session.add(issue)
        db.session.commit()
        flash("Your issue has been opened", "success")
        landlord = db.session.query(User).filter(User.user_id == property.landlord_id).first()
        msg = Message("New Issue", sender="noreply@Towercoursework.com", recipients=[landlord.email])  # Creates email
        msg.body = f'''A new issue has been created at {property.address_line_1} {property.address_line_1}'''  # Email text
        mail.send(msg)  # Sends email
        return redirect(url_for("home"))
    return render_template("create_issue.html", title="Create an issue", form=form)


@app.route("/all_issues")  # Outputs all issues
@login_required
def all_issues():
    if current_user.role != ("Admin"):
        abort(403)
    page = request.args.get("page", 1, type=int)  # Page for pagination
    query = db.session.query(Issue, Properties).filter(Issue.closed == False).outerjoin(Properties,
                                                          Properties.property_id == Issue.property_id).order_by(
        Issue.issue_id.desc())
    issues = query.paginate(page, per_page=10)
    next_url = url_for("all_issues", page=issues.next_num) \
        if issues.has_next else None
    prev_url = url_for("all_issues", page=issues.prev_num) \
        if issues.has_prev else None
    return render_template("all_issues.html", title="View all issues", issues=issues, next_url=next_url,
                           prev_url=prev_url, page=page)


@app.route("/Issue_page/<int:issue_id>")  # Homepage for issue
@login_required
def Issue_page(issue_id):
    page = request.args.get("page", 1, type=int)
    issue = db.session.query(Issue).filter(Issue.issue_id == issue_id).first()
    place = db.session.query(Properties).filter(Properties.property_id == issue.property_id).first()
    place_url = url_for('Property', property_id=place.property_id)
    jobs = db.session.query(Jobs).filter(Jobs.issue == issue_id).all()
    completed =True  # Checking if all jobs are completed
    for all in jobs:
        if  all.closed == False:
            completed=False
    found_notes = db.session.query(Issue_Notes).filter(Issue_Notes.issue == Issue.issue_id).order_by(
        Issue_Notes.note_id.desc())
    notes = found_notes.paginate(page, per_page=5)
    next_url = url_for("Issue", page=notes.next_num) \
        if notes.has_next else None
    prev_url = url_for("Issue", page=notes.prev_num) \
        if notes.has_prev else None
    create_a_job = url_for("Create_Job", issue_id=issue_id)
    return render_template("Issue.html", title="Issue", issue=issue, notes=notes, next_url=next_url, prev_url=prev_url,
                           create_a_job=create_a_job, jobs=jobs, completed=completed, place=place, place_url=place_url)


@app.route("/Issue_note_page/<int:issue_id>", methods=["GET", "POST"])  # Add a note to an issue
@login_required
def Issue_note_page(issue_id):
    form = note_form()
    if form.validate_on_submit():
        note = Issue_Notes(issue=issue_id, title=form.title.data, content=form.content.data)
        db.session.add(note)  # Adds the note to the database
        db.session.commit()
        flash("Note creation successful", "success")
        return redirect(url_for("home"))
    return render_template("issue_note.html", title="Add a note", form=form)


@app.route("/Landlord_Issues")
@login_required
def Landlord_issues():  # Outputs all issues relevant to a landlord
    if current_user.role != ("Landlord"):
        abort(403)
    page = request.args.get("page", 1, type=int)
    query = db.session.query(Issue, Properties).outerjoin(Properties,
                                                          Properties.property_id == Issue.property_id).filter(
        Properties.landlord_id == current_user.user_id). \
        order_by(Issue.issue_id.desc())  # Queries issues and the properties they are attached to
    issues = query.paginate(page, per_page=10)  # Paginates the query
    next_url = url_for("all_issues", page=issues.next_num) \
        if issues.has_next else None
    prev_url = url_for("all_issues", page=issues.prev_num) \
        if issues.has_prev else None
    issues = query.paginate(page, per_page=10)
    return render_template("all_issues.html", title="View issues", issues=issues, next_url=next_url,
                           prev_url=prev_url, page=page)


@app.route("/Approve_issue/<int:issue_id>")  # Used to approve an issue for work
@login_required
def Approve_issue(issue_id):
    if current_user.role != "Landlord":  # Only Landlord's can approve work
        abort(403)
    properties = db.session.query(Properties, Issue).outerjoin(Properties,
                                                               Properties.property_id == Issue.property_id).filter(
        Properties.landlord_id == current_user.user_id).filter(Issue.issue_id == issue_id).first()
    if properties:
        issue = db.session.query(Issue).filter(Issue.issue_id == issue_id).first()
        issue.approved = True
        db.session.commit()
        flash("Work has been authorized", "success")
        return redirect(url_for('Issue_page', issue_id=issue_id))  # Return to the issue's page
    else:
        flash("You do not have the power to authorize approval", "Failure")
        return redirect(url_for("home"))


@app.route("/Create_Job/<int:issue_id>", methods=["POST", "GET"])  # Creates a Job
@login_required
def Create_Job(issue_id):
    if current_user.role != ("Admin"):
        abort(403)
    form = IssueForm()
    if form.validate_on_submit():
        job = Jobs(issue=issue_id, summary=form.summary.data, content=form.content.data)
        db.session.add(job)
        db.session.commit()
        issue = db.session.query(Issue).filter(Issue.issue_id == issue_id).first()
        property = db.session.query(Properties).filter(Properties.property_id == issue.property_id).first()
        landlord = db.session.query(User).filter(User.user_id == property.landlord_id).first()
        msg = Message("New Job", sender="noreply@Towercoursework.com", recipients=[landlord.email])  # Creates email
        msg.body = f'''A new job has been made for an issue at {property.address_line_1} {property.address_line_2}'''
        mail.send(msg)  # Sends email
        return redirect(url_for('Issue_page', issue_id=issue_id))
    return render_template("add_job.html", form=form, legend=("Create a Job"), title=("Create a Job"))


def send_reset_email(user):  # Used to generate and send password reset links
    token = user.get_reset_token()
    msg = Message("Password Reset Request", sender="noreply@Towercoursework.com",
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
If you did not make this request, ignore this email and no changes will be made
'''
    mail.send(msg)


@app.route("/reset_password", methods=["POST", "GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Your email has been sent with instructions to reset your password,", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():  # Checks if the form is valid
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()  # Commits new entry to the database
        flash("Your password has been updated!", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)


@app.route("/Job/<int:job_id>")  # Job page
@login_required
def Job(job_id):
    page = request.args.get("page", 1, type=int)
    job = db.session.query(Jobs).filter(Jobs.job_id == job_id).first()
    quotes = db.session.query(Quotes, User).outerjoin(Quotes, User.user_id == Quotes.contractor).filter(
        Quotes.job == job_id).all()
    approved = False  # Checks if any quotes have been approved already
    for quote in quotes:
        if quote.Quotes.chosen == True:
            approved = True
    data = db.session.query(Jobs_Notes).filter_by(job = job_id)
    notes = data.paginate(page, per_page=5)
    next_url = url_for("Job", page=notes.next_num) \
        if notes.has_next else None
    prev_url = url_for("Job", page=notes.prev_num) \
        if notes.has_prev else None
    return render_template("Job.html", title="Job page", job=job, quotes=quotes, approved=approved, notes=notes, next_url=next_url, prev_url=prev_url)


@app.route("/Create_a_quote/<int:job_id>", methods=["GET", "POST"])  # Invites contractors
@login_required
def Invite_contractor(job_id):
    if current_user.role != ("Admin"):
        abort(403)
    form = Invite_Form()
    contractors = db.session.query(User).filter(User.role == ("Contractor")).all()  # List of contractors
    contractor_list = [(i.user_id, i.business) for i in contractors]  # Formats the list of contractors
    form.contractor.choices = contractor_list  # Adds the list to the choices on the form
    if form.validate_on_submit():
        chosen = db.session.query(User).filter(User.user_id == form.contractor.data).first()
        msg = Message("Job Invite", sender="noreply@Towercoursework.com", recipients=[chosen.email])
        msg.body = f'''Hello {chosen.name}, You have been invited give a quote on a job. To view more details, click this link and sign in:
{url_for("Add_quote", job_id=job_id, _external=True)}
Thank you'''
        mail.send(msg)
        return redirect(url_for("Job", job_id=job_id))
    return render_template("Invite_contractor.html", title="Invite a contractor", form=form)


@app.route("/Add_quote/<int:job_id>", methods=["GET", "POST"])  # Adds a quote to the database
@login_required
def Add_quote(job_id):
    if current_user.role != "Contractor":
        abort(403)
    form = Quote_Form()
    job = db.session.query(Jobs).filter(Jobs.job_id == job_id).first()
    issue = db.session.query(Issue).filter(Issue.issue_id == job.issue).first()
    place = db.session.query(Properties).filter_by(property_id=issue.property_id).first()
    if form.validate_on_submit():
        quote = Quotes(content=form.content.data, job=job_id, contractor=current_user.user_id)
        db.session.add(quote)
        db.session.commit()
        flash("The quote has been added", "success")
        return redirect(url_for("home"))
    return render_template("Add_Quote.html", title="Add a quote", form=form, job=job, issue=issue, place=place)


@app.route("/Approve_quote/<int:quote_id>", methods=["GET", "POST"])
@login_required
def Approve_quote(quote_id):  # Approving a quote
    if current_user.role != "Admin":
        abort(403)
    form = Approve_Form()
    quote = db.session.query(Quotes).filter_by(quote_id=quote_id).first()
    job = db.session.query(Jobs).filter_by(job_id=quote.job).first()
    already_approved = False
    all_quotes = db.session.query(Quotes).filter_by(job=job.job_id).all()
    for quotes in all_quotes:  # Ensures a quote hasn't already been accepted for a job
        if quotes.chosen == True:
            already_approved = True
    if already_approved == True:
        flash("Quote has already been approved", "warning")
        return redirect(url_for("Job", job_id=job.job_id))
    if form.validate_on_submit():
        quote.chosen = True  # Marks a quote as accepted
        db.session.commit()
        issue = db.session.query(Issue).filter(Issue.issue_id == job.issue).first()
        place = db.session.query(Properties).filter(Properties.property_id == issue.property_id).first()
        contractor = db.session.query(User).filter(quote.contractor == User.user_id).first()
        msg = Message("Your quote has been chosen", sender="noreply@Towercoursework.com", recipients=[contractor.email])
        msg.body = f'''Your quote has been chosen for the following job:
        {job.summary}
        {job.content}
        The address is:
        {place.address_line_1} {place.address_line_2}
        {place.postcode}
        '''
        mail.send(msg)
        flash("The Quote has been approved", "success")
        return redirect(url_for("Job", job_id=job.job_id))
    return render_template("Approval.html", title="Approve a quote", form=form, quote=quote)


@app.route("/Contractor/<int:user_id>")  # Contractor user page
@login_required
def Contractor(user_id):
    if current_user.role == "Tenant" or current_user.role == "Landlord":
        abort(403)
    page = request.args.get("page", 1, type=int)
    contractor = db.session.query(User).filter_by(user_id=user_id).first()
    approved = db.session.query(Quotes, Jobs).outerjoin(Quotes, Jobs.job_id == Quotes.job).filter_by(
        contractor=contractor.user_id).filter_by(chosen=True).filter(Jobs.closed == False).order_by(Quotes.created.desc())
    approved_quotes = approved.paginate(page,  per_page=5)  # Turns the query into a pagination object
    approved_next = url_for("Contractor", user_id=user_id, page=approved_quotes.next_num)\
        if approved_quotes.has_next else None
    approved_prev = url_for("Contractor", user_id=user_id, page=approved_quotes.prev_num) \
        if approved_quotes.has_prev else None
    return render_template("Contractor.html", contractor=contractor,
                           approved_quotes=approved_quotes, approved_next=approved_next, approved_prev=approved_prev,
                           title="Contractor")


@app.route("/delete_issue/<int:issue_id>", methods=["GET", "POST"])
@login_required
def delete_issue(issue_id):
    if current_user.role != "Admin":
        abort(403)
    form = Delete_Form()
    issue = db.session.query(Issue).filter_by(issue_id=issue_id).first()
    if issue not in locals():  # If the issue doesn't exist abort
        abort(404)
    if form.validate_on_submit():
        db.session.delete(issue)
        db.session.commit()
        return redirect(url_for("all_issues"))
    return render_template("Delete_page.html", form=form)

@app.route("/contractor_job/<int:job_id>")
@login_required
def contractor_job(job_id):  # Details of a job shown to a contractor
    page = request.args.get("page", 1, type=int)
    quote = db.session.query(Quotes).filter_by(job = job_id).first()
    job = db.session.query(Jobs).filter_by(job_id = job_id).first()
    issue= db.session.query(Issue).filter_by(issue_id = job.issue).first()
    location = db.session.query(Properties).filter_by(property_id = issue.property_id).first()
    landlord = db.session.query(User).filter_by(user_id = location.landlord_id).first()
    job_notes= db.session.query(Jobs_Notes).filter(Jobs_Notes.job == job.job_id)
    notes = job_notes.paginate(page, per_page=5)
    next_url = url_for("contractor_job", page=notes.next_num) \
        if notes.has_next else None
    prev_url = url_for("contractor_job", page=notes.prev_num) \
        if notes.has_prev else None

    occupants = db.session.query(User, Tenancies).outerjoin(Tenancies.occupants).filter(Tenancies.property_id == location.property_id)

    return render_template("contractor_job.html", quote=quote, job=job, location=location, issue=issue,
                           landlord=landlord, occupants=occupants, title="Job", next_url=next_url, prev_url=prev_url,
                           notes=notes)

@app.route("/contractor_all_quotes/<int:user_id>") # Outputs all quotes a contractor has made
@login_required
def contractor_all_quotes(user_id):
    page = request.args.get("page", 1, type=int)
    quotes = db.session.query(Quotes,Jobs).outerjoin(Quotes, Jobs.job_id==Quotes.job).filter_by(contractor = user_id).order_by(Quotes.created.desc())
    all_quotes = quotes.paginate(page, per_page=8)
    next_url = url_for("contractor_all_quotes", user_id=user_id, page=all_quotes.next_num)\
        if all_quotes.has_next else None
    prev_url = url_for("contractor_all_quotes", user_id=user_id, page=all_quotes.prev_num) \
        if all_quotes.has_prev else None
    return render_template("contractor_all_quotes.html", all_quotes=all_quotes, next_url=next_url, prev_url=prev_url,
                           title="Contractor quotes")


@app.route("/add_job_note/<int:job_id>", methods=["GET", "POST"])  # Add a note to a job
@login_required
def add_job_note(job_id):
    form = note_form()
    if form.validate_on_submit():
        note = Jobs_Notes(title=form.title.data, content=form.content.data, job=job_id)
        db.session.add(note)
        db.session.commit()
        if current_user.role != "Contractor":  # If the current user's role is a contractor, redirect to contractors job details page.
            return redirect(url_for("Job", job_id=job_id))
        else:
            return redirect(url_for("contractor_job", job_id=job_id))
    return render_template("issue_note.html", form=form, title="Add a job")


@app.route("/delete_job_note/<int:note_id>", methods=["GET", "POST"])  # Deletes a note on a job
@login_required
def delete_job_note(note_id):
    if current_user.role != "Admin":
        abort(403)
    form = Delete_Form()
    note = db.session.query(Jobs_Notes).filter_by(note_id=note_id).first()
    if note not in locals():  # If the note doesn't exist, abort
        abort(404)
    if form.validate_on_submit():
        job = db.session.query(Jobs).filter(Jobs.job_id == note.job).first()
        db.session.delete(note)
        db.session.commit()
        flash("The note has been successfully deleted", "success")
        return redirect(url_for("Job", job_id=job.job_id))
    return render_template("Delete_page.html", title="Delete Note", form=form)

@app.route("/delete_issue_note/<int:note_id>", methods=["GET", "POST"])  # Delete's a note tied to an issue
@login_required
def delete_issue_note(note_id):
    if current_user.role != "Admin":
        abort(403)
    form = Delete_Form()
    note = db.session.query(Issue_Notes).filter_by(note_id=note_id).first()  # Gets the note
    if note not in locals():  # If the notes doesn't exist, abort
        abort(404)
    if form.validate_on_submit():
        issue = db.session.query(Issue).filter(Issue.issue_id == note.issue).first()
        db.session.delete(note)
        db.session.commit()
        flash("The note has been successfully deleted", "success")
        return redirect(url_for("Issue_page", issue_id=issue.issue_id))
    return render_template("Delete_page.html",title="Delete Note", form=form)

@app.route("/job_closing/<int:job_id>", methods=["GET", "POST"])  # Marks a job as closed
@login_required
def job_closing(job_id):
    if current_user.role != "Admin":
        abort(403)
    job = db.session.query(Jobs).filter_by(job_id = job_id).first()
    form = Close_Form()  # Job closure form
    if form.validate_on_submit():
        issue = db.session.query(Issue).filter(Issue.issue_id == job.issue).first()
        job.closed = True
        db.session.commit()
        flash("Job has been marked as complete", "success")
        return redirect(url_for("Issue_page", issue_id=issue.issue_id))
    return render_template("job_closing.html", form=form, job=job)  # Renders job closure page, passing over the form and the job details


@app.route("/issue_closing/<int:issue_id>", methods=["GET", "POST"])  # Marks an issue as closed
@login_required
def issue_closing(issue_id):
    if current_user.role != "Admin":
        abort(403)
    issue = db.session.query(Issue).filter_by(issue_id = issue_id).first()
    form = Close_Form()
    if form.validate_on_submit():
        issue.closed = True
        db.session.commit()
        flash("Job has been marked as complete", "success")
        return redirect(url_for("Issue_page", issue_id=issue.issue_id))
    return render_template("issue_closing.html", form=form, issue=issue) # Renders job closure page, passing over the form and the job details


@app.route("/all_properties")  # Outputs all properties on a page
@login_required
def all_properties():
    if current_user.role != "Admin":
        abort(403)
    page = request.args.get("page", 1, type=int)
    all_places = db.session.query(Properties, User).outerjoin(Properties, User.user_id == Properties.landlord_id).filter(Properties.landlord_id == User.user_id).order_by(Properties.property_id.desc())
    places = all_places.paginate(page, per_page=8)  # Turns the query into a pagination object
    print(places)
    next_url = url_for("all_properties", page=places.next_num) \
        if places.has_next else None
    prev_url = url_for("all_properties", page=places.prev_num) \
        if places.has_prev else None
    return render_template("all_properties.html", places=places, prev_url=prev_url, next_url=next_url)  # Creates the page with the data supplied.