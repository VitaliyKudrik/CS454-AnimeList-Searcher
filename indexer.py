from whoosh.analysis import RegexTokenizer, StopFilter

from dateparsing import *
from whoosh import index
from whoosh.fields import Schema, TEXT, DATETIME, NUMERIC
import os
import pandas as pd
import datetime


"""
This indexer will read a CSV file with certain data and will then create a whoosh
index that can be searched using the searcher.py
By: Vitaliy Kudrik
"""

# This is for the true date, just to make user experience better
inverse_months = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul",
                  8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}


# This just opens the csv file for reading when creating the index.
def read_file(dataFile):
    # Get the data from the .csv file
    data = pd.read_csv(dataFile)
    # Make the data easily accessible in a dictionary
    list_data = data.to_dict('index')
    return list_data


# Creates the index we will search
def create_index():
    data = read_file("top_17665_anime_final_clean.csv")
    # Schema which will hold all of our data
    schema = Schema(Title=TEXT(stored=True), True_title=TEXT(stored=True), Rating=NUMERIC(stored=True, sortable=True),
                    Link=TEXT(stored=True), Picture=TEXT(stored=True), EpisodeCount=NUMERIC(stored=True, sortable=True),
                    Begin_date=DATETIME(stored=True, sortable=True), End_date=DATETIME(stored=True, sortable=True),
                    Genres=TEXT(stored=True), True_description=TEXT(stored=True), Description=TEXT(stored=True),
                    True_genres=TEXT(stored=True), True_date=TEXT(stored=True), Producers=TEXT(stored=True),
                    True_rating=TEXT(stored=True), True_episode_count=TEXT(stored=True))
    # If the directory doesn't exist then we create it
    if not os.path.exists("index"):
        os.mkdir("index")
    # Create the index
    ix = index.create_in("index", schema)
    # Init the writer
    writer = ix.writer()
    # Go through all the data in our csv file
    for i in range(0, len(data)):
        date_holder = date_parser(data[i]["Airing Dates"])
        print(i, data[i]["Title"])
        # Get the episode count and if there isn't one give it a big number which we will ignore in searching
        episode_count = data[i]["Episode Count"]
        if episode_count.strip() == "Unknown":
            # Give a episode count of 0 so that we can filter it out when needed
            episode_count = 0
            # Used to make user experience better
            true_episode_count = "Still Airing"
        else:
            # Turn the episode count data into an int if it isn't already.
            episode_count = int(episode_count)
            # Used to make user experience better
            true_episode_count = str(episode_count)

        # Get the rating and if there isn't one give it a big number which we will ignore in searching
        anime_rating = data[i]["Rating"]
        # Because an empty field is a float for some reason, we check for nan using nan != nan
        if anime_rating != anime_rating:
            # Give a rating of 0 so that we can filter it out when needed
            anime_rating = 0
            true_rating = "Unrated"
        else:
            # Used to make user experience better
            true_rating = str(anime_rating)

        # Check if the anime has producers
        anime_producers = data[i]["Producers"]
        # Because an empty field is a float for some reason, we check for nan using nan != nan
        if anime_producers != anime_producers:
            # Since there were no producers we just write that there isn't any
            anime_producers = "No_Producers"

        # Check if the anime has genres since a select few small specials don't have genres
        anime_genres = data[i]["Genres"]
        # Initialize search genres
        search_genres = ""
        # Because an empty field is a float for some reason we check for nan using nan != nan
        if anime_genres != anime_genres:
            # Since there were no producers we just write that there isn't any
            anime_genres = "None"
        else:
            # Make the genres lower case for ease of searching
            search_genres = anime_genres.lower()
        # Create the datetime objects
        begin_date = datetime.datetime(date_holder[0][0], date_holder[0][1], date_holder[0][2])
        end_date = datetime.datetime(date_holder[1][0], date_holder[1][1], date_holder[1][2])
        # This is a str holder for the date that will be presented to users
        true_date = ""
        # This is just for displaying a nice date to users quickly
        true_begin = begin_date.strftime("%m-%d-%Y")
        true_end = end_date.strftime("%m-%d-%Y")

        true_begin = true_begin.split("-")
        true_begin[0] = inverse_months[int(true_begin[0])]
        true_begin = "-".join(true_begin)

        true_end = true_end.split("-")
        true_end[0] = inverse_months[int(true_end[0])]
        true_end = "-".join(true_end)

        # Deal with movies and one offs that start and end same day
        if begin_date == "Not available":
            true_date = "Not available"
        else:
            if begin_date == end_date:
                if true_begin == 'Dec-31-9999':
                    true_date = 'Date TBA'
                else:
                    true_date = true_begin
            # Deal with anime that is still ongoing
            elif true_end == 'Dec-31-9999':
                true_date = true_begin + " - ?"
            # Deal with anime that hasn't begun
            elif true_date == 'Dec-31-9999':
                true_date = "?"
            # Deal with anime that have both begin and end dates
            else:
                true_date = true_begin + " - " + true_end
        # The searchable title of the anime will be lowercase but presented anime title will be normal case
        lower_title = data[i]["Title"].lower()

        # Include stop words and make it lower case for searching.
        stopper = RegexTokenizer() | StopFilter()
        # List comprehension from whoosh documents
        search_description = [token.text for token in stopper(u"{}".format(data[i]["Description"].lower()))]
        # Put the words that were left after the stopper into the search description
        search_description = " ".join(search_description)

        # Write the newly formatted document in the index
        writer.add_document(Title=lower_title, True_title=data[i]["Title"], Rating=anime_rating, Link=data[i]["Link"],
                            Picture=data[i]["Picture"], EpisodeCount=episode_count, Begin_date=begin_date,
                            End_date=end_date, Genres=search_genres, True_description=data[i]["Description"],
                            Description=search_description, True_genres=anime_genres, True_date=true_date,
                            Producers=anime_producers, True_episode_count=true_episode_count, True_rating=true_rating)
    # Commit all the things we wrote using our for loop
    writer.commit()


if __name__ == "__main__":
    create_index()
