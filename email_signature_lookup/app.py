from flask import Flask
import requests
app = Flask(__name__)

@app.route("/<email>")
def index(email):
    url = "FunctionAppURL"
    parameters = {
        "email": email
    }
    response = requests.get(url, params=parameters)
    return response.text

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)