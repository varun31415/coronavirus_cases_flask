from flask import Flask, render_template, Response
import requests
from bs4 import BeautifulSoup
import threading
from flask_socketio import SocketIO, emit
import COVID19Py

global coronavirus
coronavirus = COVID19Py.COVID19(data_source="jhu")# jhu, nyt, csbs
csbs = COVID19Py.COVID19(data_source="nyt")

app = Flask(__name__)
app.config["SECRET_KEY"] = "2e8fe3d23ehi23e7y"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:coronavirus@localhost/coronavirus"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
socket = SocketIO(app)
#db = SQLAlchemy(app)

global info

def toInt(string):
    result = ""
    for char in string:
        try: print(int(char))
        except: pass
        else: result = result + char
    return int(result)

"""def cases_update_countries():
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
        if country["country"] != "US":
            code1 = code1 + f"""#<tr id="{country["country"]}"><td>{country['country']}</td><td>{ country["confirmed"] }</td><td>{country["deaths"]}</td></tr>"""
"""     else: 
            counties = csbs.getLocations(rank_by="confirmed")
            deaths = 0 
            confirmed = 0 
            for county in counties:
                deaths = deaths + county["latest"]["deaths"]
                confirmed = confirmed + county["latest"]["confirmed"]
            code1 = code1 + f"""#<tr id="{country["country"]}"><td>{country['country']}</td><td>{ confirmed }</td><td>{ deaths }</td></tr>"""
""" code = code1
    return code1"""


def cases_country(country):
    res = requests.get(f'https://www.worldometers.info/coronavirus/country/{country.lower()}')
    print(f'https://www.worldometers.info/coronavirus/country/{country.lower()}')
    if country == "us":
        country = "United States"
    if country == "uk":
        country = "United Kingdom"
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
    output = output[0:500]
    state1 = False
    state2 = False
    state3 = False 
    cases = ""
    deaths = ""
    num1 = 0
    num2 = 0
    for char in output:
        num1 = num1 + 1
        if num1 == (15 + len(country)):
            state1 = True
            state3 = True
        if state1 and state3:
            cases = cases + char 
            if char == " ":
                state1 = False
                state3 = False
                state2 = True
        if state2 and not state1:
            num2 = num2 + 1
        if num2 == 12:
            state1 = True
        if state2 and state1:
            deaths = deaths + char
            if char == " ":
                state1 = False
                state2 = False

    outputs = output.split("\n")
    output = ""
    for line in outputs:
        output = output + line
    output2 = output.split(cases)[2].split(deaths)[1].split("Recovered: ")[1]
    recovered = ""
    state1 = False
    for char in output2:
        if char != " ":
            state1 = True
        if state1: 
            recovered = recovered + char 
            if char == " ":
                state1 = False
                break 
    return {"cases":cases,"deaths":deaths,"output":output2,"recovered":recovered}

def cases_update_two_countries():
    threading.Timer(50.0,cases_update_two_countries)
    table_code2 = ""
    countries = ["US","Spain","Italy","France","UK","Germany","Turkey","Russia","Iran","China","Brazil","Canada","Belgium","Netherlands","India","Peru","Switzerland"]
    data = []
    for country in countries:
        info1 = cases_country(country.lower())
        data.append({"cases":info1["cases"],"deaths":info1["deaths"],"country":country,"recovered":info1["recovered"]})
    data_new = []
    for country in data:
        top_country = country 
        print("country is "+country["country"])
        for country2 in data:
            if toInt(country2["cases"]) > toInt(top_country["cases"]) and country2 not in data_new:
                print(country2["cases"] + " > " + top_country["cases"])
                top_country = country2
            else:
                print(country2["cases"] + " < " + top_country["cases"])
        print(f"""top country is {top_country['country']}""")
        data_new.append(top_country)
    data = data_new
    print(data_new)
    #for country in data:
    #   print(country["cases"])
    for country in data:
        table_code2 = table_code2 + f"""<tr id="{country["country"]}"><td>{country['country']}</td><td>{ country["cases"] }</td><td>{ country["deaths"] }</td><td>{country["recovered"]}</td></tr>"""
    table_code = table_code2
    return table_code

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
    output = output[0:50]
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
#code = cases_update_countries()
table_code = cases_update_two_countries()

@socket.on("update request",namespace="/")
def update(info_updated):
    socket.emit("update",info,namespace='/')

@app.route("/")
def index():
    return render_page("index.html", cases=info["cases"], deaths=info["deaths"])

@app.route("/donate")
def donater():
    return render_page("donate.html")

#@app.route('/countries/')
#def show_countries():
#    global code
#    return render_page("countries.html",code=code)
@app.route("/countries/")
def show_countries2():
    global table_code 
    return render_page("countries.html",code=table_code)

@app.route("/country/<country>")
def country(country):
    return cases_country(country)["recovered"]# 60,495

if __name__ == "__main__":
    socket.run(app,port=80,host="0.0.0.0")
