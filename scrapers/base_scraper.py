import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker

class BaseScraper(ABC):
    def __init__(self, config_path: str = "config/websites.json"):
        self.config = self._load_config(config_path)
        self.faker = Faker()
        self.driver = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _get_webdriver_service(self):
        """Get the appropriate webdriver service."""
        return Service(ChromeDriverManager().install())

    def setup_driver(self):
        """Setup Selenium WebDriver if needed."""
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = self._get_webdriver_service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    @abstractmethod
    def scrape_properties(self) -> List[Dict[str, Any]]:
        """Scrape properties from the website."""
        pass

    def generate_mock_data(self) -> Dict[str, Any]:
        """Generate mock data for alternative metrics."""
        mock_data = {}
        for field in self.config['data_structure']['mock_fields']:
            if field == 'neighborhood_crime_rate':
                mock_data[field] = round(self.faker.random_number(digits=2) / 100 * 100, 2)
            elif field == 'school_rating':
                mock_data[field] = round(self.faker.random_number(digits=1) / 10 * 10, 1)
            elif field == 'future_development_potential':
                mock_data[field] = round(self.faker.random_number(digits=2) / 100 * 100, 2)
            elif field == 'market_trend_score':
                mock_data[field] = round((self.faker.random_number(digits=3) / 1000 * 200) - 100, 2)
            elif field == 'infrastructure_score':
                mock_data[field] = round(self.faker.random_number(digits=2) / 100 * 100, 2)
        return mock_data

    def save_data(self, data: List[Dict[str, Any]], filename: str):
        """Save scraped data to JSON file."""
        os.makedirs('data/raw', exist_ok=True)
        with open(f'data/raw/{filename}', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False) 