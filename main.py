from flask import Flask
from flask import render_template, request, redirect
import random
import datetime
import requests
from searcher import anime_searcher
app = Flask(__name__)


# Deal with user queries
@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        data = request.form
        print(data)
    else:
        data = request.args
        x = data.get('search')
        print(data)
        x = x.strip()
        # Deal with bad user input or no input
        if x is not None and x != "":
            # Send you to the anime you want to see
            return redirect(f'/search/{x}')

    return render_template('index.html')


# Show the actual anime results. Hasn't been made presentable yet
@app.route('/search/<anime>')
def search(anime):
    results = anime_searcher(anime)
    pics = []
    for pic in results:
        pics.append(pic['Picture'])
    return render_template('search.html', name=anime, results=results, pics=pics)


if __name__ == "__main__":
    app.run(debug=True)
