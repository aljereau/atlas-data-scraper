import json
import os
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def check_funda_structure():
    """Check the current HTML structure of a Funda property page to improve selectors."""
    # Set up the browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Find the most recent JSON file to get a property URL
        json_files = glob.glob('data/raw/*.json')
        latest_file = max(json_files, key=os.path.getmtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get the first property URL
        if data and 'source_url' in data[0]:
            url = data[0]['source_url']
            print(f"Checking Funda page structure using URL: {url}")
            
            # Load the page
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Save the page source for inspection
            with open('funda_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            print("Saved page source to funda_page_source.html")
            
            # Identify key elements for scraping and their structure
            print("\nKey Elements Found:")
            
            # Check for page title
            try:
                title = driver.title
                print(f"Page Title: {title}")
            except:
                print("Could not find page title")
            
            # Check for property price
            try:
                price_element = driver.find_element("css selector", ".object-header__price")
                print(f"Price element found: {price_element.text}")
            except:
                print("Could not find price element using .object-header__price")
            
            # Check for address
            try:
                address_element = driver.find_element("css selector", ".object-header__title")
                print(f"Address element found: {address_element.text}")
            except:
                print("Could not find address element using .object-header__title")
            
            # Check for details table
            try:
                details = driver.find_elements("css selector", ".object-kenmerken-list")
                if details:
                    print(f"Found {len(details)} detail tables with class .object-kenmerken-list")
                    # Print the first few items in the first table
                    rows = details[0].find_elements("css selector", "dt, dd")
                    print("\nDetail items found:")
                    for i in range(0, min(20, len(rows)), 2):
                        if i+1 < len(rows):
                            label = rows[i].text
                            value = rows[i+1].text
                            print(f"  {label}: {value}")
            except Exception as e:
                print(f"Error checking details table: {str(e)}")
            
            print("\nSuggested update for the funda_selectors dictionary:")
            print("""
self.funda_selectors = {
    'Property Name': {
        'selector': '.object-header__title',
        'type': 'text'
    },
    'Address': {
        'selector': '.object-header__title, .object-header__subtitle',
        'type': 'text',
        'combine': True
    },
    'Price': {
        'selector': '.object-header__price',
        'type': 'text'
    },
    'Construction Year': {
        'selector': 'dt:contains("Bouwjaar")',
        'type': 'next_sibling',
        'tag': 'dd'
    },
    'Living Area': {
        'selector': 'dt:contains("Wonen")',
        'type': 'next_sibling',
        'tag': 'dd'
    },
    'Plot Size': {
        'selector': 'dt:contains("Perceel")',
        'type': 'next_sibling',
        'tag': 'dd'
    },
    'Number of Rooms': {
        'selector': 'dt:contains("Kamers")',
        'type': 'next_sibling',
        'tag': 'dd'
    },
    'Energy Label': {
        'selector': 'dt:contains("Energielabel")',
        'type': 'next_sibling',
        'tag': 'dd'
    }
}
""")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_funda_structure() 