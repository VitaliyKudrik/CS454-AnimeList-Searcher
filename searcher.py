from whoosh import qparser, sorting
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
from whoosh.index import open_dir
import pandas as pd

"""
This Searcher will search through the whoosh index that was created by the indexer.
It will provide back data in a form similar to dictionaries if you use the .fields() command on 
the returned results from anime_searcher. To search just type any query you like in string format.
By: Vitaliy Kudrik
"""

# These are used for filtering out other genres
genres = ["action", "adventure", "avant garde", "award winning", "boys love", "comedy", "drama", "fantasy",
          "girls love", "gourmet", "horror", "mystery", "romance", "sci-fi", "slice of life", "sports", "supernatural",
          "suspense", "work life", "ecchi", "cars", "demons", "game", "harem", "historical", "martial arts", "mecha",
          "military", "music", "parody", "police", "psychological", "samurai", "school", "space", "super power",
          "vampire", "josei", "kids", "seinen", "shoujo", "shounen"]


# This just opens the csv file for reading when creating the index.
def read_file(dataFile):
    # Get the data from the .csv file
    data = pd.read_csv(dataFile)
    # Make the data easily accessible in a dictionary
    list_data = data.to_dict('index')
    return list_data


# This searches for the user provided query and prints results_limit amount of results
def anime_searcher(user_query, my_filter="", is_reverse=False):
    # Change this number if you want more results
    results_limit = 9999
    # These are for the user to pick from when choosing OR queries or AND queries
    disjunctive = qparser.OrGroup
    # conjunctive = qparser.AndGroup

    # Open the index
    ix = open_dir("index")
    # To change scoring algo use: weighting=scoring.TF_IDF()
    with ix.searcher() as searcher:
        # We will have all the date from our anime in the parser except links
        multiparser = MultifieldParser(["Title", "Rating", "EpisodeCount", "Begin_date", "End_date", "Genres",
                                        "Description", "Producers"], schema=ix.schema, group=disjunctive)

        # This was added to get some edit distance in our searching just in case users mistype
        # I'm not using it in this code directly but a user can type ~ after a word and have an edit distance
        multiparser.add_plugin(FuzzyTermPlugin())
        question_str = user_query.lower()
        multiparser.add_plugin(qparser.GtLtPlugin)
        multiparser.remove_plugin_class(qparser.WildcardPlugin)
        # These are ways to restrict certain results or to filter for certain results, not used here for now
        # allow_q = Term("Title", "")

        # Facet which will sort data by rating, the numeric rating didn't work so we are using True_rating
        rating_facet = sorting.FieldFacet('True_rating')
        # Facet which will sort data by episode count
        episode_facet = sorting.FieldFacet('EpisodeCount')
        # Facet which will sort data by date
        date_facet = sorting.FieldFacet('Begin_date')
        # Parse the question
        user_question = multiparser.parse(question_str)
        # Search the question and check for filtering
        if my_filter == "rating":
            # If is_reverse is true then we reverse the results
            if is_reverse:
                results = searcher.search(user_question, limit=results_limit, sortedby=rating_facet, reverse=True)
            else:
                results = searcher.search(user_question, limit=results_limit, sortedby=rating_facet, reverse=False)
        elif my_filter == "air_date":
            if is_reverse:
                results = searcher.search(user_question, limit=results_limit, sortedby=date_facet, reverse=True)
            else:
                results = searcher.search(user_question, limit=results_limit, sortedby=date_facet, reverse=False)
        elif my_filter == "episodes":
            if is_reverse:
                results = searcher.search(user_question, limit=results_limit, sortedby=episode_facet, reverse=True)
            else:
                results = searcher.search(user_question, limit=results_limit, sortedby=episode_facet, reverse=False)
        else:
            results = searcher.search(user_question, limit=results_limit)

        # Holder for all the anime we will find
        return_this = []
        # Counter to make sure we loop properly
        results_counter = len(results)
        # Counter to make sure we loop properly
        counter = 0
        # Stop once we hit 0
        while results_counter > 0:
            # Add the dictionary data to the list
            return_this.append(results[counter].fields())
            counter += 1
            results_counter -= 1
        # Return the list of anime
        return return_this

# x = anime_searcher("Action Vampire Romance")
# for anime in x:
#     print(anime['Title'], "\t\t", anime['True_genres'], anime['True_date'])
