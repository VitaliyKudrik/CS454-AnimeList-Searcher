"""
This is just a simple helper file to keep my code cleaner.
Modifying the dates was kind of a messy process because some of the scraped data
wasn't very clean for some reason. Possibly due to inconsistency on their record keeping and my scraping.
"""

import re

months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7,
          "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


# This is a helper function for the date_parser
def modify_date(date_data):
    # Base case for only a year in the date_data
    if len(date_data.strip()) == 4:
        return [int(date_data), 1, 1]

    # Split the date in 3 separate numbers
    if "-" in date_data:
        date_data = date_data.split("-")
    # This deals with a very select few documents that are formatted strangely using spaces instead of "-"s
    elif " " in date_data:
        # This is a regex expression that removes all space characters from text.
        clean_spaces = re.compile(r'[" ]')
        date_data = clean_spaces.sub("", date_data)
        date_data = date_data[0:3] + "-" + date_data[3::]
        date_data = date_data.split("-")
        date_data.insert(0, "1")
        date_data[2] = date_data[2][2::].strip()

    # Some anime only have a month and year for release date, so by default we will just set the day to 1
    if len(date_data) == 2:
        date_data.insert(0, "1")

    # Deal with the day
    date_data[0] = int(date_data[0])
    # Deal with the month
    date_data[1] = months[date_data[1]]

    # Deal with small issue in a few pieces of data | changes a 4 number year into last 2 digits
    if date_data[2] and len(date_data[2].strip()) > 2:
        # Remove trailing whitespace and take the last two digits of the number in string form
        date_data[2] = str(int(date_data[2][2::].strip()))

    # Deal with the year
    if int(date_data[2]) > 21:
        # Checks if the anime has a year after 21 which would imply it's from 1900's
        date_data[2] = "19" + date_data[2]
    else:
        # Otherwise we are from the 2000's
        date_data[2] = "20" + date_data[2]
    # Make the year into int
    date_data[2] = int(date_data[2].strip())
    # Switch the year and the day to fit the daytime format
    date_data[0], date_data[2] = date_data[2], date_data[0]
    # Return the new date formatted
    return date_data


# Format = Day, Month, Year
def date_parser(my_date):
    # Some air dates aren't available so we just give them a date that eventually we ignore when searching
    if my_date.strip() == "Not available":
        return [9999, 12, 31], [9999, 12, 31]
    date_data = my_date.strip()
    # Deal with a data issue where formatting was slightly weird.
    # Data starts with a "to" followed by a year.
    # This just returns that year with a default day and month of 1,1
    if my_date[0:2] == "to":
        my_date = my_date.split("-")
        # Deal with the year
        my_date[1] = "20" + my_date[1][2::]
        # If the year is "00" then we are in the year 2000
        if int(my_date[1]) == 0:
            my_date[1] = "2000"
        return [int(my_date[1]), 1, 1], [int(my_date[1]), 1, 1]

    # Deal with date formats like 11-Mar, Mar-11, 2-Mar, Mar-2
    if len(date_data) == 6 or len(date_data) == 5:
        date_data = date_data.split("-")
        # Switch the months around because there is sometimes 11-Mar and sometimes Mar-11
        if len(date_data[0]) == 3:
            date_data[0], date_data[1] = date_data[1], date_data[0]
        # If it's a single digit number then it's from the year 2000
        if len(date_data[0]) == 1:
            date_data[0] = "200" + date_data[0]
        # Not sure if this was necessary [probably not], keeping just in case. Doesn't hurt having it.
        if len(date_data[1]) == 1:
            date_data[1] = "200" + date_data[1]
        # If the year is "00" then we are in the year 2000
        if int(date_data[0]) == 0:
            date_data[0] = '2000'
        return [int(date_data[0]), months[date_data[1]], 1], [int(date_data[0]), months[date_data[1]], 1]

    # We only have a year in the date
    if len(date_data) == 4:
        return [int(date_data), 1, 1], [int(date_data), 1, 1]
    # This is a placeholder date if an anime is still ongoing and doesn't have an end date
    date_data_two = [9999, 12, 31]

    # Our dates typically come in at day, month, year
    # ex = 14-Apr-04

    # Check for occasional data that has comma's
    comma_check = my_date.split(" ")
    # Just a checker to make sure that I actually found a comma
    found = False
    for x in range(len(comma_check)):
        # Found a comma
        if "," in comma_check[x]:
            # Remove comma
            comma_check[x] = comma_check[x].replace(",", "")
            # Set flag to true
            found = True
    # If we found a comma then we make sure to make our date back into a string
    if found:
        my_date = " ".join(comma_check)

    # Check if we have two dates
    if "to" in my_date:
        # If we do then we split it on the "to" and we will have two dates in our array
        dates = my_date.split("to")
    else:
        # Otherwise we just put 1 date into the array
        dates = [my_date]
    try:
        # Deal with the first date
        date_data = modify_date(dates[0])
    # This except clause is broad but it's that way because there are a few exceptions that occur
    # These cases are rare and only really happen in the later anime that are formatted strangely
    except:
        date_data = my_date.split("-")
        # Checks if the month is first then switches
        if len(date_data[0]) == 3:
            date_data[0], date_data[1] = date_data[1], date_data[0]
        # If the format is correct
        if len(date_data[0]) == 4 and len(date_data[1]) == 3:
            # Check if we have a question mark in the data
            if "?" in date_data[2]:
                # If we did then we return the normal date and an enormous date that will be ignored
                return [int(date_data[0]), months[date_data[1]], 1], [9999, 12, 31]
            # Otherwise the dates are the same and we return them
            return [int(date_data[0]), months[date_data[1]], 1], [int(date_data[0]), months[date_data[1]], 1]

    # Deal with second date
    if len(dates) == 2:
        # If anime is on going then we give it the date with the year 9999
        if dates[1].strip() == "?":
            return date_data, date_data_two
        # Otherwise we will also convert that date into datetime format
        date_data_two = modify_date(dates[1])
    else:
        # There is only 1 date and nothing else, likely a movie/ova/ona, so end and start date are the same
        date_data_two = date_data
    # Returns two dates in format: year, month, day
    return date_data, date_data_two