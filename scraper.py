"""
TITLE:
    Advanced Twitter Scraper

LAST MODIFIED:
    2024-12-20

AUTHOR:
    Abu Sayed
    devabusayed@example.com

DESCRIPTION:
    This script provides an enhanced web scraping tool for extracting tweets from Twitter based on search criteria.
    It leverages Selenium with improved error handling, dynamic waits, and the ability to save data incrementally,
    minimizing data loss during scraping. It's designed to be flexible and extensible for various use cases.

FEATURES:
    - Robust error handling to manage null fields gracefully.
    - Incremental saving of data to reduce potential data loss.
    - Utilizes WebDriverWait for better dynamic content loading.
    - Configurable parameters for search, page scrolling, and data storage.

NOTES:
    - Be cautious of Twitter's scraping policies and potential IP bans for excessive activity.
    - Consider replacing CSV saving with a database integration for larger-scale use cases.

"""

import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions

def create_webdriver_instance():
    """Initialize the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")  # Remove this for debugging
    driver = webdriver.Chrome(options=options)
    return driver

def login_to_twitter(username, password, driver):
    """Log in to Twitter using provided credentials."""
    url = 'https://twitter.com/login'
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "session[username_or_email]"))
        )
        driver.find_element(By.NAME, "session[username_or_email]").send_keys(username)
        driver.find_element(By.NAME, "session[password]").send_keys(password)
        driver.find_element(By.NAME, "session[password]").send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.url_contains("/home"))
        print("Login successful.")
    except exceptions.TimeoutException:
        print("Login failed. Please check your credentials or internet connection.")
        driver.quit()
        return False
    return True

def perform_search(search_term, driver):
    """Search for the given term on Twitter."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search query"]'))
        )
        search_input = driver.find_element(By.XPATH, '//input[@aria-label="Search query"]')
        search_input.send_keys(search_term)
        search_input.send_keys(Keys.RETURN)
        print(f"Search initiated for: {search_term}")
    except exceptions.TimeoutException:
        print("Search input not found. Exiting...")
        driver.quit()
        return False
    return True

def save_to_csv(data, filepath):
    """Save tweet data to a CSV file."""
    header = ['User', 'Handle', 'PostDate', 'TweetText', 'ReplyCount', 'RetweetCount', 'LikeCount']
    with open(filepath, mode='a+', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)  # Write header if file is empty
        if data:
            writer.writerow(data)


def scrape_tweets(driver, filepath, scroll_limit=5):
    """Scrape tweets based on the current view."""
    last_position = None
    scroll_attempts = 0

    while scroll_attempts < scroll_limit:
        cards = driver.find_elements(By.XPATH, '//div[@data-testid="tweet"]')
        for card in cards:
            try:
                tweet = extract_tweet_data(card)
                if tweet:
                    save_to_csv(tweet, filepath)
            except exceptions.StaleElementReferenceException:
                continue

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        curr_position = driver.execute_script("return window.pageYOffset;")

        if curr_position == last_position:
            scroll_attempts += 1
        else:
            scroll_attempts = 0

        last_position = curr_position

    print(f"Scraping complete. Data saved to {filepath}")

def extract_tweet_data(card):
    """Extract relevant data from a tweet card."""
    try:
        user = card.find_element(By.XPATH, './/span').text
        handle = card.find_element(By.XPATH, './/span[contains(text(), "@")]').text
        post_date = card.find_element(By.XPATH, './/time').get_attribute('datetime')
        content = card.find_element(By.XPATH, './/div[2]/div[2]').text
        reply_count = card.find_element(By.XPATH, './/div[@data-testid="reply"]').text
        retweet_count = card.find_element(By.XPATH, './/div[@data-testid="retweet"]').text
        like_count = card.find_element(By.XPATH, './/div[@data-testid="like"]').text
        return [user, handle, post_date, content, reply_count, retweet_count, like_count]
    except exceptions.NoSuchElementException:
        return None

def main():
    """Main function to orchestrate the scraper."""
    username = "your_email@example.com"
    password = "your_password"
    search_term = "Python"
    filepath = "tweets.csv"

    driver = create_webdriver_instance()

    if not login_to_twitter(username, password, driver):
        return

    if not perform_search(search_term, driver):
        return

    scrape_tweets(driver, filepath)
    driver.quit()

if __name__ == "__main__":
    main()
