from flask import Flask
from flask import render_template, request, redirect
import random
import datetime
import requests
from searcher import anime_searcher
from math import ceil

app = Flask(__name__)


# Helper function to fill the global anime holder properly
def global_anime_creater(results):
    global gbl_results
    gbl_results = {}
    # Get the amount of pages
    pages = int((ceil(len(results) / 10) * 10) / 10)
    # This will keep track of which anime we are on
    anime_count = 0
    # This will hold 10 anime which we will add to our global results
    temp = []
    # For as many pages of top 10 results that we have
    for i in range(0, pages):
        # Get the ten pages for that page
        for _ in range(0, 10):
            temp.append(results[anime_count])
            anime_count += 1
            # Make sure we stop at the right place
            if anime_count > len(results) - 1:
                break
        # Add the 10 pages to the global results
        gbl_results[str(i)] = temp
        # Reset temp for the next 10 pages
        temp = []


# Deal with user queries
@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        data = request.form
    else:
        data = request.args
        x = data.get('search')
        # Deal with bad user input or no input
        if x is not None and x != "":
            x = x.strip()
            # Send you to the anime you want to see
            return redirect(f'/search/{x}/0')

    return render_template('index.html')


# Global value to keep track of current searching
current_search = ""
gbl_results = {}


# Show the actual anime results. Hasn't been made presentable yet
@app.route('/search/<anime>/<page>')
def search(anime, page):
    global current_search
    global gbl_results
    # Get the amount of pages in the results

    if current_search == "":
        current_search = anime
        results = anime_searcher(anime)
        global_anime_creater(results)

    elif current_search == anime:
        pass
    else:
        current_search = anime
        results = anime_searcher(anime)
        global_anime_creater(results)
    pages = len(gbl_results)
    curr_page_len = len(gbl_results[page])

    # pics = []
    # for pic in gbl_results:
    #     pics.append(pic['Picture'])
    # I don't think we need more than 48 pages, and it also fits perfectly in our results if there are 48.
    if pages > 48:
        pages = 48
    return render_template('result.html', name=anime, results=gbl_results, pages=pages, page=page, i_page=int(page),
                           curr_page_len=curr_page_len)




if __name__ == "__main__":
    app.run(debug=True)
    #app.run()

