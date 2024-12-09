### functions 
# OddsPortal scraper functions 
import os
import urllib
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import sys
import random
import signal
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from create_clean_table import *

global DRIVER_LOCATION
DRIVER_LOCATION = '/Users/jeffreykang/chromedriver-mac-arm64/chromedriver'
global service
service = Service(executable_path=DRIVER_LOCATION)
driver = None

def initialize_driver():
    global driver
    if driver is not None:
        driver.quit()
    try:
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        driver = None

def random_pause(min_seconds=2, max_seconds=6):
    """Pause for a random amount of time between min_seconds and max_seconds."""
    pause_duration = random.uniform(min_seconds, max_seconds)
    print(f"Pausing for {pause_duration:.2f} seconds...")
    time.sleep(pause_duration)

def scroll_to_bottom():
    """Scroll to the bottom of the page to ensure all elements are loaded."""
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Adjust this sleep time if needed for content to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # No more content to load
            last_height = new_height
    except Exception as e:
        print(f"Error during scrolling: {e}")

def wait_for_dom_complete(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete")

def get_data_typeA(game_id, game_link):
    try:
        print(f"Navigating to the game link: {game_link}")
        # Open the game's specific page
        driver.get(game_link) 
        print(f"Processing game {game_id}")
        random_pause(1,4)
        
        # Extracting average and highest odds
        try:
            # Locate the main container where the odds are located
            odds_container_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[2]/div/div/div[2]'
            odds_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, odds_container_xpath))
            )
        
            # Define the XPaths for the four odds we need to extract
            odds_xpaths = [
                './div[1]/div[2]/div/p',  # Average Home Odds
                './div[1]/div[3]/div/p',  # Average Away Odds
                './div[2]/div[2]/div/p',  # Highest Home Odds
                './div[2]/div[3]/div/p'   # Highest Away Odds
            ]
        
            # Extract odds data
            extracted_odds = []
            for xpath in odds_xpaths:
                try:
                    # Locate the <p> element and extract its text content
                    p_tag = odds_container.find_element(By.XPATH, xpath)
                    odd_value = p_tag.text
                    extracted_odds.append(odd_value)
                except Exception as e:
                    print(f"Error extracting odds for XPath {xpath}: {e}")
                    extracted_odds.append(None)  # Append None if extraction fails
        
        except Exception as e:
            print(f"Error finding the odds container: {e}")

        # Extracting team names
        home_team_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[1]/div[1]/div/div[1]/span'
        away_team_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[1]/span'
        home_team = driver.find_element(By.XPATH, home_team_xpath).text
        away_team = driver.find_element(By.XPATH, away_team_xpath).text
    
        # Extracting score
        score_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[2]/div[3]/div[2]/strong'
        score_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, score_xpath))
        )
        score_text = score_element.text.strip()
        parts = score_text.split(':')
        home_score = parts[0].strip()
        away_score = parts[1].split()[0].strip() if len(parts) > 1 else None
    
        # Extracting date/time
        date_time_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[2]/div[1]'
        date_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, date_time_xpath)))
        # Locate all <p> tags within the date container
        date_p_tags = date_container.find_elements(By.TAG_NAME, 'p')
        # Extract and join the text from each <p> tag
        date_time = " ".join([p.text for p in date_p_tags])
    
        # Game data
        game_data = {
            'Game ID': game_id,
            'Home Team': home_team,
            'Away Team': away_team,
            'Home Score': home_score,
            'Away Score': away_score,
            'Average Home Odds': extracted_odds[0],
            'Average Away Odds': extracted_odds[1], 
            'Highest Home Odds': extracted_odds[2],
            'Highest Away Odds': extracted_odds[3],
            'Date': date_time
        }
    
        # Extracting bookmakers' odds
        bookmaker_data = []

        try:
            # Locate the main container where the bookmakers' odds are listed
            bookmakers_section_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[2]/div/div/div[1]'
            bookmakers_container = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, bookmakers_section_xpath))
            )
        
            # Locate all the relevant <p> tags within the bookmakers container
            p_tags = bookmakers_container.find_elements(By.XPATH, './/p')
        
            # Skip the first 4 <p> tags (labels) by slicing the list
            p_tags = p_tags[4:]
        
            # Iterate over the remaining <p> tags in triplets: Name, Home Odds, Away Odds
            i = 0
            while i < len(p_tags):
                try:
                    bookmaker_name = p_tags[i].text.strip()
        
                    # Check if the bookmaker name indicates the end of the list
                    if "click to show" in bookmaker_name.lower():
                        break
        
                    # Ensure the next two <p> tags exist for Home and Away odds
                    if i + 2 < len(p_tags):
                        home_odd = p_tags[i + 1].text.strip()
                        away_odd = p_tags[i + 2].text.strip()
        
                        # Store the bookmaker's data in a dictionary
                        bookmaker_data.append({
                            'Game ID': game_id,
                            'Bookmaker Name': bookmaker_name,
                            'Home Odds': home_odd,
                            'Away Odds': away_odd
                        })
        
                    # Move to the next triplet
                    i += 3
        
                except Exception as e:
                    print(f"Error processing bookmaker at index {i}: {e}")
                    i += 1  # Move to the next element to avoid an infinite loop

        except Exception as e:
            print(f"Error finding the bookmakers container: {e}")
    
    except Exception as e:
        print(f"Error processing game {game_id}: {e}")
        game_data, bookmaker_data = {}, []
    
    return {'game_data': game_data, 'bookmaker_data': bookmaker_data}

def get_data_typeB(game_id, game_link):
    try:
        print(f"Navigating to the game link: {game_link}")
        # Open the game's specific page
        driver.get(game_link) 
        print(f"Processing game {game_id}")
        random_pause(1,4)
        
        # Extracting average and highest odds
        try:
            # Locate the main container where the odds are located
            odds_container_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[2]/div/div/div[2]'
            odds_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, odds_container_xpath))
            )
        
            # Define the XPaths for the four odds we need to extract
            odds_xpaths = [
                './div[1]/div[2]/div/p',  # Average Home Odds
                './div[1]/div[3]/div/p', # Average Draw Odds
                './div[1]/div[4]/div/p',  # Average Away Odds
                './div[2]/div[2]/div/p',  # Highest Home Odds
                './div[2]/div[3]/div/p', # Highest Draw Odds
                './div[2]/div[4]/div/p'   # Highest Away Odds
            ]
        
            # Extract odds data
            extracted_odds = []
            for xpath in odds_xpaths:
                try:
                    # Locate the <p> element and extract its text content
                    p_tag = odds_container.find_element(By.XPATH, xpath)
                    odd_value = p_tag.text
                    extracted_odds.append(odd_value)
                except Exception as e:
                    print(f"Error extracting odds for XPath {xpath}: {e}")
                    extracted_odds.append(None)  # Append None if extraction fails
        
        except Exception as e:
            print(f"Error finding the odds container: {e}")

        # Extracting team names
        home_team_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[1]/div[1]/div/div[1]/span'
        away_team_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[1]/div[3]/div[1]/span'
        home_team = driver.find_element(By.XPATH, home_team_xpath).text
        away_team = driver.find_element(By.XPATH, away_team_xpath).text
    
        # Extracting score
        score_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[2]/div[3]/div[2]/strong'
        score_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, score_xpath))
        )
        score_text = score_element.text.strip()
        parts = score_text.split(':')
        home_score = parts[0].strip()
        away_score = parts[1].split()[0].strip() if len(parts) > 1 else None
    
        # Extracting date/time
        date_time_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[1]/div[2]/div[1]'
        date_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, date_time_xpath)))
        # Locate all <p> tags within the date container
        date_p_tags = date_container.find_elements(By.TAG_NAME, 'p')
        # Extract and join the text from each <p> tag
        date_time = " ".join([p.text for p in date_p_tags])
    
        # Game data
        game_data = {
            'Game ID': game_id,
            'Home Team': home_team,
            'Away Team': away_team,
            'Home Score': home_score,
            'Away Score': away_score,
            'Average Home Odds': extracted_odds[0],
            'Average Draw Odds': extracted_odds[1],
            'Average Away Odds': extracted_odds[2],
            'Highest Home Odds': extracted_odds[3],
            'Highest Draw Odds': extracted_odds[4],
            'Highest Away Odds': extracted_odds[5],
            'Date': date_time
        }
    
        # Extracting bookmakers' odds
        bookmaker_data = []

        try:
            # Locate the main container where the bookmakers' odds are listed
            bookmakers_section_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[2]/div[2]/div/div/div[1]'
            bookmakers_container = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, bookmakers_section_xpath))
            )
        
            # Locate all the relevant <p> tags within the bookmakers container
            p_tags = bookmakers_container.find_elements(By.XPATH, './/p')
        
            # Skip the first 5 <p> tags (labels) by slicing the list
            p_tags = p_tags[5:]
        
            # Iterate over the remaining <p> tags in triplets: Name, Home Odds, Draw Odds, Away Odds
            i = 0
            while i < len(p_tags):
                try:
                    bookmaker_name = p_tags[i].text.strip()
        
                    # Check if the bookmaker name indicates the end of the list
                    if "click to show" in bookmaker_name.lower():
                        break
        
                    # Ensure the next three <p> tags exist for Home, Draw, and Away odds
                    if i + 3 < len(p_tags):
                        home_odd = p_tags[i + 1].text.strip()
                        draw_odd = p_tags[i + 2].text.strip()
                        away_odd = p_tags[i + 3].text.strip()
        
                        # Store the bookmaker's data in a dictionary
                        bookmaker_data.append({
                            'Game ID': game_id,
                            'Bookmaker Name': bookmaker_name,
                            'Home Odds': home_odd,
                            'Draw Odds': draw_odd,
                            'Away Odds': away_odd
                        })
        
                    # Move to the next quaduple
                    i += 4
        
                except Exception as e:
                    print(f"Error processing bookmaker at index {i}: {e}")
                    i += 1  # Move to the next element to avoid an infinite loop

        except Exception as e:
            print(f"Error finding the bookmakers container: {e}")
    
    except Exception as e:
        print(f"Error processing game {game_id}: {e}")
        game_data, bookmaker_data = {}, []
    
    return {'game_data': game_data, 'bookmaker_data': bookmaker_data}


def scrape_page_typeA(page, sport, country, league, season, processed_game_ids):
    base_link = f'https://www.oddsportal.com/{sport}/{country}/{league}-{season}/results/'
    if page == 1:
        page_url = base_link
        print(f"Starting on page {page}: {page_url}")
    elif page > 1:
        page_url = f'{base_link}#/page/{page}/'
        print(f"Navigated to page {page}: {page_url}")
    
    # Define the XPath directly as a string here
    # data-v-09299aa8 - oddsportal changed the div name 
    game_divs_xpath = '//div[contains(@class, "eventRow") and @data-v-b3200024 and @set and @id]'
    #game_divs_xpath = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[4]/div[1]/div[1]'

    # Initialize these strings to contain a list of game data
    game_level_data = []
    bookmaker_level_data = []
    max_retries = 5

    # Safely iterate over the game divs with re-initialization on each iteration
    i = 0
    while True:
        try:
            # Reload the page and scroll to the bottom to load all elements
            driver.get(page_url)
            random_pause(2,5)
            scroll_to_bottom()
            wait_for_dom_complete(driver)

            retries = 0
            while retries < max_retries:
                game_divs = driver.find_elements(By.XPATH, game_divs_xpath)
                if game_divs and len(game_divs) != 5:
                    print(f"Found {len(game_divs)} game divs.")
                    break
                else:
                    print(f"Found {len(game_divs)} game divs, which may be incorrect, retrying... (Attempt {retries + 1})")
                    retries += 1
                    driver.get(page_url)
                    random_pause(2, 5)
                    scroll_to_bottom()
                    wait_for_dom_complete(driver)
            
            game_ids = [div.get_attribute('id') for div in game_divs]

            # Get the current game div
            game_div = game_divs[i]
            game_id = game_div.get_attribute('id')
            print(f'game_id for {i + 1}: {game_id}')

            if len(game_id) == 8:
                # Locate the nested 'group flex' div and extract the <a> tag
                group_flex_div = game_div.find_element(By.XPATH, './/div[@class="group flex"]')
                game_link_element = group_flex_div.find_element(By.TAG_NAME, 'a')
                game_link = game_link_element.get_attribute('href')
                # Visit the game's link
                driver.get(game_link)
                random_pause(2,4)

                # Call get_data_typeA or B to collect data depending on league because of draw
                if league == 'premier-league':
                    data = get_data_typeB(game_id, game_link)
                else:
                    data = get_data_typeA(game_id, game_link)

                # Append collected data
                if data['game_data']:
                    game_level_data.append(data['game_data'])
                if data['bookmaker_data']:
                    bookmaker_level_data.extend(data['bookmaker_data'])

                print(f"Data from game {i + 1} collected")
                # Add the game ID to the set of processed IDs
                processed_game_ids.add(game_id)

            # Increment the offset to process the next game
            i += 1

            # If we've processed all available games, break the loop
            if i >= len(game_divs):
                print(f"No more game divs available at index {i}.")
                break

        except NoSuchElementException:
            print(f"Error processing game {i + 1}, skipping.")
            continue

        except StaleElementReferenceException as e:
            print(f"Stale element reference at index {i}: {e}")

    print("Completed data collection for the page.")
    return {'game_level_data': game_level_data, 'bookmaker_level_data': bookmaker_level_data}

# To be used in scrape_league_typeA
def navigate_to_season(driver, base_link, season_year):
    driver.get(base_link)
    time.sleep(2)  # Ensure the page loads completely
    season_links = driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[3]/div/div[2]//a')
    for link in season_links:
        if season_year in link.text:
            link.click()
            print(f"Navigated to season {season_year}")
            return

# To be used in scrape_league_typeA
def determine_max_pages(driver):
    attempts = 0
    max_attempts=3
    while attempts < max_attempts:
        try:
            pagination_links = driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[4]/div[1]/div[3]/div//a')
            # Max pages is determined by the number that appears before 'Next' on the HTML page which is second from the last
            max_pages = int(pagination_links[-2].text)
            return max_pages
            
        except Exception as e:
            attempts += 1
            print(f"Attempt {attempts} failed with error: {e}")
            if attempts < max_attempts:
                print("Retrying to determine max pages...")
                random_pause(2, 5)  # Pause for a random time between 2 and 5 seconds before retrying
            else:
                print("Pagination parsing failed after multiple attempts, defaulting to 1")
                return 1

def scrape_league_typeA(season, sport, country, league):
    base_link = f'https://www.oddsportal.com/{sport}/{country}/{league}-{season}/results/'

    game_level_all_data = []
    bookmaker_level_all_data = []

    navigate_to_season(driver, base_link, season)
    actual_max_pages = int(determine_max_pages(driver))
    print(f'{actual_max_pages} pages to scrape')
    # Initialize a set to track processed game IDs
    processed_game_ids = set()
    for page in range(1, actual_max_pages + 1):
        data = scrape_page_typeA(page, sport, country, league, season, processed_game_ids)
        game_level_all_data.extend(data['game_level_data'])
        bookmaker_level_all_data.extend(data['bookmaker_level_data'])
        print(f'Data entered, going to next page')
        
    print(f'Finished scraping season {season}')

    return {'game_level_data': game_level_all_data, 'bookmaker_level_data': bookmaker_level_all_data}


def scrape_oddsportal_historical(sport, country, league, start_season, nseasons):
    global driver
    initialize_driver()
    if driver is None:
        print("Driver not initialized. Exiting function.")
        return
    
    start_year = int(start_season.split('-')[0])
    game_level_all_data = []
    bookmaker_level_all_data = []

    for i in range(nseasons):
        season = f'{start_year+i}-{start_year+i+1}'
        print(f'Starting to scrape season {season}')
        data = scrape_league_typeA(season, sport, country, league)
        game_level_all_data.extend(data['game_level_data'])
        bookmaker_level_all_data.extend(data['bookmaker_level_data'])

    driver.quit()

    game_df = pd.DataFrame(game_level_all_data)
    bookmaker_df = pd.DataFrame(bookmaker_level_all_data)
    if not os.path.exists(f'./{sport}/{league}'):
        os.makedirs(f'./{sport}/{league}')
    game_csv_path = f'./{sport}/{league}/Historical_{league}_{start_season}_games.csv'
    bookmaker_csv_path = f'./{sport}/{league}/Historical_{league}_{start_season}_bookmakers.csv'
    game_df.to_csv(game_csv_path, sep=';', encoding='utf-8', index=False)
    bookmaker_df.to_csv(bookmaker_csv_path, sep=';', encoding='utf-8', index=False)

    print(f'Game data saved to {game_csv_path}')
    print(f'Bookmaker data saved to {bookmaker_csv_path}')

    return {'game_data': game_df, 'bookmaker_data': bookmaker_df}

