import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import getpass
import xlrd
from datetime import datetime
import time

# Modules
import files_handling

# Current working directory
cwd = os.getcwd()

# Global vars
LOGIN_URL = 'https://login.xero.com/'
DASHBOARD_URL = 'https://go.xero.com/Dashboard/'
LOGIN_DETAILS = cwd + r'\data\user_pass.xlsx'
URL_LIST = cwd + r'\data\url_company.xlsx'

# Create new folder for reports
files_handling.folder_create()

# Firefox driver + options
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference("browser.download.folderList", 2)
firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
firefox_profile.set_preference("browser.download.dir", files_handling.THIS_REPORTS_DIR)
firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
driver = webdriver.Firefox(executable_path=cwd+r'\drivers\geckodriver.exe', firefox_profile=firefox_profile, service_log_path=r'.\drivers\geckodriver.log')

# # Chrome driver + options
# chrome_options = ChromeOptions()
# chrome_options.add_argument("user-data-dir=C:\\Users\\"+getpass.getuser()+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default")  # this is the directory for the cookies
# driver = webdriver.Chrome(executable_path=cwd+r'\drivers\chromedriver.exe', options=chrome_options)

second = 1
minute = 60
page_wait_time = 1*minute
element_wait_time = 5*second
download_file_wait_time = 5*second
refresh_page_wait_time = 15*second
end_program_wait_time = 30*second

max_tries = 3


def check_toast_error_exists(css):
    try:
        driver.find_element(By.CSS_SELECTOR, css)
    except NoSuchElementException:
        return False
    return True


def download_report():

    try:
        xpath_export = '//button[@data-automationid="report-toolbar-export-button"]'
        export_button = WebDriverWait(driver, page_wait_time)\
            .until(EC.presence_of_element_located((By.XPATH, xpath_export)))
        export_button.click()

        xpath_export_as_excel = "//*[@id='report-toolbar-export-excel-menuitem']"
        export_as_excel_button = WebDriverWait(driver, element_wait_time)\
            .until(EC.presence_of_element_located((By.XPATH, xpath_export_as_excel)))
        export_as_excel_button.click()

    except TimeoutException:
        print("Page loading took too long")
        return False

    # Downlaoded - wait to allow download to commence
    time.sleep(download_file_wait_time)

    return True


def load_report_url(url):
    driver.get(url)

    try:
        xpath_export = '//button[@data-automationid="report-toolbar-export-button"]'
        css_toast = 'div[data-automationid="toast"]'

        WebDriverWait(driver, page_wait_time).until(
            lambda d:
            d.find_element(By.XPATH, xpath_export)
            or d.find_element(By.CSS_SELECTOR, css_toast)
        )
    except TimeoutException:
        print("Report URL took too long to load... Aborting")
        return False

    if check_toast_error_exists(css_toast):
        print("Page loaded with error... Refreshing")
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'r')
        time.sleep(refresh_page_wait_time)
        return False

    return True


def login_event(username, password):

    try:
        driver.get(LOGIN_URL)
    except:
        print("Webpage load failed")
        return False

    try:
        driver.find_element_by_id("email").send_keys(username)
        driver.find_element_by_id("password").send_keys(password)
        driver.find_element_by_id("submitButton").click()
    except:
        print("Failed to submit login details")
        return False

    try:
        # # Search for Dashboard header
        # xpath = '//*[@id="header"]/header/div/ol[1]'
        # WebDriverWait(driver, page_wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))

        # Search for Edit dashboard in footer
        css = 'a[data-automationid = "editDashboard-edit"]'
        WebDriverWait(driver, page_wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    except:
        print("Failed to log in within", page_wait_time, "seconds")
        return False

    return True


def basic_checks():

    flag = True

    # Try open user_pass file
    try:
        wb = xlrd.open_workbook(LOGIN_DETAILS)
        sheet = wb.sheet_by_index(0)
        # Check headers
        if sheet.cell_value(0, 0) != 'Username' or sheet.cell_value(0, 1) != 'Password':
            print(LOGIN_DETAILS, " ... login details headers invalid")
            flag = False
    except:
        print(LOGIN_DETAILS, " ... login details file doesn't exist or needs to be closed")
        flag = False

    # Try open url_company file
    try:
        wb = xlrd.open_workbook(URL_LIST)
        sheet = wb.sheet_by_index(0)
        # Check headers
        if sheet.cell_value(0, 0) != 'Include (Y/N)' or sheet.cell_value(0, 1) != 'Company' or sheet.cell_value(0, 2) != 'URL':
            print(LOGIN_DETAILS, " ... URL list headers invalid")
            flag = False
    except:
        print(URL_LIST, " ... URL list file doesn't exist or needs to be closed")
        flag = False

    return flag


def main():

    print("START - XERO_DOWNLOAD")

    if not basic_checks():
        print("Resolve initial errors first... aborting")
        return False

    login_sheet = xlrd.open_workbook(LOGIN_DETAILS).sheet_by_index(0)
    username = login_sheet.cell_value(1, 0)
    password = login_sheet.cell_value(1, 1)

    url_sheet = xlrd.open_workbook(URL_LIST).sheet_by_index(0)

    login_success = login_event(username, password)
    if not login_success:
        return False

    for i in range(1, url_sheet.nrows):
        include = str(url_sheet.cell_value(i, 0))
        company = str(url_sheet.cell_value(i, 1))
        url = str(url_sheet.cell_value(i, 2))
        # Check row input
        print(f'{i:02} - ', end='')
        print(company)

        if include.lower() == 'n':
            print("...SKIP...")
            continue

        for j in range(max_tries):
            loaded = load_report_url(url)
            if loaded is True:
                break
            if j == max_tries - 1:
                print("Error on page too many times... aborting")
                return False

        downloaded_report = download_report()
        print("Download report for company: " + company)
        if downloaded_report:
            print("SUCCESS")
        else:
            print("FAILURE")

    print("\nClosing window in", end_program_wait_time, "seconds...")
    time.sleep(end_program_wait_time)

    driver.close()

    print("END - XERO_DOWNLOAD")

    return True

if __name__ == '__main__': main()


