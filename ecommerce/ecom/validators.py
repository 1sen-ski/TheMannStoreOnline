from django.core.exceptions import ValidationError


def validate_card_number(value):
    card_number = ''.join(value.split())
    if not card_number.isdigit() or len(card_number) != 16:
        raise ValidationError("Invalid card number. Please enter a 16-digit number with no spaces.")


def validate_expiry_date(value):
    try:
        month, year = value.split(' - ')
        if not (1 <= int(month) <= 12) or not (22 <= int(year) <= 29):
            raise ValidationError("Invalid expiry date. Please select a valid month and year.")
    except ValueError:
        raise ValidationError("Invalid expiry date format. Please select a valid month and year.")


def validate_cv_code(value):
    if not value.isdigit() or len(value) != 3:
        raise ValidationError("CV code should be a 3-digit number.")


def validate_mobile_for_payment(value):
    if not value.isdigit():
        raise ValidationError("Mobile number should contain only digits.")
    if len(value) < 10 or len(value) > 15:
        raise ValidationError("Mobile number should be between 10 and 15 digits.")


def validate_nonnegative(value):
    if value < 0:
        raise ValidationError("Value must be non-negative.")


def validate_name(value):
    if len(value) < 3 or len(value) > 15:
        raise ValidationError("Name should be between 3 and 15 characters.")


def validate_username(value):
    if len(value) < 3 or len(value) > 15 or ' ' in value:
        raise ValidationError("Username should be between 3 and 15 characters with no spaces.")


def validate_password(value):
    if len(value) < 6 or len(value) > 20 or ' ' in value:
        raise ValidationError("Password should be between 6 and 20 characters with no spaces.")


def validate_password_numbers(value):
    if sum(c.isdigit() for c in value) < 2:
        raise ValidationError("Password should contain at least 2 numbers.")


def validate_mobile(value):
    if len(value) < 10:
        raise ValidationError("Mobile number should be a sequence of at least 10 digits.")

