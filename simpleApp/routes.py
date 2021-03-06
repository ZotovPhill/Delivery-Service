from flask import render_template, url_for, flash, redirect, request
from simpleApp.models import User, Employee, Package, Delivery, Location
from simpleApp.registrationForms import (
    RegistrationForms,
    LoginForms,
    UpdateForms,
    NewPackageForm,
)
from simpleApp import app, db, bcrypt, login_manager
from flask_login import login_user, current_user, logout_user, login_required
import uuid

import secrets

delivery_list = [
    {
        "order_id": 1,
        "product_id": "5xHc391YUI-FX505DY-BQ024",
        "product_name": "Игровой ноутбук ASUS TUF Gaming FX505DY-BQ024",
        "parcel_weight": 180,
        "sent_from": "Moskow",
        "sent_to": "Warshaw",
        "status": "Shipped",
    },
    {
        "order_id": 2,
        "product_id": "S340-15IWL-81N8013ERK",
        "product_name": "Ноутбук Apple MacBook Pro 13 'Touch Bar 2019 MV992'",
        "parcel_weight": 60,
        "sent_from": "Brest",
        "sent_to": "Moskow",
        "status": "Shipped",
    },
]


@app.route("/home", methods=["GET", "POST"])
def home():
    login_form = LoginForms()

    if login_form.validate_on_submit():
        user = User.query.filter_by(personal_id=login_form.personal_id.data).first()
        user_location = Location.query.filter_by(id=user.live_place).first()
        if (
            user
            and bcrypt.check_password_hash(user.password, login_form.password.data)
            and user_location.country[:3] == login_form.country.data
        ):
            login_user(user)
            flash(
                f"""Welcome, {user.first_name}! You have been
                successfully logged in to your cabinet!
                """,
                "success",
            )
            return redirect(url_for("home"))
        else:
            flash("Authorization failled. Try another ID or Password", "danger")
    return render_template(
        "home.html",
        delivery_list=delivery_list,
        personal_id=current_user,
        login_form=login_form,
        username=current_user,
    )


@app.route("/register", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    login_form = LoginForms()
    registration_form = RegistrationForms()
    personal_id = secrets.token_hex(5)
    if registration_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            registration_form.password.data
        ).decode("utf-8")
        country_on_form = registration_form.country.data
        location = (
            db.session.query(Location)
            .filter(Location.country.like(f"%{country_on_form}%"))
            .first()
        )
        user = User(
            first_name=registration_form.first_name.data,
            last_name=registration_form.last_name.data,
            personal_id=personal_id,
            email=registration_form.email.data,
            live_place=location.id,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
        flash(
            f"Your account {registration_form.personal_id.data} has been created successfully!",
            "success",
        )
        return redirect(url_for("home"))

    return render_template(
        "registration.html",
        registration_form=registration_form,
        title="Registration Form",
        personal_id=personal_id,
        login_form=login_form,
    )


@app.route("/workspace", methods=["GET", "POST"])
def workspace():
    login_form = LoginForms()
    update_form = UpdateForms()
    user_location = Location.query.filter_by(id=current_user.live_place).first()
    if update_form.validate_on_submit():
        current_user.first_name = update_form.first_name.data
        current_user.last_name = update_form.last_name.data
        current_user.email = update_form.email.data
        current_user.live_place = update_form.country.data
        db.session.commit()
        flash("Your account has been updated", "success")
        return redirect(url_for("workspace"))
    elif request.method == "GET":
        update_form.first_name.data = current_user.first_name
        update_form.last_name.data = current_user.last_name
        update_form.email.data = current_user.email
        update_form.country.data = current_user.live_place

    packages = Package.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "workspace.html",
        title="Workspace",
        packages=packages,
        login_form=login_form,
        username=current_user,
        location=f"{user_location.country}, {user_location.city}",
        update_form=update_form,
    )


@app.route("/about")
def about():
    login_form = LoginForms()
    return render_template(
        "about.html",
        delivery_list=delivery_list,
        personal_id="669f6febaa",
        login_form=login_form,
    )


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/workspace/package", methods=["GET", "POST"])
@login_required
def new_package():
    login_form = LoginForms()
    new_package_form = NewPackageForm()
    product_id = str(uuid.uuid4())
    if new_package_form.validate_on_submit():
        from_city_on_form = new_package_form.sent_from.data
        to_city_on_form = new_package_form.sent_to.data
        location_from = (
            db.session.query(Location)
            .filter(Location.city.like(f"%{from_city_on_form}%"))
            .first()
        )
        location_to = (
            db.session.query(Location)
            .filter(Location.city.like(f"%{to_city_on_form}%"))
            .first()
        )

        package = Package(
            product_id=product_id,
            product_name=new_package_form.product_name.data,
            parcel_weight=new_package_form.parcel_weight.data,
            user_id=current_user.id,
            sent_from=location_from,
            sent_to=location_to,
            description=new_package_form.description.data,
        )
        db.session.add(package)
        db.session.commit()
        flash("New Package has been created!", "success")
        return redirect(url_for("workspace"))

    return render_template(
        "new_package.html",
        title="New Package",
        login_form=login_form,
        new_package_form=new_package_form,
        product_id=product_id,
    )


@app.route("/workspace/package/<int:package_id>")
def updata_package(package_id):
    package = Package.query.get_or_404(package_id)
    return render_template("update_package.html", title=package.id, package=package)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @login_manager.user_loader
# def load_employee(employee_id):
#     return Employee.query.get(int(employee_id))

# employee = Employee.query.filter_by(
#     personal_id=login_form.personal_id.data
# ).first()
# if user:

# else:
# employee_location = Location.query.filter_by(
#     id=employee.working_place
# ).first()


# elif (
#     employee
#     and bcrypt.check_password_hash(employee.password, login_form.password.data)
#     and employee_location.country[:3] == login_form.country.data
# ):
#     login_user(employee)
#     return redirect(url_for("workspace"))
