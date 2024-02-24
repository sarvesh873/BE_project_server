import requests

new_data = {

    "username": "abcs",
    "password": "Admin@1234",
    "title": "Making a POST request",
    "body": "This is the data we created."
}

# The API endpoint to communicate with
url_post = "http://127.0.0.1:8000/api/login/"

# A POST request to tthe API
post_response = requests.post(url_post, json=new_data)

# Print the response
post_response_json = post_response.json()
print(post_response_json)