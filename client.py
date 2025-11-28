import requests

response = requests.post(url='http://127.0.0.1:8000/api/v1/user',
                          json={"name": "new user",
                                "password": "new password"})
print(response.status_code)
print(response.json())

response = requests.post(url='http://127.0.0.1:8000/api/v1/advertisement',
                          json={"title": "title test",
                                "description": "description test",
                                "price": 500,
                                "author_id": 1})
print(response.status_code)
print(response.json())

response = requests.get(url='http://127.0.0.1:8000/api/v1/advertisement/1')
print(response.status_code)
print(response.json())