from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from simpleApp.models import User, Employee


class RegistrationForms(FlaskForm):
    first_name = StringField(
        "First Name:", validators=[DataRequired(), Length(min=2, max=20)]
    )
    last_name = StringField(
        "Last Name:", validators=[DataRequired(), Length(min=2, max=20)]
    )

    personal_id = StringField(
        "Personal Number:", validators=[DataRequired(), Length(min=10, max=10)]
    )
    email = StringField("E-mail:", validators=[DataRequired(), Email()])
    country = SelectField(
        "Country:",
        choices=[
            ("Bel", "Belarus"),
            ("Wes", "Western Russia"),
            ("Ukr", "Ukrain"),
            ("Pol", "Poland"),
        ],
    )
    password = PasswordField("Password:", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password:", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_personal_id(self, personal_id):
        personal_id = User.query.filter_by(personal_id=personal_id.data).first()
        if personal_id:
            raise ValidationError(
                """This user is already exist! Refresh
                page or choose different identificator.
                """
            )

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(
                """This E-mail is been used! For you security protection
                purpose we strongly recommend to use only one E-mail
                per account. Make sure to typed correctly or choose another
                E-mail data!
                """
            )


class LoginForms(FlaskForm):
    personal_id = StringField(
        "Personal Number:", validators=[DataRequired(), Length(min=10, max=10)]
    )
    country = SelectField(
        "Country",
        choices=[
            ("Wes", "Western Russia"),
            ("Bel", "Belarus"),
            ("Ukr", "Ukrain"),
            ("Pol", "Poland"),
        ],
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_field = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

    def validate_personal_id(self, personal_id):
        user_personal_id = User.query.filter_by(personal_id=personal_id.data).first()
        employee_personal_id = Employee.query.filter_by(
            personal_id=personal_id.data
        ).first()

        if not user_personal_id and not employee_personal_id:
            raise ValidationError(
                """This user does not exist! Check correctness of your data.
                """
            )
