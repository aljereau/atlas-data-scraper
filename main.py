import os
import json
import time
from pathlib import Path
from scrapers.improved_funda_scraper import ImprovedFundaScraper

def ensure_dirs():
    """Ensure required directories exist."""
    directories = ['data/raw', 'data/processed', 'logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def save_data(data, filename):
    """Save scraped data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")

def main():
    """Main function to run the scraper."""
    print("Starting Atlast Data Scraper")
    ensure_dirs()
    
    # Configure the scraper with Excel path
    excel_path = "reference_data/Ai Modeling Data File.xlsm"
    print(f"Using Excel configuration from: {excel_path}")
    
    try:
        # Initialize the Funda scraper
        print("Initializing Funda scraper...")
        scraper = ImprovedFundaScraper(excel_path=excel_path)
        
        # Scrape property data
        print("Beginning property scraping...")
        start_time = time.time()
        property_data = scraper.scrape_properties()
        end_time = time.time()
        
        # Generate output filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"data/raw/funda_data_{timestamp}.json"
        
        # Save the scraped data
        save_data(property_data, output_file)
        
        # Print summary
        print(f"Scraping completed in {end_time - start_time:.2f} seconds")
        print(f"Scraped {len(property_data)} properties from Funda")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
    finally:
        # Ensure scraper is properly closed
        if 'scraper' in locals():
            scraper.close()
            print("Scraper resources released")
    
    print("Scraping process completed")

if __name__ == "__main__":
    main() 