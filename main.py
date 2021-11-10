from flask import Flask
from flask import render_template, request, redirect
from searcher import anime_searcher
from math import ceil

app = Flask(__name__)


# Helper function to fill the global anime holder properly
def global_anime_creator(results):
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
@app.route('/', methods=['GET'])
def homepage():
    if request.method == 'GET':
        data = request.args
        x = data.get('search')
        # Deal with bad user input or no input
        if x is not None and x != "":
            x = x.strip()
            # Send you to the anime you want to see
            return redirect(f'/search/{x}/0')

    return render_template('/index.html')


# Global value to keep track of current searching
current_search = ""
gbl_results = {}


# Show the actual anime results. Hasn't been made presentable yet
@app.route('/search/<anime>/<page>', methods=['GET'])
def search(anime, page):
    global current_search
    global gbl_results

    # If the user submits a new query we handle it here
    if request.method == 'GET':
        data = request.args
        x = data.get('search')
        # Deal with bad user input or no input
        if x is not None and x != "":
            # Strip here just to avoid a few issues
            x = x.strip()
            if x != "":
                # Send you to the anime you want to see
                return redirect(f'/search/{x}/0')

    # If the search is empty then we set the current anime and get new results
    if current_search == "":
        current_search = anime
        results = anime_searcher(anime)
        global_anime_creator(results)
    # If we are on the same query and looking at different pages then don't recalculate
    elif current_search == anime:
        pass
    # If the search isn't empty, but we have a new query then we set the current anime and get new results
    else:
        current_search = anime
        results = anime_searcher(anime)
        global_anime_creator(results)
    # The amount of pages of 10 results each max.
    pages = len(gbl_results)
    # This is for checking the length of the last page with 10 results, just in case it has less than 10
    curr_page_len = 0
    # Int value of the current page, used in comparison on html page
    i_page = 0
    # Check if the page is valid in case a user types their own page number on the browser search bar
    if page.isdigit():
        # Make sure it's a valid page within range
        if int(page) < pages:
            # Set the values for the html page to see
            curr_page_len = len(gbl_results[page])
            i_page = int(page)
    # I don't think we need more than 48 pages, and it also fits perfectly in our results if there are 48.
    if pages > 48:
        pages = 48
    # Render the template and send the data to the page
    return render_template('result.html', name=anime, results=gbl_results, pages=pages, page=page, i_page=i_page,
                           curr_page_len=curr_page_len)


if __name__ == "__main__":
    app.run(debug=True)


