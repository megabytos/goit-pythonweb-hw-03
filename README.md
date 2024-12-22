# Python Web Development HomeWork 3 - HTTP Web Server with jinja template

## Running the server
To run the server with docker, execute the following command:

```bash
docker-compose up
```
To run the server without docker, execute the following commands:

```bash
python -m pip install poetry

poetry install

python main.py
```

The application runs on port 3000: (http://localhost:3000)

## Features of HTTP Web Server
* Processing GET requests:  routing and returning static content
* Processing POST requests:  saving form data to a JSON file
* Returning saved JSON data as a rendered template