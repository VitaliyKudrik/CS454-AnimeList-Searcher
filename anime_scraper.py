from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from time import sleep
from random import randint

# Student: Vitaliy Kudrik
# CS 454 - Information Retrieval
# Final project - Web scraper for anime searcher
# Teacher - Ben McCamish


# Format = Day, Month, Year
def date_parser(date):
    # Check if there is only a year in the date, which happens for some specials/movies
    if len(date.split()) == 1:
        return date

    # months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7,
    #           "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    date_data = date.split()
    remove_comma = re.compile(r'[,]')

    # Check for movies that have a month, day and year
    if len(date.split()) == 3:
        # remove the comma using regex
        for thing in date_data:
            date_data[date_data.index(thing)] = remove_comma.sub("", thing)
        date_data[0], date_data[1] = date_data[1], date_data[0]
        return date_data[0] + "-" + date_data[1] + "-" + date_data[2][2:]

    if len(date.split()) == 5:
        # remove the comma using regex
        for thing in date_data:
            date_data[date_data.index(thing)] = remove_comma.sub("", thing)
        date_data[0], date_data[1] = date_data[1], date_data[0]
        return date_data[0] + "-" + date_data[1] + "-" + date_data[2][2:] + " to " + "?"

    # If the "to" is in the data then we have two dates.
    if "to" in date_data and len(date_data) == 7:
        date_data[0], date_data[1] = date_data[1], date_data[0]
        date_data[4], date_data[5] = date_data[5], date_data[4]

        for thing in date_data:
            # remove the comma using regex
            date_data[date_data.index(thing)] = remove_comma.sub("", thing)
            # Removed this because keeping the shortened month names seems better, but left it here in case
            # it even needs to be changed back to integer form.
            # ---- If thing is a month like "Feb", then we exchange it with the integer value for it
            # ---- if thing in months:
            #     ---- date_data[date_data.index(thing)] = str(months[thing])

    if len(date_data) == 7:
        first_date = date_data[0] + "-" + date_data[1] + "-" + date_data[2][2:]
        second_date = date_data[4] + "-" + date_data[5] + "-" + date_data[6][2:]
        return first_date + " to " + second_date

    # If all else fails just return the original date.
    return date


# Takes in an anime's link which will be received from the top anime page
def get_anime_info(anime, info_holder):
    # Access the webpage of the anime using a link
    response_ani = requests.get(anime)
    # Get the text of the webpage
    webpage_ani = response_ani.text
    # Parse the html using beautiful soup
    temp_soup = BeautifulSoup(webpage_ani, "html.parser")

    # Get the link of the anime's picture
    anime_img = temp_soup.find(name="img", itemprop="image")
    if anime_img is not None:
        info_holder.append(anime_img.get("data-src"))
    else:
        # If there is no img link then we just link an img that says there is no img
        info_holder.append("No_IMG_Found.png")

    # Get all the anime information which is typically contained in spaceit class.
    anime_info = temp_soup.find_all(name="div", class_="spaceit_pad")
    clean_black_slash = re.compile(r'[\n\r\t]')

    # The website changed some stuff around so now I have to do this to get the episodes and airdates
    episode_flag = False
    aired_flag = False
    for i in range(0, len(anime_info)):
        # stop looping if we already found the episode and air dates
        if episode_flag and aired_flag:
            break
        if "Aired" in anime_info[i].text[0:6]:
            # This is the air dates of the anime
            air_dates = anime_info[i].text[10::]
            air_dates = clean_black_slash.sub("", air_dates)
            air_dates = date_parser(air_dates)
            info_holder.append(air_dates)
            aired_flag = True
        if "Episodes" in anime_info[i].text[0:9]:
            # This is the amount of episodes the anime has. The cleaning is for the extra black text and new lines.
            episode_count = (anime_info[i].text[13::])
            episode_count = clean_black_slash.sub("", episode_count)
            info_holder.append(episode_count)
            episode_flag = True

    # This is a regex expression that removes all backslash characters from text.

    genre_list = []
    # Find all the anime_genres
    anime_genre = temp_soup.find_all(name="span", itemprop="genre")
    # Add them to a list so that we can use that list to create a simple genre string
    for thing in anime_genre:
        genre_list.append(thing.text)
    # Join the items in the list using commas to make a simple genre string
    genre_string = ", "
    genre_string = genre_string.join(genre_list)
    info_holder.append(genre_string)

    # This gets the description of the anime
    anime_description = temp_soup.find(name="p", itemprop="description").text
    anime_description = clean_black_slash.sub("", anime_description)
    if anime_description is not None:
        info_holder.append(anime_description)
    else:
        info_holder.append("Unknown description")

    # Hold a list of people who worked on the production of the anime. This includes Producers, Licensors and Studios.
    producer_list = []
    # This is where the producers are
    anime_info = temp_soup.find_all(name="a")
    for thing in anime_info:
        # They each have their own href which I use to find them
        href = thing.get('href')
        # Make sure the href exists
        if href is not None:
            # If the word producer is in the href
            # Checking for myanimlist.net is a check for when there are no producers in a certain category.
            if 'producer' in href and "myanimelist.net" not in href:
                # We break the link apart and only get the actual name of the producer
                href = href.split("/")
                # Sometimes producers and studios are the same, so we only need them once.
                if href[-1] not in producer_list:
                    producer_list.append(href[-1])

    producer_string = ", "
    producer_string = producer_string.join(producer_list)
    info_holder.append(producer_string)

    return info_holder


# Main function
def main():
    """
        I will be using myanimelist.net to get my data. Specifically the top anime list.
        This list has thousands of animes so I decided it would be the easiest place to collect data.
        also their robots.txt didn't have many restrictions at all, so I assumed scraping their data would be fine.
    """
    # Page counter is what I'll use to navigate the top anime list. They have a limit of showing 50 anime per page
    # So after I get all 50 anime's from the page, I will increment the counter by 50
    page_counter = 0
    # This try actually only catches if the website stops us from crawling due to limitations or bans
    # I had to include this, otherwise my data wouldn't be saved and I didn't want to risk that.

    df = None
    try:
        for i in range(0, 330):
            # Get the new page with 50 new animes
            response = requests.get("https://myanimelist.net/topanime.php?limit={}".format(page_counter))
            # Get the text of the webpage
            webpage = response.text
            # Parse the html using beautiful soup
            soup = BeautifulSoup(webpage, "html.parser")
            # Single out the top 50 anime that are presented on each page
            top_fifty = soup.find_all(name="tr", class_="ranking-list")

            # Go through all the anime in the list and get their information
            # Counter is used to create the DataFrame without issues, it also helps to see how fast the program worked
            counter = 0
            for anime in top_fifty:
                # This is what will be added into the pandas dataframe.
                # All the data we scrape is going to be put into here.
                anime_info_holder = list()

                # Get the title of the anime and append it to the holder
                anime_info_holder.append(anime.find(name='div', class_="di-ib clearfix").find('a').text)
                # Get the rating of the anime and append it to the holder
                anime_info_holder.append(anime.find(name='td', class_="score ac fs14").find('span').text)
                # Get the link of the anime and append it to the holder
                link = anime.find(name='div', class_="di-ib clearfix").find('a').get('href')
                if link is not None:
                    anime_info_holder.append(link)
                else:
                    anime_info_holder.append("Unknown link")
                # This will go to the anime's webpage and scrape more data, adding it to the holder
                anime_info_holder = get_anime_info(link, anime_info_holder)
                # We create the initial dataframe if page_counter and normal counter are both 0, thus at beginning
                if counter == 0 and page_counter == 0:
                    df = pd.DataFrame([anime_info_holder], columns=['Title', 'Rating', 'Link', 'Picture',
                                                                    'Episode Count', 'Airing Dates', 'Genres',
                                                                    'Description', 'Producers'])
                    df.index = df.index + 1
                else:
                    # This is a dataframe which we will append to the already existing dataframe
                    append_df = pd.DataFrame([anime_info_holder],
                                             columns=['Title', 'Rating', 'Link', 'Picture', 'Episode Count',
                                                      'Airing Dates', 'Genres', 'Description', 'Producers'])
                    # Once all of it will be appended then we write to CSV.
                    df = df.append(append_df, ignore_index=True)
                counter += 1
                # Sleep a little so that we don't overload the website. Feel free to change this to what you want Ben.
                sleep(randint(2, 4))
                # Clean feedback to what's happening. I enjoyed watching this as my data populated.
                print(anime_info_holder[0], " ", counter, page_counter)
            if i % 30 == 0:
                df.to_csv("top_19500_anime_4_{}.csv".format(i))
            page_counter += 50
        # Finally send all the data to a csv file name top_2600_anime.
        df.to_csv("top_19500_anime_4_final_data.csv")
    # If any exceptions happen, then we make sure to write the file then the program can close.
    except Exception as e:
        print(e)

        df.to_csv("top_19500_anime_4_final_data.csv")
        # Stop the program and return
        return


if __name__ == "__main__":
    main()
