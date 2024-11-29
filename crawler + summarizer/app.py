from flask import Flask, render_template, request
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from openai import OpenAI
from langchain_openai import ChatOpenAI
import pandas as pd 
aa
api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        if not search_query:
            return "Invalid input", 400
        
        urls = scrape_google(search_query)
        summaries = process_links(urls)
        return render_template('result.html', urls=urls, summaries=summaries)

    return render_template('index.html')

def scrape_google(search_query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    urls = set()
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(2)  
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        links = driver.find_elements(By.CSS_SELECTOR, "a")
        for link in links:
            href = link.get_attribute("href")
            if href and 'google' not in href and 'youtube' not in href:
                urls.add(href)
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
    finally:
        driver.quit()
    return list(urls)

def process_links(links):
    summaries = []
    print('LInk')
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106", openai_api_key=api_key)
    for link in links[:10]:
        try:
            loader = WebBaseLoader([link])
            docs = loader.load()
            chain = load_summarize_chain(llm, chain_type="map_reduce")
            summary = chain.run(docs)
            summaries.append({'Link': link, 'Summary': summary})
        except Exception as e:
            print(f"Error processing link {link}: {e}")
            summaries.append({'Link': link, 'Summary': f"Error generating summary: {e}"})
    return summaries

if __name__ == '__main__':
    app.run(debug=True, port=5014)
