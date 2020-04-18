from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import threading

app = Flask(__name__)
global info

def coronavirus_cases():
    try:
        threading.Timer(5.0, coronavirus_cases).start()
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
    state = False
    num = 0
    for char in output:
        num = num + 1
        if num == 28:
            state = True
        if state:
            cases = cases + char
            if char == " ":
                state = False
    
    deaths = ""
    state = False
    num = 0
    for char in output:
        num = num + 1
        if num == 48:
            state = True
        if state:
            deaths = deaths + char
            if char == " ":
                state = False

    return {"cases":cases, "deaths":deaths}

info = coronavirus_cases()

@app.route("/")
def index():
    global info
    return render_template("index.html",cases=info["cases"],deaths=info["deaths"])

if __name__ == "__main__":
    app.run(port=8000,host="0.0.0.0")