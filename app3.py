import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
from time import sleep
from selenium.webdriver.chrome.service import Service
import pandas as pd

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')  # Uncomment if you don't need a GUI

# Set up the Chrome WebDriver with the ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Initialize an empty list to store the data
collected_data = []

def scrape_page(driver):
    sleep(4)
    links = driver.find_elements(By.CLASS_NAME, 'complink')
    hrefs = list(set([link.get_attribute('href') for link in links]))

    for url in hrefs: 
        sleep(2)
        driver.get(url)
        try:
            # Using try-except to handle cases where the element might not be found
            director_name_element = driver.find_element(By.XPATH, '//*[@id="overview"]/div/p[6]')
            directors = director_name_element.text
            # Store the URL and Directors in a dictionary
            data_row = {'URL': url, 'Directors': directors}
            collected_data.append(data_row)
        except:
            print(f"Could not find the directors for URL: {url}")

def go_to_next_page(driver):
    # Try to find the 'Next' button; this selector might need adjustment
    next_buttons = driver.find_elements(By.XPATH, '/html/body/main/div/div/div/center/a[2]')
    if next_buttons:
        next_button = next_buttons[-1]  
        next_button.click()
        return True
    else:
        return False

base_url = 'https://www.tofler.in/companylist/maharashtra/manufacturing-motor-vehicles/pg-'
page_num = 2  
driver.get(f"{base_url}{page_num}")

while True:
    scrape_page(driver)
    # Check if 'Next' button exists and click it, or break if it doesn't
    if not go_to_next_page(driver):
        break
    sleep(2)  # Wait for the next page to load

# Close the browser
driver.quit()

# Convert the collected data into a pandas DataFrame
df = pd.DataFrame(collected_data)

# Now you have a DataFrame `df` with the data
# You can inspect it, manipulate it, or save it to a file
print(df.head())  # To print the first few rows of the DataFrame

# Optionally, save the DataFrame to a CSV file
df.to_excel('collected_data1.csv', index=False)
