from Tower import app, bcrypt
from .Branch import db, login_manager
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from Tower.models import User, Properties, Tenancies, Issue, Issue_Notes, Jobs, Jobs_Notes, Quotes
from Tower.forms import RegistrationForm, PropertiesForm, User_search_Form, LoginForm, IssueForm, New_tenancy_Form,\
    Property_search_Form, Add_Tenant_Form, Update_User_Form, Update_Contractor_Form, note_form, Update_Properties_form,\
    Delete_Form


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
        return redirect(url_for("home"))

    return render_template("register.html", title="Register", form=form)  # Renders template for the user


@app.route("/new_property", methods=["GET", "POST"]) #Adds a new property to the database
@login_required
def new_property():
    if current_user.role != ("Admin"): #Ensures only admins can use this route
        abort(403) #Redirects to a 403 error
    landlords = db.session.query(User).filter(User.role == "Landlord")
    form = PropertiesForm()
    landlord_list = [(i.user_id, i.name) for i in landlords]
    form.Landlord.choices = landlord_list #Fills in the landlord choices box
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
    if current_user.role != ("Admin"): #Ensures only admins can use this route
        abort(403) #Redirects to a 403 error
    form = User_search_Form()
    if form.validate_on_submit():
        SearchData = db.session.query(User).filter(User.name.like('%'+form.name.data+'%')).all() #Queries the Searched Data
        print(SearchData)
        return render_template("Search_Users.html", SearchData=SearchData, form=form)
    return render_template("Search_Users.html", title = "Search Users", form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("home"))
            flash("Login Successful", "success")
        else:
            flash("Login Unsuccessful, check your email and password", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/emergency", methods=["GET", "POST"]) #Disable before deployment !!!!!!!
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

@app.route("/new_tenancy",methods=["GET", "POST"])
@login_required
def new_tenancy():
    if current_user.role != "Admin":
        abort(403)
    form = New_tenancy_Form()
    current_tenancies = db.session.query(Tenancies.property_id)
    properties = db.session.query(Properties).filter(Properties.property_id.notin_(current_tenancies))
    choice_list = [(i.property_id, i.address_line_1+" "+i.address_line_2) for i in properties]
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
    tenants = db.session.query(User).filter(User.role=="Tenant")
    tenant_choice_list = [(i.user_id, i.name)for i in tenants]
    form.Tenant.choices = tenant_choice_list
    locations = db.session.query(Tenancies, Properties).filter(Tenancies.property_id == Properties.property_id).all()
    location_choices = [(j.Tenancies.tenancy_id, j.Properties.address_line_1+ " "+ j.Properties.address_line_2) for j in locations]
    form.Tenancy.choices= location_choices
    if form.validate_on_submit():
        user= db.session.query(User).filter(User.user_id == form.Tenant.data).first()
        tenancy= db.session.query(Tenancies).filter(Tenancies.tenancy_id == form.Tenancy.data).first()
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
        SearchData = db.session.query(User, Properties).outerjoin(Properties, User.user_id == Properties.landlord_id).\
            filter(Properties.address_line_1.like('%'+form.address_line_1.data+'%')).all()
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
        data= db.session.query(Properties, User).outerjoin(Properties, User.user_id == Properties.landlord_id).\
            filter(tenancy.property_id == Properties.property_id).all()
        tenancies = tenancies+data
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

@app.route("/Update_User/<int:user_id>" , methods=["GET", "POST"]) #Currently broken. Needs fixing
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
        form.business_name =user.business
        if form.validate_on_submit():
            user.email = form.email.data
            user.phone_number = form.email.data
            user.name = form.name.data
            flash("The user has been updated")
            return redirect(url_for("home"))
            db.session.commit()
        elif request.method == "GET":
            form.name.data = user.name  # Loads the users name into the form
            form.phone_number.data =user.phone_number# Loads the user's phone number into the form.
            form.business_name = user.business #Loads the user's business name into the form
        return render_template("Update_Contractor.html",legend=("Update a User") ,user=user, form=form)
    else:
        form = Update_User_Form() #Loads the form
        if form.validate_on_submit():
            if form.email.data: #Only if an email is entered on the form, it is saved
                user.email = form.email.data
            user.phone_number = form.phone_number.data #Updates the data
            user.name = form.name.data
            db.session.commit()
            print(user)
            flash("The user has been updated", "success")
            db.session.commit()
            return redirect(url_for('home'))
        elif request.method == "GET": #If a GET request is received
            form.name.data = user.name #Loads the users name into the form
            form.phone_number.data = user.phone_number #Loads the user's phone number into the form.
        return render_template("Update_User.html",legend=("Update a User"), user=user, form=form)



@app.route("/Property/<int:property_id>", methods=["GET", "POST"])
@login_required
def Property(property_id):
    property = db.session.query(Properties, User).outerjoin(Properties, User.user_id == Properties.landlord_id).\
        filter(Properties.property_id == property_id).first()
    tenancy = db.session.query(Tenancies).filter(Tenancies.property_id == property_id).first()
    occupancies = db.session.query(User).outerjoin(Tenancies.occupants).filter(Tenancies.property_id == property_id)
    #for users in tenancy.User:
        #data = db.session.query(User).filter(users.user_id == User.user_id)
        #occupancies = occupancies+data
    return render_template("Property.html", title="Property", property=property, occupancies=occupancies, tenancy=tenancy)

@app.route("/Delete_property/<int:property_id>")
@login_required
def Delete_property(property_id):
    pass



@app.route("/Property_update/<int:property_id>", methods=["GET", "POST"])
@login_required
def Update_Property(property_id):
    if current_user.role !=("Admin"):
        abort(403)
    form = Update_Properties_form()
    landlords = db.session.query(User).filter(User.role == "Landlord")
    landlord_list = [(i.user_id, i.name) for i in landlords]
    form.Landlord.choices = landlord_list #Fills in the landlord choices box
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
    if current_user.role !=("Admin") and current_user.user_id != user_id:
        abort(403)
    properties = db.session.query(Properties).filter(Properties.landlord_id == user_id).all()
    return render_template("Landlord.html", title="User Profile", landlord=landlord, properties=properties)

@app.route("/Admin/<int:user_id>")
@login_required
def Admin(user_id):
    if current_user.role !=("Admin"):
        abort(403)
    user = db.session.query(User).filter(User.user_id == user_id).first()
    if user.role !=("Admin"):
        abort(404)
    return render_template("Admin.html", title = "User Profile",user=user)

@app.route("/create_issue/<int:property_id>", methods=["GET", "POST"])
@login_required
def create_issue(property_id):
    form = IssueForm()
    if form.validate_on_submit():
        property=db.session.query(Properties).filter(Properties.property_id == property_id)
        issue = Issue(summary=form.summary.data, content = form.content.data, property_id = property_id)
        db.session.add(issue)
        db.session.commit()
        flash("Your issue has been opened", "success")
        return redirect(url_for("home"))
    return render_template("create_issue.html", title="Create an issue", form=form)

@app.route("/all_issues")
@login_required
def all_issues():
    if current_user.role !=("Admin"):
        abort(403)
    page = request.args.get("page", 1, type=int)
    query = db.session.query(Issue, Properties).outerjoin(Properties, Properties.property_id == Issue.property_id).order_by(Issue.issue_id.desc())
    issues = query.paginate(page, per_page=10)
    next_url = url_for("all_issues", page=issues.next_num)\
    if issues.has_next else None
    prev_url = url_for("all_issues", page=issues.prev_num)\
    if issues.has_prev else None
    return render_template("all_issues.html", title = "View all issues", issues=issues, next_url=next_url, prev_url=prev_url, page=page)

@app.route("/Issue_page/<int:issue_id>")
@login_required
def Issue_page(issue_id):
    page = request.args.get("page", 1, type=int)
    issue = db.session.query(Issue).filter(Issue.issue_id == issue_id).first()
    print(issue)
    jobs = db.session.query(Jobs).filter(Jobs.issue == issue_id).all()
    found_notes = db.session.query(Issue_Notes).filter(Issue_Notes.issue == Issue.issue_id).order_by(Issue_Notes.note_id.desc())
    notes = found_notes.paginate(page, per_page=5)
    next_url = url_for("Issue", page = notes.next_num)\
    if notes.has_next else None
    prev_url = url_for("Issue", page=notes.prev_num)\
    if notes.has_prev else None
    create_a_job = url_for("Create_Job", issue_id=issue_id)
    return render_template("Issue.html", title="Issue", issue=issue, notes=notes, next_url=next_url, prev_url=prev_url, create_a_job=create_a_job, jobs=jobs)

@app.route("/Issue_note_page/<int:issue_id>", methods=["GET", "POST"])
@login_required
def Issue_note_page(issue_id):
    form = note_form()
    if form.validate_on_submit():
        note = Issue_Notes(issue = issue_id, title = form.title.data, content = form.content.data)
        db.session.add(note)
        db.session.commit()
        flash("Note creation successful", "success")
        return redirect(url_for("home"))
    return render_template("issue_note.html", title="Add a note", form=form)

@app.route("/Landlord_Issues")
@login_required
def Landlord_issues():
    if current_user.role !=("Landlord"):
        abort(403)
    page = request.args.get("page", 1, type=int)
    query = db.session.query(Issue, Properties).outerjoin(Properties,
                                                          Properties.property_id == Issue.property_id).filter(Properties.landlord_id==current_user.user_id).\
        order_by(Issue.issue_id.desc())
    issues = query.paginate(page, per_page=10)
    next_url = url_for("all_issues", page=issues.next_num)\
        if issues.has_next else None
    prev_url = url_for("all_issues", page=issues.prev_num)\
        if issues.has_prev else None
    issues = query.paginate(page, per_page=10)
    return render_template("all_issues.html", title="View issues", issues=issues, next_url=next_url,
                           prev_url=prev_url, page=page)

@app.route("/Approve_issue/<int:issue_id>")
@login_required
def Approve_issue(issue_id):
    if current_user.role !="Landlord":
        abort(403)
    properties = db.session.query(Properties, Issue).outerjoin(Properties, Properties.property_id == Issue.property_id).filter(Properties.landlord_id == current_user.user_id).filter(Issue.issue_id == issue_id).first()
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
    if current_user.role !=("Admin"):
        abort(403)
    form = IssueForm()
    if form.validate_on_submit():
        job = Jobs(issue=issue_id, summary= form.summary.data, content=form.content.data)
        db.session.add(job)
        db.session.commit()
        return redirect(url_for('Issue_page', issue_id=issue_id))
    return render_template("add_job.html", form=form, legend=("Create a Job"))

@app.route("/Job<int:job_id>")
@login_required
def Job(job_id):
    job = db.session.query(Jobs).filter(Jobs.job_id == job_id).first()
    quotes = db.session.query(Quotes).filter(Quotes.job == job_id).all()
    return render_template("Job.html", job=job, quotes=quotes)

@app.route("/Contractor/<int:user_id>")
@login_required
def Contractor(user_id):
    return redirect(url_for("home"))
# @app.route("/new_issue")
# def new_issue():
#     form = IssueForm()
#     if form.validate_on_submit():
