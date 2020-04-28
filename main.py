from flask import Flask, render_template, Response
import requests
from bs4 import BeautifulSoup
import threading
from flask_socketio import SocketIO, emit
import COVID19Py

global coronavirus
coronavirus = COVID19Py.COVID19()

app = Flask(__name__)
app.config["SECRET_KEY"] = "2e8fe3d23ehi23e7y"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:coronavirus@localhost/coronavirus"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
socket = SocketIO(app)
#db = SQLAlchemy(app)

global info


def cases_update_countries():
    threading.Timer(60.0,cases_update_countries)
    locations = coronavirus.getLocations(rank_by="confirmed")
    country_names = []
    for location in locations:
        if location["country"] not in country_names:
            country_names.append(location["country"])
    countries = []
    for name in country_names:
        deaths = 0
        confirmed = 0
        for location in locations:
            if location["country"] == name:
                deaths = deaths + location["latest"]["deaths"]
                confirmed = confirmed + location["latest"]["confirmed"]
        countries.append({"country":name,"deaths":deaths,"confirmed":confirmed})
    countries = sorted(countries, key=lambda country: country["confirmed"],reverse=True) 
    code1 = ""
    for country in countries:
        code1 = code1 + f"""<tr id="{country["country"]}"><td>{country['country']}</td><td>{ country["confirmed"] }</td><td>{country["deaths"]}</td></tr>"""
    code = code1
    return code1

def render_page(template, *args, **kwargs):
    return render_template("base.html", template=template, *args, **kwargs)

def coronavirus_cases():
    threading.Timer(20.0,coronavirus_cases)
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
code = cases_update_countries()

@socket.on("update request",namespace="/")
def update(info_updated):
    socket.emit("update",info,namespace='/')

@app.route("/")
def index():
    return render_page("index.html", cases=info["cases"], deaths=info["deaths"])

@app.route("/donate")
def donater():
    return render_page("donate.html")

@app.route('/countries')
def show_countries():
    global code
    return render_page("countries.html",code=code)

if __name__ == "__main__":
    socket.run(app,port=80,host="0.0.0.0")
