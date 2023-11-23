import jwt
import datetime

# Define a secret key for signing the JWT token
SECRET_KEY = 'lOtxle2-0K5kCebOXK9Pd7n8_q9QFZ4beTbSkQ7G0HA'

# Define a function to generate a JWT token
def generate_jwt_token(payload):
    # Set the expiration time for the token (optional)
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=365)

    # Create the token with the payload and the secret key
    token = jwt.encode({
        'payload': payload,
        'exp': expiration_time
    }, SECRET_KEY, algorithm='HS256')

    return token

# Generate a JWT token with a payload
payload = {
    'user_id': 123,
    'username': 'john_doe'
}
jwt_token = generate_jwt_token(payload)

print(jwt_token)

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjp7InVzZXJfaWQiOjEyMywidXNlcm5hbWUiOiJqb2huX2RvZSJ9LCJleHAiOjE3MjM2MTI0Nzl9.z4MBKlGw1H7P0j83_YNgWQE8wOhmCMnGn3HrL3xXDOM
