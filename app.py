from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():

    return "This is our first flask application"

if __name__ == "__main__":
    app.run(debug=True)# 5000