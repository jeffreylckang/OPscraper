############ Final oddsportal scraper

# ATP, baseball, basket, darts, eSports, football, nfl, nhl, rugby
''' Create 4 main functions : scrape_historical, scrape_specific_season, scrape current_season, scrape_next_games
NB : You need to be in the right repository to import functions...'''
import os

from functions import *

print('Data will be saved in the following directory:', os.getcwd())

#Data for training data for NFL
#scrape_oddsportal_historical(sport = 'american-football', country = 'usa', league = 'nfl', start_season = '2013-2014', nseasons = 1)
#scrape_oddsportal_historical(sport = 'american-football', country = 'usa', league = 'nfl', start_season = '2014-2015', nseasons = 3)
#scrape_oddsportal_historical(sport = 'american-football', country = 'usa', league = 'nfl', start_season = '2017-2018', nseasons = 2)
#scrape_oddsportal_historical(sport = 'american-football', country = 'usa', league = 'nfl', start_season = '2019-2020', nseasons = 3)
#scrape_oddsportal_historical(sport = 'american-football', country = 'usa', league = 'nfl', start_season = '2022-2023', nseasons = 2)

#rescraped for dates

#Data for training data for NBA
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2014-2015', nseasons = 1)
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2015-2016', nseasons = 1)
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2016-2017', nseasons = 1)
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2017-2018', nseasons = 1)
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2018-2019', nseasons = 1)
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2019-2020', nseasons = 1)
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2020-2021', nseasons = 1)
#scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2021-2022', nseasons = 1)
scrape_oddsportal_historical(sport = 'basketball', country = 'usa', league = 'nba', start_season = '2022-2023', nseasons = 1)

#Data for training data for MLB ?
#scrape_oddsportal_historical(sport = 'baseball', country = 'usa', league = 'mlb', start_season = '2014-2015', nseasons = 2)

#Data for training data for EPL
#scrape_oddsportal_historical(sport = 'football', country = 'england', league = 'premier-league', start_season = '2013-2014', nseasons = 1)
#scrape_oddsportal_historical(sport = 'football', country = 'england', league = 'premier-league', start_season = '2014-2015', nseasons = 3)
#scrape_oddsportal_historical(sport = 'football', country = 'england', league = 'premier-league', start_season = '2017-2018', nseasons = 1)
#scrape_oddsportal_historical(sport = 'football', country = 'england', league = 'premier-league', start_season = '2018-2019', nseasons = 1)
#scrape_oddsportal_historical(sport = 'football', country = 'england', league = 'premier-league', start_season = '2019-2020', nseasons = 3)
#scrape_oddsportal_historical(sport = 'football', country = 'england', league = 'premier-league', start_season = '2022-2023', nseasons = 2)






