import email_validator
from email_validator import validate_email, EmailNotValidError

def check_email(email_address):
    try:
        # Check syntax and deliverability (DNS MX records)
        email_info = validate_email(email_address, check_deliverability=True)
        
        # Returns the normalized form of the email
        return f"Valid email! Normalized address: {email_info.normalized}"
        
    except EmailNotValidError as e:
        # Returns why the email is invalid (e.g., bad syntax or domain doesn't exist)
        return f"Invalid email: {str(e)}"