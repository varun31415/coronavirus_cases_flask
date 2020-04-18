from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import threading

app = Flask(__name__)
global info

def coronavirus_cases():
    try:
        threading.Timer(4.0, coronavirus_cases).start()
    except: 
        pass
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
    return {"cases":cases, "deaths":deaths, "output":output}

info = coronavirus_cases()

@app.route("/")
def index():
    global info
    return render_template("index.html", cases=info["cases"],deaths=info["deaths"])

if __name__ == "__main__":
    app.run(port=8000,host="0.0.0.0")