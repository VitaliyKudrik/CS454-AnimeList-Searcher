from flask import Flask
from flask import render_template, request, redirect
from searcher import anime_searcher, upper_genres
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


# This is just a helper function for cleaner code. It sets the filters for post results filtering
def filter_setter(data):
    global filter_reverse
    global curr_filter

    # Find the filter
    f_rating = data.get('rating')
    f_episodes = data.get('episodes')
    f_air_date = data.get('air_date')
    # Set the current filter
    if f_rating:
        if curr_filter != 'rating':
            curr_filter = "rating"
            filter_reverse = True
        else:
            if filter_reverse:
                filter_reverse = False
            else:
                filter_reverse = True
    elif f_episodes:
        if curr_filter != 'episodes':
            curr_filter = "episodes"
            filter_reverse = True
        else:
            if filter_reverse:
                filter_reverse = False
            else:
                filter_reverse = True
    elif f_air_date:
        if curr_filter != 'air_date':
            curr_filter = "air_date"
            filter_reverse = True
        else:
            if filter_reverse:
                filter_reverse = False
            else:
                filter_reverse = True


# Deal with user queries
@app.route('/', methods=['GET'])
def homepage():
    if request.method == 'GET':
        data = request.args
        user_query = data.get('search')
        for thing in data:
            my_field = data.get(thing)
            if thing != "genre_holder[]":
                if my_field is not None and my_field != "":
                    print(thing, my_field)
        # These are the genres from the check box
        adv_genres = data.getlist('genre_holder[]')
        print(adv_genres)
        
        # Deal with bad user input or no input
        if user_query is not None and user_query != "":
            user_query = user_query.strip()
            # Send you to the anime you want to see
            return redirect(f'/search/{user_query}/0')
    return render_template('index.html', genres=upper_genres, len_genres=len(upper_genres))


# Global value to keep track of current searching
current_search = ""
gbl_results = {}
# Current filter settings
curr_filter = None
filter_reverse = True
# Description toggle
desc = 1


# Show the actual anime results. Hasn't been made presentable yet
@app.route('/search/<anime>/<page>', methods=['GET', 'POST'])
def search(anime, page):
    global current_search
    global gbl_results
    global curr_filter
    global filter_reverse
    global desc

    # This is for the rank button
    no_filter = False

    if request.method == 'GET':
        data = request.args
        user_query = data.get('search')
        # This will set the global variables for filters
        filter_setter(data)
        if data.get("rank") is not None:
            no_filter = True
            curr_filter = None
            filter_reverse = True
        # Deal with bad user input or no input
        if user_query is not None and user_query != "":
            # Strip here just to avoid a few issues
            user_query = user_query.strip()
            if user_query != "":
                # Send you to the anime you want to see
                return redirect(f'/search/{user_query}/0')
        if data.get("desc") is not None:
            if desc:
                desc = 0
            else:
                desc = 1
    # If the search is empty then we set the current anime and get new results
    if current_search == "":
        current_search = anime
        results = anime_searcher(anime)
        global_anime_creator(results)
    # If we are on the same query and looking at different pages then don't recalculate
    elif current_search == anime:
        if curr_filter is not None and no_filter is False:
            results = anime_searcher(anime, curr_filter, filter_reverse)
            global_anime_creator(results)
        else:
            results = anime_searcher(anime)
            global_anime_creator(results)

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
    # Pagination
    begin_page = i_page
    end_page = int(pages)
    total_pages = int(pages)
    if begin_page - 5 <= 0:
        begin_page = 0
        if end_page > 10:
            end_page = 10
    elif abs(begin_page - end_page) < 5:
        begin_page = end_page - 10
        end_page = end_page
    else:
        if begin_page + 5 > total_pages:
            end_page = total_pages
        else:
            end_page = begin_page + 5
        begin_page = begin_page - 5

    # print("pages = {} \t page = {} \t i_page = {} \t curr_page_len = {}".format(pages, page, i_page, curr_page_len))
    # Render the template and send the data to the page
    return render_template('result.html', name=anime, results=gbl_results, pages=pages, page=page, i_page=i_page,
                           curr_page_len=curr_page_len, begin_page=begin_page, end_page=end_page, desc=desc)


if __name__ == "__main__":
    app.run(debug=True)
