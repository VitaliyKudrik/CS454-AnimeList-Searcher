# CS454-AnimeList-Searcher
Final project for CS 454

Queries for dates = "year:month:date" - must be like this - "1999-04-09"
cannot have "2005-4-14" you need to have a zero if there is only 1 digit.

This command can sort by dates or other things, might be useful for the filtering after results.
sortedby

Edit distance is like this: "Gedsxs[tilde]2" using the ~ for editdistance and a number for how much of a distance.
"Gedsxs[tilde]2" would translate to "Geass" for "Code Geass"

When creating the index I created "True" copies of data that will be shown to the user so that I can keep more refined data for actual searching.
By this I mean that I used stop words for description, which means I needed to save one version of description with stopping and one without so that I can show users.

I also used True copies for rating and episode count and air date. This is because some ratings have 99999 values because they were unrated.
Similar reasons for air date and episode count, so I fixed those fillers with True data which is just text that says the proper data.