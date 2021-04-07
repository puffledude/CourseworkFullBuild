from Tower import app, bcrypt, mail
from .Branch import db, login_manager
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from Tower.models import User, Properties, Tenancies, Issue, Issue_Notes, Jobs, Jobs_Notes, Quotes
from Tower.forms import RegistrationForm, PropertiesForm, User_search_Form, LoginForm, IssueForm, New_tenancy_Form, \
    Property_search_Form, Add_Tenant_Form, Update_User_Form, Update_Contractor_Form, note_form, Update_Properties_form, \
    Delete_Form, RequestResetForm, ResetPasswordForm, Invite_Form, Quote_Form, Approve_Form
from flask_mail import Message


@app.route("/")
@app.route("/home")  # Home page for the web app
def home():
    return render_template("home.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(403)
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
With this you can register any issues you have with your property'''
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
        return redirect(url_for("home"))
    return render_template("new_property.html", title="New Property", form=form)


@app.route("/search_users", methods=["GET", "POST"])
@login_required
def search_users():
    if current_user.role != ("Admin"):  # Ensures only admins can use this route
        abort(403)  # Redirects to a 403 error
    form = User_search_Form()
    if form.validate_on_submit():
        SearchData = db.session.query(User).filter(
            User.name.like('%' + form.name.data + '%')).all()  # Queries the Searched Data
        print(SearchData)
        return render_template("Search_Users.html", SearchData=SearchData, form=form)
    return render_template("Search_Users.html", title="Search Users", form=form)




@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login Successful", "success")
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful, check your email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/emergency", methods=["GET", "POST"])  # Disable before deployment !!!!!!!
def emergency():
    form = RegistrationForm()  # Loads registration form from forms
    if form.validate_on_submit():  # Checks if the form is valid
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(name=form.name.data, phone_number=form.phone_number.data, email=form.email.data,
                    role=form.role.data, business=form.business.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()  # Commits new entry to the database
        flash("The account has been created!", "success")
        return redirect(url_for("home"))

    return render_template("register.html", title="Register", form=form)  # Renders template for the user


@app.route("/new_tenancy", methods=["GET", "POST"])
@login_required
def new_tenancy():
    if current_user.role != "Admin":
        abort(403)
    form = New_tenancy_Form()
    current_tenancies = db.session.query(Tenancies.property_id)
    properties = db.session.query(Properties).filter(Properties.property_id.notin_(current_tenancies))
    choice_list = [(i.property_id, i.address_line_1 + " " + i.address_line_2) for i in properties]
    form.property.choices = choice_list
    if form.validate_on_submit():
        tenancy = Tenancies(property_id=form.property.data, start_date=form.start_date.data)
        db.session.add(tenancy)
        db.session.commit()
        flash("The tenancy has been created successfully.", "success")
        return redirect(url_for("home"))
    return render_template("new_tenancy.html", title="New Tenancy", form=form)


@app.route("/add_tenant", methods=["GET", "POST"])
@login_required
def add_tenant():
    if current_user.role != "Admin":
        abort(403)
    form = Add_Tenant_Form()
    tenants = db.session.query(User).filter(User.role == "Tenant")
    tenant_choice_list = [(i.user_id, i.name) for i in tenants]
    form.Tenant.choices = tenant_choice_list
    locations = db.session.query(Tenancies, Properties).filter(Tenancies.property_id == Properties.property_id).all()
    location_choices = [(j.Tenancies.tenancy_id, j.Properties.address_line_1 + " " + j.Properties.address_line_2) for j
                        in locations]
    form.Tenancy.choices = location_choices
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.user_id == form.Tenant.data).first()
        tenancy = db.session.query(Tenancies).filter(Tenancies.tenancy_id == form.Tenancy.data).first()
        tenancy.occupants.append(user)
        db.session.commit()
        flash("Tenant added", "success")
        return redirect(url_for("home"))
    return render_template("add_tenant.html", title="Add Tenant", form=form)


@app.route("/search_properties", methods=["GET", "Post"])
@login_required
def search_properties():
    if current_user.role != ("Admin"):
        abort(403)
    form = Property_search_Form()
    if form.validate_on_submit():
        SearchData = db.session.query(User, Properties).outerjoin(Properties, User.user_id == Properties.landlord_id). \
            filter(Properties.address_line_1.like('%' + form.address_line_1.data + '%')).all()
        return render_template("Search_Properties.html", SearchData=SearchData, form=form)
    return render_template("Search_Properties.html", title="Property Searching", form=form)


@app.route("/Tenant/<int:user_id>")
@login_required
def Tenant(user_id):
    if current_user.role != ("Admin") and current_user.user_id != user_id:
        abort(403)
    users = db.session.query(User).filter(User.user_id == user_id).first()
    if users.role != ("Tenant"):
        abort(404)
    tenancies = []
    for tenancy in users.Tenancies:
        data = db.session.query(Properties, User).outerjoin(Properties, User.user_id == Properties.landlord_id). \
            filter(tenancy.property_id == Properties.property_id).all()
        tenancies = tenancies + data
    return render_template("Tenant.html", title="User Profile", users=users, tenancies=tenancies)


@app.route("/Delete_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def Delete_user(user_id):
    if current_user.role != ("Admin"):
        abort(403)
    form = Delete_Form()
    if form.validate_on_submit():  # If the form validates on submission
        user = db.session.query(User).filter(User.user_id == user_id).first()
        for present in user.Tenancies:  # Unlinks a user from a Tenancy
            user.Tenancies.remove(present)
        db.session.delete(user)  # Deletes the user
        db.session.commit()
        flash("The user and their associated data has been deleted", "success")
        return redirect(url_for('home'))
    return render_template("Delete_page.html", form=form)


@app.route("/Update_User/<int:user_id>", methods=["GET", "POST"])  # Currently broken. Needs fixing
@login_required
def Update_User(user_id):
    if current_user.role != ("Admin"):
        abort(403)
    user = db.session.query(User).filter(User.user_id == user_id).first()
    if user.role == ("Contractor"):
        form = Update_Contractor_Form()
        form.user_id.data = user.user_id
        form.name.data = user.name
        form.phone_number = user.phone_number
        form.business_name = user.business
        if form.validate_on_submit():
            user.email = form.email.data
            user.phone_number = form.email.data
            user.name = form.name.data
            flash("The user has been updated")
            return redirect(url_for("home"))
            db.session.commit()
        elif request.method == "GET":
            form.name.data = user.name  # Loads the users name into the form
            form.phone_number.data = user.phone_number  # Loads the user's phone number into the form.
            form.business_name = user.business  # Loads the user's business name into the form
        return render_template("Update_Contractor.html", legend=("Update a User"), user=user, form=form)
    else:
        form = Update_User_Form()  # Loads the form
        if form.validate_on_submit():
            if form.email.data:  # Only if an email is entered on the form, it is saved
                user.email = form.email.data
            user.phone_number = form.phone_number.data  # Updates the data
            user.name = form.name.data
            db.session.commit()
            print(user)
            flash("The user has been updated", "success")
            db.session.commit()
            return redirect(url_for('home'))
        elif request.method == "GET":  # If a GET request is received
            form.name.data = user.name  # Loads the users name into the form
            form.phone_number.data = user.phone_number  # Loads the user's phone number into the form.
        return render_template("Update_User.html", legend=("Update a User"), user=user, form=form)


@app.route("/Property/<int:property_id>", methods=["GET", "POST"])
@login_required
def Property(property_id):
    property = db.session.query(Properties, User).outerjoin(Properties, User.user_id == Properties.landlord_id). \
        filter(Properties.property_id == property_id).first()
    tenancy = db.session.query(Tenancies).filter(Tenancies.property_id == property_id).first()
    occupancies = db.session.query(User).outerjoin(Tenancies.occupants).filter(Tenancies.property_id == property_id)
    # for users in tenancy.User:
    # data = db.session.query(User).filter(users.user_id == User.user_id)
    # occupancies = occupancies+data
    return render_template("Property.html", title="Property", property=property, occupancies=occupancies,
                           tenancy=tenancy)


@app.route("/Delete_property/<int:property_id>")
@login_required
def Delete_property(property_id):
    pass


@app.route("/Property_update/<int:property_id>", methods=["GET", "POST"])
@login_required
def Update_Property(property_id):
    if current_user.role != ("Admin"):
        abort(403)
    form = Update_Properties_form()
    landlords = db.session.query(User).filter(User.role == "Landlord")
    landlord_list = [(i.user_id, i.name) for i in landlords]
    form.Landlord.choices = landlord_list  # Fills in the landlord choices box
    property = db.session.query(Properties).filter(Properties.property_id == property_id).first()
    if form.validate_on_submit():
        property.address_line_1 = form.address_line_1.data
        property.address_line_2 = form.address_line_2.data
        property.landlord_id = form.Landlord.data
        db.session.commit()
        flash("The property has been updated!", "success")
        return redirect(url_for("home"))
    elif request.method == "GET":
        form.Landlord.data = property.landlord_id
        form.postcode.data = property.postcode
        form.address_line_1.data = property.address_line_1
        form.address_line_2.data = property.address_line_2
    return render_template("Update_Property.html", title="New Property", form=form)


@app.route("/Landlord/<int:user_id>")
@login_required
def Landlord(user_id):
    landlord = db.session.query(User).filter(User.user_id == user_id).first()
    print(current_user)
    if landlord.role != ("Landlord"):
        abort(404)
    if current_user.role != ("Admin") and current_user.user_id != user_id:
        abort(403)
    properties = db.session.query(Properties).filter(Properties.landlord_id == user_id).all()
    return render_template("Landlord.html", title="User Profile", landlord=landlord, properties=properties)


@app.route("/Admin/<int:user_id>")
@login_required
def Admin(user_id):
    if current_user.role != ("Admin"):
        abort(403)
    user = db.session.query(User).filter(User.user_id == user_id).first()
    if user.role != ("Admin"):
        abort(404)
    return render_template("Admin.html", title="User Profile", user=user)


@app.route("/create_issue/<int:property_id>", methods=["GET", "POST"])
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
        msg = Message("New Issue", sender="noreply@Towercoursework.com", recipients=[landlord.email])
        msg.body = f'''A new issue has been created at {property.address_line_1} {property.address_line_1}'''
        mail.send(msg)
        return redirect(url_for("home"))
    return render_template("create_issue.html", title="Create an issue", form=form)


@app.route("/all_issues")
@login_required
def all_issues():
    if current_user.role != ("Admin"):
        abort(403)
    page = request.args.get("page", 1, type=int)
    query = db.session.query(Issue, Properties).outerjoin(Properties,
                                                          Properties.property_id == Issue.property_id).order_by(
        Issue.issue_id.desc())
    issues = query.paginate(page, per_page=10)
    next_url = url_for("all_issues", page=issues.next_num) \
        if issues.has_next else None
    prev_url = url_for("all_issues", page=issues.prev_num) \
        if issues.has_prev else None
    return render_template("all_issues.html", title="View all issues", issues=issues, next_url=next_url,
                           prev_url=prev_url, page=page)


@app.route("/Issue_page/<int:issue_id>")
@login_required
def Issue_page(issue_id):
    page = request.args.get("page", 1, type=int)
    issue = db.session.query(Issue).filter(Issue.issue_id == issue_id).first()
    print(issue)
    jobs = db.session.query(Jobs).filter(Jobs.issue == issue_id).all()
    found_notes = db.session.query(Issue_Notes).filter(Issue_Notes.issue == Issue.issue_id).order_by(
        Issue_Notes.note_id.desc())
    notes = found_notes.paginate(page, per_page=5)
    next_url = url_for("Issue", page=notes.next_num) \
        if notes.has_next else None
    prev_url = url_for("Issue", page=notes.prev_num) \
        if notes.has_prev else None
    create_a_job = url_for("Create_Job", issue_id=issue_id)
    return render_template("Issue.html", title="Issue", issue=issue, notes=notes, next_url=next_url, prev_url=prev_url,
                           create_a_job=create_a_job, jobs=jobs)


@app.route("/Issue_note_page/<int:issue_id>", methods=["GET", "POST"])
@login_required
def Issue_note_page(issue_id):
    form = note_form()
    if form.validate_on_submit():
        note = Issue_Notes(issue=issue_id, title=form.title.data, content=form.content.data)
        db.session.add(note)
        db.session.commit()
        flash("Note creation successful", "success")
        return redirect(url_for("home"))
    return render_template("issue_note.html", title="Add a note", form=form)


@app.route("/Landlord_Issues")
@login_required
def Landlord_issues():
    if current_user.role != ("Landlord"):
        abort(403)
    page = request.args.get("page", 1, type=int)
    query = db.session.query(Issue, Properties).outerjoin(Properties,
                                                          Properties.property_id == Issue.property_id).filter(
        Properties.landlord_id == current_user.user_id). \
        order_by(Issue.issue_id.desc())
    issues = query.paginate(page, per_page=10)
    next_url = url_for("all_issues", page=issues.next_num) \
        if issues.has_next else None
    prev_url = url_for("all_issues", page=issues.prev_num) \
        if issues.has_prev else None
    issues = query.paginate(page, per_page=10)
    return render_template("all_issues.html", title="View issues", issues=issues, next_url=next_url,
                           prev_url=prev_url, page=page)


@app.route("/Approve_issue/<int:issue_id>")
@login_required
def Approve_issue(issue_id):
    if current_user.role != "Landlord":
        abort(403)
    properties = db.session.query(Properties, Issue).outerjoin(Properties,
                                                               Properties.property_id == Issue.property_id).filter(
        Properties.landlord_id == current_user.user_id).filter(Issue.issue_id == issue_id).first()
    if properties:
        issue = db.session.query(Issue).filter(Issue.issue_id == issue_id).first()
        issue.approved = True
        db.session.commit()
        flash("Work has been authorized")
        return redirect(url_for('Issue_page', issue_id=issue_id))
    else:
        flash("You do not have the power to authorize approval", "Failure")
        return redirect(url_for("home"))


@app.route("/Create_Job/<int:issue_id>", methods=["POST", "GET"])
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
        msg = Message("New Job", sender="noreply@Towercoursework.com", recipients=[landlord.email])
        msg.body = f'''A new job has been made for an issue at {property.address_line_1} {property.address_line_2}'''
        mail.send(msg)
        return redirect(url_for('Issue_page', issue_id=issue_id))
    return render_template("add_job.html", form=form, legend=("Create a Job"), title=("Create a Job"))


def send_reset_email(user):
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


@app.route("/Job/<int:job_id>")
@login_required
def Job(job_id):
    job = db.session.query(Jobs).filter(Jobs.job_id == job_id).first()
    quotes = db.session.query(Quotes, User).outerjoin(Quotes, User.user_id == Quotes.contractor).filter(
        Quotes.job == job_id).all()
    approved = False
    for quote in quotes:
        if quote.Quotes.chosen == True:
            approved = True

    return render_template("Job.html", job=job, quotes=quotes, approved=approved)


@app.route("/Create_a_quote/<int:job_id>", methods=["GET", "POST"])
@login_required
def Invite_contractor(job_id):
    if current_user.role != ("Admin"):
        abort(403)
    form = Invite_Form()
    contractors = db.session.query(User).filter(User.role == ("Contractor")).all()
    contractor_list = [(i.user_id, i.name) for i in contractors]
    form.contractor.choices = contractor_list
    if form.validate_on_submit():
        chosen = db.session.query(User).filter(User.user_id == form.contractor.data).first()
        msg = Message("Job Invite", sender="noreply@Towercoursework.com", recipients=[chosen.email])
        msg.body = f'''Hello {chosen.name}, You have been invited give a quote on a job. To view more details, click this link and sign in:
{url_for("Add_quote", job_id=job_id, _external=True)}
Thank you'''
        mail.send(msg)
        return redirect(url_for("Job", job_id=job_id))
    return render_template("Invite_contractor.html", title="Invite a contractor", form=form)


@app.route("/Add_quote/<int:job_id>", methods=["GET", "POST"])
@login_required
def Add_quote(job_id):
    if current_user.role != "Contractor":
        abort(403)
    form = Quote_Form()
    job = db.session.query(Jobs).filter(Jobs.job_id == job_id).first()
    issue = db.session.query(Issue).filter(Issue.issue_id == job.issue).first()
    place = db.session.query(Properties).filter_by(property_id=issue.property_id)
    if form.validate_on_submit():
        quote = Quotes(content=form.content.data, job=job_id, contractor=current_user.user_id)
        db.session.add(quote)
        db.session.commit()
        flash("The quote has been added", "success")
        return redirect(url_for("home"))
    return render_template("Add_Quote.html", form=form, job=job, issue=issue, place=place)


@app.route("/Approve_quote/<int:quote_id>", methods=["GET", "POST"])
@login_required
def Approve_quote(quote_id):
    if current_user.role != "Admin":
        abort(403)
    form = Approve_Form()
    quote = db.session.query(Quotes).filter_by(quote_id=quote_id).first()
    job = db.session.query(Jobs).filter_by(job_id=quote.job).first()
    already_approved = False
    all_quotes = db.session.query(Quotes).filter_by(job=job.job_id).all()
    for quotes in all_quotes:
        if quotes.chosen == True:
            already_approved = True
    if already_approved == True:
        flash("Quote has already been approved")
        return redirect(url_for("Job", job_id=job.job_id))
    if form.validate_on_submit():
        quote.chosen = True
        db.session.commit()
        issue = db.session.query(Issue).filter(Issue.issue_id == job.issue).first()
        place = db.session.query(Properties).filter(Properties.property_id == issue.property_id).first()
        contractor = db.session.query(User).filter(quote.contractor == User.user_id).first()
        msg = Message("Your quote has been chosen", sender="noreply@Towercoursework.com", recipients=[contractor.email])
        msg.body = f'''Your quote has been chosen for the following job:
        {job.title}
        {job.content}
        The address is:
        {place.address_line_1} {place.address_line_2}
        {place.postcode}
        '''
        return redirect(url_for("Job", job_id=job.job_id))
    return render_template("Approval.html", form=form, quote=quote)


@app.route("/Contractor/<int:user_id>")
@login_required
def Contractor(user_id):
    if current_user.role == "Tenant" or current_user.role == "Landlord":
        abort(403)
    page = request.args.get("page", 1, type=int)
    contractor = db.session.query(User).filter_by(user_id=user_id).first()
    approved = db.session.query(Quotes, Jobs).outerjoin(Quotes, Jobs.job_id == Quotes.job).filter_by(
        contractor=contractor.user_id).filter_by(chosen=True).filter(Jobs.closed == False).order_by(Quotes.created.desc())
    approved_quotes = approved.paginate(page,  per_page=5)
    approved_next = url_for("Contractor", user_id=user_id, page=approved_quotes.next_num)\
        if approved_quotes.has_next else None
    approved_prev = url_for("Contractor", user_id=user_id, page=approved_quotes.prev_num) \
        if approved_quotes.has_prev else None
    return render_template("Contractor.html", contractor=contractor,
                           approved_quotes=approved_quotes, approved_next=approved_next, approved_prev=approved_prev)


@app.route("/delete_issue/<int:issue_id>", methods=["GET", "POST"])
@login_required
def delete_issue(issue_id):
    if current_user.role != "Admin":
        return redirect(url_for("Issue_page", issue_id=issue_id))
    issue = db.session.query(Issue).filter_by(issue_id=issue_id).first()
    property =db.session.query(Properties).filter_by(property_id = issue.property_id).first()
    db.session.delete(issue)
    db.session.commit()
    return redirect(url_for("all_issues"))