import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
from time import sleep
from selenium.webdriver.chrome.service import Service

# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
# Instantiate the WebDriver with ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

collected_data=[]
try:
    i = 1
    while True:
        url = f"https://www.tofler.in/companylist/maharashtra/manufacturing-motor-vehicles/pg-{i}"
        driver.get(url)
        sleep(2)  # Wait for page to load. Consider WebDriverWait for better efficiency

        # Check if the "No Data Found" message is present 
        if not driver.find_elements(By.CLASS_NAME, 'no-data-found-selector'):  # Update this selector as needed
            links = driver.find_elements(By.CLASS_NAME, 'complink')
            hrefs = list(set([link.get_attribute('href') for link in links]))
            
            for href in hrefs:
                driver.get(href)
                sleep(2)  # Consider WebDriverWait here as well

                try:
                    # Assuming 'overview' is a common class for all company pages
                    paragraph = driver.find_element(By.XPATH, '//*[@id="overview"]/div')
                    paragraph_text = paragraph.text
                    # print("Company URL:", href)
                    # print("Paragraph Text:", paragraph_text)
                    # print("-------")

                    data_row={"Comapny Link":href , "Details":paragraph_text}
                    collected_data.append(data_row)

                except Exception as e:
                    print(f"Error fetching paragraph for {href}: {e}")
        else:
            print("Reached the last page or no data found.")
            break
        i += 1
except Exception as e:
    print(f"Error during scraping: {e}")
finally:
    driver.quit()


import pandas as pd 
import re

def Company_Name(paragraph_text):
    match = re.search(r"OVERVIEW - (.+?)\n",paragraph_text)
    return match.group(1) if match else None 

def AGM_date(paragraph_text):
    match = re.search(r"was held on ([\d\w\s,]+)\.", paragraph_text)
    return match.group(1) if match else None

def Directors(paragraph_text):
    match = re.search(r"has [^\-]+? directors - ([\w\s,.-]+)\.", paragraph_text)
    return match.group(1) if match else None

def CIN(paragraph_text):
    match = re.search(r"The Corporate Identification Number \(CIN\) of [^\-]+? is ([\w\d]+)\.", paragraph_text)
    return match.group(1) if match else None

def Address(paragraph_text):
    match = re.search(r"The registered office of [^\-]+? is at (.+)$", paragraph_text, re.MULTILINE)
    return match.group(1) if match else None

def incorporated_date(paragraph_text):
    match = re.search(r"incorporated on ([\d\w\s,]+)\.", paragraph_text)
    return match.group(1) if match else None

def company_type(paragraph_text):
    match = re.search(r"is an (\w+ private company)", paragraph_text)
    return match.group(1) if match else "N/A"

def share_capital(paragraph_text):
    match = re.search(r"authorized share capital is (INR [\d\.]+ [cr|lac]+)", paragraph_text)
    return match.group(1) if match else None

def paid_up_capital(paragraph_text):
    match = re.search(r"the total paid-up capital is (INR [\d\.]+ [cr|lac]+)", paragraph_text)
    return match.group(1) if match else None

def current_status(paragraph_text):
    match = re.search(r"The current status of [\w\s]+ is - ([\w\s]+)\.", paragraph_text)
    return match.group(1) if match else None


df = pd.DataFrame(collected_data)


df['Company Name'] = df['Details'].apply(Company_Name)
df['Last Reported AGM Date'] = df['Details'].apply(AGM_date)
df['Directors'] = df['Details'].apply(Directors)
df['CIN Number'] = df['Details'].apply(CIN)
df['Address'] = df['Details'].apply(Address)
df['Incorporated Date'] = df['Details'].apply(incorporated_date)
df['Company Type'] = df['Details'].apply(company_type)
df['Authorized Share Capital'] = df['Details'].apply(share_capital)
df['Paid-up Capital'] = df['Details'].apply(paid_up_capital)
df['Current Status'] = df['Details'].apply(current_status)


df.to_csv("Automobile Comapny Data")