# This not the most updated version, It's just a trial method 

from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from time import sleep

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')  # Uncomment if you don't need a GUI

# Set up the Chrome WebDriver with the ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def check_next_page_exists(driver):
    try:
        driver.find_element(By.XPATH, '/html/body/main/div/div/div/center/a[contains(@rel, "next")]')
        return True
    except NoSuchElementException:
        return False

def get_directors_and_move_next(driver):
    while True:
        sleep(4)  # Wait for the page to load
        links = driver.find_elements(By.CLASS_NAME, 'complink')
        hrefs = list(set([link.get_attribute('href') for link in links]))
 
        for url in hrefs: 
            driver.get(url)
            sleep(2)
            try:
                Director_Name = driver.find_element(By.XPATH, '//*[@id="overview"]/div/p[6]')
                Directors = Director_Name.text
                print("Directors: ", Directors)
            except NoSuchElementException:
                print("Director information not found for URL:", url)
            sleep(2)
            driver.back()  # Go back to the listing page
            
        if check_next_page_exists(driver):
            next_page = driver.find_element(By.XPATH, '/html/body/main/div/div/div/center/a[contains(@rel, "next")]')
            next_page.click()
        else:
            break  # No more pages to navigate

# Start scraping from the initial page
initial_page = 'https://www.tofler.in/companylist/maharashtra/manufacturing-motor-vehicles/pg-5'
driver.get(initial_page)
get_directors_and_move_next(driver)

# Close the browser once done
driver.quit()
