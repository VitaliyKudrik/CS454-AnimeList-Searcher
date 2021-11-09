from whoosh import qparser
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
from whoosh.index import open_dir
import pandas as pd


"""
This Searcher will search through the whoosh index that was created by the indexer.
It will provide back data in a form similar to dictionaries if you use the .fields() command on 
the returned results from anime_searcher. To search just type any query you like in string format.
By: Vitaliy Kudrik
"""


# This just opens the csv file for reading when creating the index.
def read_file(dataFile):
    # Get the data from the .csv file
    data = pd.read_csv(dataFile)
    # Make the data easily accessible in a dictionary
    list_data = data.to_dict('index')
    return list_data


# This searches for the user provided query and prints results_limit amount of results
def anime_searcher(user_query):
    # Change this number if you want more results
    results_limit = 9999
    # These are for the user to pick from when choosing OR queries or AND queries
    disjunctive = qparser.OrGroup
    conjunctive = qparser.AndGroup

    # Lets the user choose what kind of queries they want
    choice = "d"
    if choice.lower() == "c":
        choice = conjunctive
    elif choice.lower() == "d":
        choice = disjunctive
    else:
        # If we don't match to either of the expected results then go to a default of disjunctive
        choice = disjunctive

    # Open the index
    ix = open_dir("index")
    # To change scoring algo use: weighting=scoring.TF_IDF()
    with ix.searcher() as searcher:
        # We will have all the date from our anime in the parser except links
        multiparser = MultifieldParser(["Title", "Rating", "EpisodeCount", "Begin_date", "End_date", "Genres",
                                        "Description", "Producers"], schema=ix.schema, group=choice)
        # This was added to get some edit distance in our searching just in case users mistype
        # I'm not using it in this code directly but a user can type ~ after a word and have an edit distance
        multiparser.add_plugin(FuzzyTermPlugin())
        question_str = user_query.lower()
        print("My query = {}".format(user_query))
        # These are ways to restrict certain results or to filter for certain results, not used here for now
        # # restrict_q = Term("Title", "")
        # # allow_q = Term("Title", "")

        # Parse the question
        user_question = multiparser.parse(question_str)
        print(user_question.all_terms(), "\n\n")
        # Search the question
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


