from flask import Flask, render_template, Response
import requests
from bs4 import BeautifulSoup
import threading
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "2e8fe3d23ehi23e7y"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:coronavirus@localhost/coronavirus"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
socket = SocketIO(app)
#db = SQLAlchemy(app)

global info

def render_page(template, *args, **kwargs):
    return render_template("base.html", template=template, *args, **kwargs)

def coronavirus_cases():
    global socket
    threading.Timer(4.0,coronavirus_cases)
    res = requests.get('https://www.worldometers.info/coronavirus/')
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)
    output = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        'style'
        # there may be more elements you don't want, such as "style", etc.
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

    cases = ""
    deaths = ""
    state = False
    state1 = False
    num = 0
    num1 = 0
    state2 = False
    for char in output:
        num = num + 1
        if num == 28:
            state = True
        if state:
            cases = cases + char
            if char == " ":
                state = False
                state1 = True
        if state1:
            num1 = num1 + 1
        if num1 == 12:
            state2 = True
        if state2:
            deaths = deaths + char
            if char == " ":
                state2 = False 
    info = {"cases":cases,"deaths":deaths}
    return {"cases":cases, "deaths":deaths}


info = coronavirus_cases()

@socket.on("update request")
def update(info_updated):
    socket.emit("update",info)

@app.route("/")
def index():
    return render_page("index.html", cases=info["cases"], deaths=info["deaths"])

@app.route("/donate")
def donater():
    return render_page("donate.html")

if __name__ == "__main__":
    socket.run(app,port=80,host="0.0.0.0")
