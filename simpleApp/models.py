from simpleApp import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    personal_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    live_place = db.Column(
        db.Integer, db.ForeignKey("location.id"), nullable=False, default="1"
    )
    password = db.Column(db.String(60), nullable=False)
    packages = db.relationship("Package", backref="owner", lazy=True)
    user_location = db.relationship("Location", backref="people", lazy=True)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', \
            '{self.personal_id}', '{self.live_place}')"


class Employee(db.Model, UserMixin):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    personal_id = db.Column(db.String(20), unique=True, nullable=False)
    working_place = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    verification_code = db.Column(db.String(60), unique=True, nullable=False)
    delivery_handler = db.relationship("Delivery", backref="operator", lazy=True)
    center_employee = db.relationship("Location", backref="workers", lazy=True)

    def __repr__(self):
        return f"Employee('{self.first_name}', '{self.last_name}', \
            '{self.personal_id}', '{self.working_place}')"


class Package(db.Model):
    __tablename__ = "package"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(60), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    parcel_weight = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    sent_from_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    sent_to_id = db.Column(db.Integer, db.ForeignKey("location.id"))

    sent_from = db.relationship(
        "Location", backref="from_place", foreign_keys=[sent_from_id]
    )
    sent_to = db.relationship("Location", backref="to_place", foreign_keys=[sent_to_id])
    description = db.Column(db.String(1000), nullable=False)
    creating_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    orders = db.relationship("Delivery", backref="parcel", lazy=True)

    def __repr__(self):
        return f"Package('{self.product_id}', '{self.user_id}', \
            '{self.sent_from}', '{self.sent_to}')"


association_table = db.Table(
    "association",
    db.Column("delivery_id", db.Integer, db.ForeignKey("delivery.id")),
    db.Column("location_id", db.Integer, db.ForeignKey("location.id")),
)


class Delivery(db.Model):
    __tablename__ = "delivery"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey("package.id"), nullable=False)
    processing_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Shipped")
    delivery_location = db.relationship(
        "Location",
        secondary=association_table,
        backref=db.backref("package_location", lazy="dynamic"),
    )


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(60), nullable=False)
    city = db.Column(db.String(60), nullable=False, unique=True)

    def __repr__(self):
        return f"Location('{self.country}', '{self.city}')"
