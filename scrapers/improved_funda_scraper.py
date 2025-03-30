from typing import Dict, List, Any
import re
import time
import random
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base_scraper import BaseScraper
from utils.excel_config import ExcelConfigParser, DataPointConfig
from utils.request_utils import RequestThrottler, get_random_user_agent

class ImprovedFundaScraper(BaseScraper):
    def __init__(self, config_path: str = "config/websites.json", 
                 excel_path: str = "reference_data/Ai Modeling Data File.xlsm"):
        super().__init__(config_path)
        self.excel_config = ExcelConfigParser(excel_path)
        self.throttler = RequestThrottler(min_delay=5.0, max_delay=10.0)  # Increased delays
        self.max_retries = 3
        self.setup_driver()  # Initialize Selenium driver
        
    def setup_driver(self):
        """Setup Selenium WebDriver with enhanced anti-detection measures."""
        if not self.driver:
            chrome_options = Options()
            
            # More stealth options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-browser-side-navigation")
            chrome_options.add_argument("--disable-gpu")
            
            # Optional: Run in headless mode
            # chrome_options.add_argument("--headless")
            
            # Set a random user agent
            user_agent = get_random_user_agent()
            chrome_options.add_argument(f"user-agent={user_agent}")
            
            # Experimental options to better hide automation
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Set up the driver
            service = self._get_webdriver_service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set reasonable page load timeout
            self.driver.set_page_load_timeout(30)
            
            # Execute CDP commands to mask WebDriver
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            print(f"Browser initialized with user agent: {user_agent}")

    def scrape_properties(self) -> List[Dict[str, Any]]:
        """Scrape all properties from the provided Funda links."""
        property_data = []
        property_links = self.excel_config.get_property_links()
        funda_metrics = self.excel_config.get_funda_metrics()
        mock_metrics = self.excel_config.get_mock_metrics()

        total_properties = len(property_links)
        print(f"Starting to scrape {total_properties} properties from Funda...")

        for idx, link in enumerate(property_links):  # Process all properties
            try:
                print(f"Scraping property {idx+1}/{total_properties}: {link}")
                # Apply throttling before each request
                self.throttler.throttle()
                
                # Extract property data with retries
                property_info = self._scrape_with_retries(link, funda_metrics)
                
                # Add mock data 
                mock_data = self.generate_custom_mock_data(mock_metrics)
                property_info.update(mock_data)
                
                # Add the source link and timestamp
                property_info['source_url'] = link
                property_info['scrape_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
                
                property_data.append(property_info)
                print(f"Successfully scraped property {idx+1}/{total_properties}")
                
            except Exception as e:
                print(f"Error scraping property {link}: {str(e)}")
                # Add a longer delay after an error
                time.sleep(random.uniform(15, 30))

        return property_data
        
    def _scrape_with_retries(self, url: str, metrics: List[DataPointConfig]) -> Dict[str, Any]:
        """Scrape a property with multiple retries."""
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                # Load the URL with extra precautions
                self._load_url_safely(url)
                
                # Wait for critical elements to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".object-header__title, .object-kenmerken-list, .object-primary"))
                    )
                except TimeoutException:
                    # If we can't find key elements, the page might be a captcha or error page
                    print("Could not find key page elements, might be facing anti-scraping measures")
                    # Save screenshot for debugging
                    self._save_debug_screenshot()
                    
                    # Check for common anti-scraping patterns
                    if "Je bent bijna op de pagina die je zoekt" in self.driver.title:
                        print("Detected anti-scraping page, waiting and retrying...")
                        time.sleep(random.uniform(10, 15))
                        retry_count += 1
                        continue
                
                # Extract property data from the page
                property_info = self._extract_property_data(metrics)
                
                # If we got some data, return it
                if property_info and len(property_info) > 1:  # More than just property_id
                    return property_info
                
                # If we didn't get enough data, retry
                print(f"Didn't extract enough data, retrying ({retry_count+1}/{self.max_retries})")
                retry_count += 1
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                last_error = e
                print(f"Error during scraping attempt {retry_count+1}: {str(e)}")
                retry_count += 1
                time.sleep(random.uniform(5, 10))
        
        # If we've exhausted retries, return what we have or raise the last error
        if last_error:
            raise last_error
        return {'property_id': self._extract_property_id(url)}
    
    def _load_url_safely(self, url: str):
        """Load the URL with extra precautions to avoid detection."""
        # First clear cookies and cache
        self.driver.delete_all_cookies()
        
        # Load the URL
        self.driver.get(url)
        
        # Add some random wait time to simulate human behavior
        time.sleep(random.uniform(3, 6))
        
        # Scroll randomly to simulate human behavior
        self._scroll_randomly()
    
    def _scroll_randomly(self):
        """Perform random scrolling to simulate human behavior."""
        height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = random.randint(3, 8)
        
        for _ in range(scrolls):
            # Scroll to a random position
            scroll_y = random.randint(100, height - 200)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_y});")
            time.sleep(random.uniform(0.5, 2))
    
    def _save_debug_screenshot(self):
        """Save a screenshot for debugging purposes."""
        try:
            os.makedirs("debug", exist_ok=True)
            filename = f"debug/screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(filename)
            print(f"Saved debug screenshot to {filename}")
            
            # Also save the page source
            with open(f"debug/page_source_{int(time.time())}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception as e:
            print(f"Could not save debug info: {str(e)}")
    
    def _extract_property_id(self, url: str) -> str:
        """Extract property ID from URL."""
        match = re.search(r'/(\d+)/?$', url)
        if match:
            return match.group(1)
        return "unknown"
    
    def _extract_property_data(self, metrics: List[DataPointConfig]) -> Dict[str, Any]:
        """Extract all property data from the loaded page."""
        property_info = {}
        
        # Extract property ID from URL
        property_id = self._extract_property_id(self.driver.current_url)
        if property_id:
            property_info['property_id'] = property_id
        
        # Create a new soup object from the current page
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Try to extract key information
        self._extract_basic_info(soup, property_info)
        
        # Extract details from object-kenmerken-list if present
        self._extract_details_table(soup, property_info)
        
        return property_info
    
    def _extract_basic_info(self, soup: BeautifulSoup, property_info: Dict[str, Any]):
        """Extract basic property information."""
        # Try to get property address/title using new selectors
        title_elem = soup.select_one('.md\\:pr-\\[4\\.2rem\\], h1')
        if title_elem:
            property_info['Property Name'] = title_elem.text.strip()
        
        # Try to get property price with new selectors
        price_elem = soup.select_one('.fd-color-price-primary, [data-testid*="price"]')
        if price_elem:
            price_text = price_elem.text.strip()
            property_info['Price'] = price_text
            # Also try to extract numeric price
            price_value = self._extract_price(price_text)
            if price_value:
                property_info['Price (numeric)'] = price_value
    
    def _extract_details_table(self, soup: BeautifulSoup, property_info: Dict[str, Any]):
        """Extract details from the property details table."""
        # Find all detail tables with new selectors
        detail_tables = soup.select('.grid.grid-cols-1.md\\:grid-cols-\\[35\\%_65\\%\\], .object-kenmerken-list, dl')
        
        for table in detail_tables:
            # Get all detail rows (dt/dd pairs)
            dt_elements = table.select('dt') or table.select('.grid div:nth-child(odd)')
            dd_elements = table.select('dd') or table.select('.grid div:nth-child(even)')
            
            # Process dt-dd pairs
            for dt, dd in zip(dt_elements, dd_elements):
                # Get the label and corresponding value
                label = dt.text.strip()
                value = dd.text.strip()
                
                if label and value:
                    # Map common property attributes
                    if any(keyword in label for keyword in ["Bouwjaar", "Built", "Construction"]):
                        property_info['Year Built'] = value
                    elif any(keyword in label for keyword in ["Woonoppervlakte", "Living area", "Usable area"]):
                        property_info['Living Area'] = value
                        # Try to extract numeric value
                        area_value = self._extract_number(value)
                        if area_value:
                            property_info['Living Area (m²)'] = area_value
                    elif any(keyword in label for keyword in ["Kamers", "Rooms"]):
                        property_info['Rooms'] = value
                    elif any(keyword in label for keyword in ["Energielabel", "Energy"]):
                        property_info['Energy Label'] = value
                    elif "Garage" in label:
                        property_info['Garage'] = value
                    elif any(keyword in label for keyword in ["Balkon", "Balcony"]):
                        property_info['Balcony'] = value
                    elif any(keyword in label for keyword in ["Tuin", "Garden"]):
                        property_info['Garden'] = value
                    elif any(keyword in label for keyword in ["Vraagprijs", "Price"]) and "€" in value:
                        property_info['Price'] = value
    
    def _extract_price(self, text: str) -> float:
        """Extract numeric price from price text."""
        if not text:
            return None
        
        # Remove currency symbols and normalize
        text = text.replace('€', '').replace('.', '').replace(',', '.').strip()
        
        # Find price pattern
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _extract_number(self, text: str) -> float:
        """Extract a numeric value from text."""
        if not text:
            return None
        
        # Find numeric pattern
        match = re.search(r'(\d+(?:[.,]\d+)?)', text)
        if match:
            try:
                # Normalize decimal separator
                value_text = match.group(1).replace(',', '.')
                return float(value_text)
            except (ValueError, TypeError):
                pass
        
        return None
    
    def generate_custom_mock_data(self, mock_metrics: List[DataPointConfig]) -> Dict[str, Any]:
        """Generate mock data based on the configured mock metrics from Excel."""
        mock_data = {}
        for metric in mock_metrics:
            field = metric.metric
            example = metric.example_data
            
            # Generate data based on metric name and example data
            if "Score" in field and "1-10" in field:
                # Score on a scale of 1-10
                mock_data[field] = round(random.uniform(1, 10), 1)
            
            elif "Rate" in field and "%" in field:
                # Percentage rate
                mock_data[field] = f"{round(random.uniform(0, 100), 1)}%"
            
            elif "Potential" in field and "%" in field:
                # Percentage potential
                mock_data[field] = f"{round(random.uniform(0, 100), 1)}%"
            
            elif "Volatility" in field:
                # Volatility percentage
                mock_data[field] = f"{round(random.uniform(0, 30), 1)}%"
            
            elif "History" in field:
                # Renovation history years
                years = [2015, 2018, 2020]
                renovations = [random.choice(["Minor", "Major", "None"]) for _ in range(random.randint(0, 3))]
                if renovations:
                    history = ", ".join([f"{years[i % len(years)]}: {renovations[i]}" for i in range(len(renovations))])
                    mock_data[field] = history
                else:
                    mock_data[field] = "No renovation history"
            
            elif "Type" in field:
                # Land ownership type
                types = ["Freehold", "Leasehold", "Shared Ownership"]
                mock_data[field] = random.choice(types)
        
        return mock_data
        
    def close(self):
        """Close the scraper and clean up resources."""
        self.close_driver() 