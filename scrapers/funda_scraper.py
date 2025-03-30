from typing import Dict, List, Any
import re
import time
import random
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .base_scraper import BaseScraper
from utils.excel_config import ExcelConfigParser, DataPointConfig
from utils.request_utils import RequestThrottler, get_random_user_agent

class FundaScraper(BaseScraper):
    def __init__(self, config_path: str = "config/websites.json", 
                 excel_path: str = "reference_data/Ai Modeling Data File.xlsm"):
        super().__init__(config_path)
        self.excel_config = ExcelConfigParser(excel_path)
        self.throttler = RequestThrottler(min_delay=3.0, max_delay=7.0)  # Conservative delays
        self.setup_driver()  # Initialize Selenium driver
        self.funda_selectors = {
            # Basic property details
            'Property Name': {
                'selector': '.object-header__title',
                'type': 'text'
            },
            'Address': {
                'selector': '.object-header__title, .object-header__subtitle',
                'type': 'text',
                'combine': True
            },
            'Property Type': {
                'selector': '.fd-m-bottom-xs:contains("Soort")',
                'type': 'sibling'
            },
            'Square Meters (Living)': {
                'selector': '.fd-m-bottom-xs:contains("Woonoppervlakte")',
                'type': 'sibling'
            },
            'Number of Rooms': {
                'selector': '.fd-m-bottom-xs:contains("Aantal kamers")',
                'type': 'sibling'
            },
            'Construction Year': {
                'selector': '.fd-m-bottom-xs:contains("Bouwjaar")',
                'type': 'sibling'
            },
            'Energy Label': {
                'selector': '.energielabel',
                'type': 'text'
            },
            'Price': {
                'selector': '.object-header__price',
                'type': 'text'
            },
            'Asking Price': {
                'selector': '.object-header__price',
                'type': 'text'
            },
            'Price per M2': {
                'method': 'calculate',
                'requires': ['Price', 'Square Meters (Living)']
            }
        }

    def setup_driver(self):
        """Setup Selenium WebDriver with random user agent."""
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Set a random user agent
            user_agent = get_random_user_agent()
            chrome_options.add_argument(f"user-agent={user_agent}")
            
            # Set up the driver
            service = self._get_webdriver_service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set reasonable page load timeout
            self.driver.set_page_load_timeout(30)
            
            print(f"Browser initialized with user agent: {user_agent}")

    def scrape_properties(self) -> List[Dict[str, Any]]:
        """Scrape all properties from the provided Funda links."""
        property_data = []
        property_links = self.excel_config.get_property_links()
        funda_metrics = self.excel_config.get_funda_metrics()
        mock_metrics = self.excel_config.get_mock_metrics()

        total_properties = len(property_links)
        print(f"Starting to scrape {total_properties} properties from Funda...")

        for idx, link in enumerate(property_links):
            try:
                print(f"Scraping property {idx+1}/{total_properties}: {link}")
                # Apply throttling before each request
                self.throttler.throttle()
                
                property_info = self.scrape_single_property(link, funda_metrics)
                
                # Add mock data based on example data in Excel
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
                time.sleep(random.uniform(10, 15))

        return property_data

    def scrape_single_property(self, url: str, metrics: List[DataPointConfig]) -> Dict[str, Any]:
        """Scrape a single property from Funda."""
        try:
            self.driver.get(url)
            
            # Add a small delay to ensure page loads completely
            time.sleep(random.uniform(2, 3))
            
            # Create soup for parsing
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            property_info = {}

            # Extract property ID from URL
            property_id_match = re.search(r'/(\d+)/?$', url)
            if property_id_match:
                property_info['property_id'] = property_id_match.group(1)
            
            # Process each metric
            for metric in metrics:
                try:
                    metric_name = metric.metric
                    data = None
                    
                    # Check if we have a predefined selector for this metric
                    if metric_name in self.funda_selectors:
                        selector_info = self.funda_selectors[metric_name]
                        
                        if selector_info['type'] == 'text':
                            elements = soup.select(selector_info['selector'])
                            if elements:
                                if selector_info.get('combine', False):
                                    # Combine text from multiple elements
                                    data = ' '.join([e.get_text().strip() for e in elements])
                                else:
                                    data = elements[0].get_text().strip()
                        
                        elif selector_info['type'] == 'sibling':
                            # Find elements containing specified text, then get text from next sibling
                            elements = soup.select(selector_info['selector'])
                            if elements:
                                parent = elements[0].parent
                                siblings = list(parent.next_siblings)
                                for sibling in siblings:
                                    if hasattr(sibling, 'get_text'):
                                        data = sibling.get_text().strip()
                                        break
                        
                        elif selector_info['type'] == 'attribute':
                            elements = soup.select(selector_info['selector'])
                            if elements and selector_info.get('attribute'):
                                data = elements[0].get(selector_info['attribute'])
                        
                        elif selector_info['method'] == 'calculate':
                            # Handle calculated fields
                            if selector_info['requires']:
                                required_fields = selector_info['requires']
                                if all(field in property_info for field in required_fields):
                                    if metric_name == 'Price per M2':
                                        price = self._extract_number(property_info['Price'])
                                        area = self._extract_number(property_info['Square Meters (Living)'])
                                        if price and area and area > 0:
                                            data = round(price / area, 2)
                    
                    # If no data from predefined selectors, use area_on_page from Excel
                    if data is None and metric.area_on_page:
                        # Try to find element by text near the data point
                        elements = soup.find_all(text=re.compile(metric.area_on_page, re.IGNORECASE))
                        if elements:
                            # Get the parent element and look for nearby elements
                            parent = elements[0].parent
                            # Look for data in siblings or parent's siblings
                            data = self._extract_data_near_element(parent, metric)
                    
                    # Clean and format the data
                    if data is not None:
                        data = self._clean_data(data, metric.example_data)
                        property_info[metric_name] = data
                    
                except Exception as e:
                    print(f"Error scraping metric {metric.metric}: {str(e)}")
                    continue

            return property_info
            
        except Exception as e:
            print(f"Error loading page {url}: {str(e)}")
            # Add screenshot for debugging
            try:
                screenshot_path = f"errors/screenshot_{int(time.time())}.png"
                os.makedirs("errors", exist_ok=True)
                self.driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")
            except:
                pass
            raise

    def _extract_number(self, text: str) -> float:
        """Extract a number from text, handling various formats."""
        if not text:
            return None
            
        # Remove currency symbols, dots as thousand separators, and convert comma to dot
        cleaned = re.sub(r'[€$]', '', str(text))
        # Replace dots used as thousand separators, but only if there's a comma for decimal
        if ',' in cleaned:
            cleaned = cleaned.replace('.', '')
            cleaned = cleaned.replace(',', '.')
        
        # Find any number in the text
        match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
        if match:
            return float(match.group(1))
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
            
            else:
                # Default mock data
                if isinstance(example, (int, float)) or (isinstance(example, str) and example.replace('.', '', 1).isdigit()):
                    # Handle numeric data
                    try:
                        value = float(example) if '.' in str(example) else int(example)
                        # Generate value within 20% of the example
                        range_min = max(0, value * 0.8)
                        range_max = value * 1.2
                        mock_data[field] = round(random.uniform(range_min, range_max), 2 if '.' in str(example) else 0)
                    except (ValueError, TypeError):
                        mock_data[field] = random.randint(0, 100)
                else:
                    # Handle text data
                    options = ["High", "Medium", "Low", "Very High", "Very Low"]
                    mock_data[field] = random.choice(options)
                
        return mock_data

    def _extract_data_near_element(self, element: Any, metric: DataPointConfig) -> Any:
        """Extract data from near the found element based on metric type."""
        # Look in the element itself and its siblings
        for sibling in [element] + list(element.next_siblings) + list(element.previous_siblings):
            if hasattr(sibling, 'get_text'):
                text = sibling.get_text().strip()
                if text and text != metric.area_on_page:
                    return text
        return None

    def _clean_data(self, text: str, example_data: str) -> Any:
        """Clean and convert scraped data based on example data format."""
        if not text:
            return None
            
        try:
            # For price data
            if '€' in str(text) or 'eur' in str(text).lower():
                # Extract number from price
                number = self._extract_number(text)
                return number if number is not None else text
                
            # For area data
            if 'm²' in str(text) or 'm2' in str(text):
                # Extract number from area
                number = self._extract_number(text)
                return number if number is not None else text
                
            # For percentage data
            if '%' in str(text) or '%' in str(example_data):
                # Extract percentage value
                match = re.search(r'(\d+(?:[.,]\d+)?)\s*%', str(text))
                if match:
                    return f"{match.group(1)}%"
                return text
                
            # For general text
            return text.strip()
            
        except Exception as e:
            print(f"Error cleaning data: {str(e)}")
            return text

    def close(self):
        """Close the scraper and clean up resources."""
        self.close_driver() 