import os
from sys import platform
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import timeit
import time

import config
import Diary

# Variables
NUM_ENTRIES_TO_SCRAPE = 100  # set to 0 for all entries

# Constants
SEC = 1
MIN = 60
ELEMENT_WAIT_TIME = 2*SEC
PAGE_WAIT_TIME = 30*SEC

cwd = os.getcwd()

if platform == "win32":
    driver = webdriver.Chrome(os.path.join(cwd, 'chromedriver-win-80'))
elif platform == "linux":
    driver = webdriver.Chrome(os.path.join(cwd, 'chromedriver-linux-80'))


def login_load():

    driver.get(config.LOGIN_URL)

    # # Doesn't work, can't send input to system pop-up box
    # time.sleep(2)
    # actions = ActionChains(driver)
    # login_string = config.USERNAME + Keys.TAB + config.PASSWORD + Keys.ENTER
    # actions.send_keys(login_string).perform()

    try:
        box_id = 'box'
        WebDriverWait(driver, PAGE_WAIT_TIME).until(EC.presence_of_element_located((By.ID, box_id)))
    except:
        print("Login failed? div 'box' not found")
        return False

    return True


def grab_diary_page(prev_text):

    try:
        div_box = WebDriverWait(driver, PAGE_WAIT_TIME)\
            .until(EC.presence_of_element_located((By.ID, 'box')))
    except TimeoutException:
        print("Page loading took too long")
        return False

    if prev_text == div_box.text:
        return False

    return div_box


def next_page():

    # Assume grab_diary_page() worked
    div_box = driver.find_element_by_id("box")
    divs_a = div_box.find_elements_by_css_selector('a')
    for div_a in divs_a:
        # If the content is 'stay', this is the correct 'a' div so check that URL
        if div_a.text == 'stay':
            href = div_a.get_attribute('href')
            driver.get(href)
            return True

    print("Failed to find 'stay' for next page")
    return False


def run_scraper(list_text, list_font):

    div = grab_diary_page("")
    text = div.text
    textHtml = div.get_attribute('innerHTML')

    count = 0
    initialText = text

    while True:
        count += 1

        # To cut program short
        if 0 < NUM_ENTRIES_TO_SCRAPE <= count:
            break

        diary_entry = Diary.add_to_diary(text)
        diary_entry_font = Diary.add_to_diary_font(textHtml)

        list_text.append(diary_entry)
        list_font.append(diary_entry_font)

        if config.add_to_file(config.files["logFile"], diary_entry, count) is False:
            return False

        if config.add_to_file(config.files["logFile_reverse"], diary_entry, count, reverse=True) is False:
            return False

        for i in range(3):
            if next_page() is False:
                break
            div = grab_diary_page(text)
            if div is not False:
                # we are at a new div with new text
                break
            else:
                continue
        else:
            print("Entry continually has same text as previous entry")
            print("Most recent entry:\n" + driver.current_url + "\n" + diary_entry.date)
            return False

        text = div.text
        textHtml = div.get_attribute('innerHTML')

        if div.text == initialText:
            break

    return True


def main():

    start = timeit.default_timer()

    diary_entries = []
    diary_entries_font = []

    if login_load() is True:

        config.clear_files()

        # Add to text file for human reading and storing
        if run_scraper(diary_entries, diary_entries_font) is False:
            return False

        # Add objects to file for pickler to write and read for new diary entries in new site

        config.add_to_file_pickle(config.files["logFile_pickle_text"], diary_entries)
        diary_entries.reverse()
        config.add_to_file_pickle(config.files["logFile_pickle_text_reverse"], diary_entries)

        config.add_to_file_pickle(config.files["logFile_pickle_font"], diary_entries_font)
        diary_entries_font.reverse()
        config.add_to_file_pickle(config.files["logFile_pickle_font_reverse"], diary_entries_font)

    # # Read from pickler files
    # config.read_from_file_pickle(config.files["logFile_pickle_text"])
    # config.read_from_file_pickle(config.files["logFile_pickle_font"])

    stop = timeit.default_timer()

    driver.close()

    print("Program run time: " + "{0:.1f}".format(stop - start) + "s")

    return True


if __name__ == '__main__': main()
