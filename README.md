# Finvise API Documentation

This API allows users to perform various operations related to Finance such as registration, login, financial profile.

### Case 1: If you have docker installed, then run these following commands :-

    - docker compose build
    - docker compose up

### Case 2: Computer: Local Enviornment Setup

    1. Create and Enter virtual enviorment
          virtualenv env
          source env/bin/activate

    2. Install all dependencies
          pip3 install -r requirements.txt

    3. Setup Models
          python3 manage.py makemigrations
          python3 manage.py migrate

    4. Run server
          python3 manage.py runserver


## Base URL

```
http://127.0.0.1:8000/api/
```

## Endpoints

### 1. User Registration

- URL: /register/
- Method: POST
- Description: Registers a new user.
- Request Body:
  ```json
  {
      "username": "example_user",
      "password": "password123",
      "email": "user@example.com",
      "phone": "1234567890",
      "first_name": "John",
      "last_name": "Doe"
  }
  ```
- curl : 
  ```
  curl -X POST \
  http://127.0.0.1:8000/api/register/ \
  -H 'Content-Type: application/json' \
  -d '{
      "username": "example_user",
      "password": "password123",
      "email": "user@example.com",
      "phone": "1234567890",
      "first_name": "John",
      "last_name": "Doe"
  }'
  ```

- Response:
  ```json
  {
      "refresh": "<refresh_token>",
      "access": "<access_token>"
  }
  ```

### 2. User Login

- URL: /login/
- Method: POST
- Description: Logs in an existing user.
- Request Body:
  ```json
  {
      "username": "example_user",
      "password": "password123"
  }
  ```
  
- Curl :
  ```
  curl -X POST \
  http://127.0.0.1:8000/api/login/ \
  -H 'Content-Type: application/json' \
  -d '{
      "username": "example_user",
      "password": "password123"
  }'

  ```

- Response:
  ```json
  {
      "refresh": "<refresh_token>",
      "access": "<access_token>"
  }
  ```

### 3. Token Refresh

- URL: /refresh/
- Method: POST
- Description: Refreshes the access token.
- Request Body:
  ```json
  {
      "refresh": "<refresh_token>"
  }
  ```

- Curl :
  ```
  curl -X POST \
  http://127.0.0.1:8000/api/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{
      "refresh": "<refresh_token>"
  }'
  ```

  
- Response:

  ```json
  {
      "access": "<new_access_token>"
  }
  ```
