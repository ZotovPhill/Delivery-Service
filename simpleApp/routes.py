from flask import render_template, url_for, flash, redirect
from simpleApp.models import User, Employee, Package, Delivery, Location
from simpleApp.registrationForms import RegistrationForms, LoginForms
from simpleApp import app, db, bcrypt, login_manager
from flask_login import login_user, current_user, logout_user

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
        employee = Employee.query.filter_by(
            personal_id=login_form.personal_id.data
        ).first()
        if user:
            user_location = Location.query.filter_by(id=user.live_place).first()
        else:
            employee_location = Location.query.filter_by(
                id=employee.working_place
            ).first()

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
        elif (
            employee
            and bcrypt.check_password_hash(employee.password, login_form.password.data)
            and employee_location.country[:3] == login_form.country.data
        ):
            login_user(employee)
            return redirect(url_for("workspace"))
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


@app.route("/workspace")
def workspace():
    login_form = LoginForms()
    return render_template(
        "workspace.html",
        title="Workspace",
        login_form=login_form,
        username=current_user,
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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @login_manager.user_loader
# def load_employee(employee_id):
#     return Employee.query.get(int(employee_id))
