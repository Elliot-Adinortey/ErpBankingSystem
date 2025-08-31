import secrets
import os
from datetime import datetime, timedelta
from src.utils.email_service import send_email

# dictionary to store password reset token
reset_tokens = {}

# dictionary to store rate limiting information
reset_requests = {}

# constants for the rate limiting
RESET_LIMIT = 5
RESET_WINDOW = timedelta(minutes=15)

def can_request_reset(username):
    now = datetime.now()
    if username not in reset_requests:
        reset_requests[username] = (now, 0)
        return True

    last_request_time, request_count = reset_requests[username]
    if now - last_request_time > RESET_WINDOW:
        reset_requests[username] = (now, 0)
        return True

    if request_count < RESET_LIMIT:
        reset_requests[username] = (last_request_time, request_count + 1)
        return True

    return False

def initiate_password_reset(users, username):
    if username in users:
        if can_request_reset(username):
            user = users[username]
            token = secrets.token_urlsafe(16)
            expiry = datetime.now() + timedelta(hours=1)
            reset_tokens[token] =(username, expiry)
            base_url = os.getenv("BASE_URL")
            reset_link = f"{base_url}/reset_password?token={token}"
            send_email(user.email,"Passeword Reset", f"Use the following link to reset your password: {reset_link}")
            print(f"Password reset email sent to {user.email}.")
        else:
            print("Error: Too many password reset requests. Please try again later.")
    else:
        print("Error: User not found.")


def reset_password(users, token, new_password):
    if token in reset_tokens:
        username, expiry = reset_tokens[token]
        if datetime.now() < expiry:
            user = users[username]
            if len(new_password) < 6:
                print("Error: Password must be at least 6 characters long")
                return
            user.set_password(new_password)
            del reset_tokens[token]
            print("Password reset successful")
        else:
            print("Error: Token has expired")
            del reset_tokens[token]
    else:
        print("Error: Invalid token.")

