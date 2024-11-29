from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from time import sleep 
import re

chrome_options = webdriver.ChromeOptions()
# Instantiate the WebDriver with ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
collected_data = []
sleep(2)

driver.get("https://www.tofler.in/login?redirecturl=/")
sleep(20)
# user_name= driver.find_element(By.XPATH,'//*[@id="email"]').send_keys("sarode.srv@gmail.com")
# sleep(1)
# password = driver.find_element(By.XPATH,'//*[@id="Password"]').send_keys("Sarode@44")
# sleep(1)
# a = driver.find_element(By.XPATH,'//*[@id="signinbutton"]').click()
# sleep(3)

try:
    for i in range(36, 72):  # This will iterate from page 1 to 72
        url = f"https://www.tofler.in/companylist/maharashtra/manufacturing-motor-vehicles/pg-{i}"
        driver.get(url)
        # sleep(10)
        # Wait for the links to be loaded on the page
        links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'complink')))
        hrefs = list(set([link.get_attribute('href') for link in links]))
        
        for href in hrefs:
            driver.get(href)
            
            try:
                # Wait for the paragraph inside 'overview' to be visible
                paragraph = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="overview"]/div'))
                )
                paragraph_text = paragraph.text

                data_row = {"Company Link": href, "Details": paragraph_text}
                collected_data.append(data_row)

            except Exception as e:
                print(f"Error fetching paragraph for {href}: {e}")

except Exception as e:
    print(f"Error during scraping: {e}")
finally:
    driver.quit() 

# Convert the collected data into a DataFrame
df1 = pd.DataFrame(collected_data)
print(df1)


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


df1['Company Name'] = df1['Details'].apply(Company_Name)
df1['Last Reported AGM Date'] = df1['Details'].apply(AGM_date)
df1['Directors'] = df1['Details'].apply(Directors)
df1['CIN Number'] = df1['Details'].apply(CIN)
df1['Address'] = df1['Details'].apply(Address)
df1['Incorporated Date'] = df1['Details'].apply(incorporated_date)
df1['Company Type'] = df1['Details'].apply(company_type)
df1['Authorized Share Capital'] = df1['Details'].apply(share_capital)
df1['Paid-up Capital'] = df1['Details'].apply(paid_up_capital)
df1['Current Status'] = df1['Details'].apply(current_status)

age_column_index = df1.columns.get_loc('Last Reported AGM Date') + 1
df1.insert(age_column_index, 'Age', df1.pop('Age')) 
df1.to_excel('Automobile1.xlsx', engine='openpyxl')

df1.to_excel('Auto2.xlsx', engine='openpyxl')