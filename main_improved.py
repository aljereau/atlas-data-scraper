import os
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from scrapers.improved_funda_scraper import ImprovedFundaScraper
from post_process import clean_property_data, convert_to_csv

def ensure_dirs():
    """Ensure required directories exist."""
    directories = ['data/raw', 'data/processed', 'logs', 'debug']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def save_data(data, filename):
    """Save scraped data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")

def setup_logging():
    """Setup logging to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/scraper_log_{timestamp}.txt"
    
    # Create a custom stdout that writes to both console and file
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, 'w', encoding='utf-8')
            
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            
        def flush(self):
            self.terminal.flush()
            self.log.flush()
    
    sys.stdout = Logger(log_file)
    print(f"Logging to {log_file}")

def main():
    """Main function to run the improved scraper and post-processing."""
    print(f"Starting Atlast Data Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ensure_dirs()
    setup_logging()
    
    # Configure the scraper with Excel path
    excel_path = "reference_data/Ai Modeling Data File.xlsm"
    print(f"Using Excel configuration from: {excel_path}")
    
    # Timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_output_file = f"data/raw/funda_data_{timestamp}.json"
    processed_json = f"data/processed/funda_data_cleaned_{timestamp}.json"
    processed_csv = f"data/processed/funda_data_cleaned_{timestamp}.csv"
    
    try:
        # Initialize the Funda scraper
        print("Initializing Funda scraper...")
        scraper = ImprovedFundaScraper(excel_path=excel_path)
        
        # Scrape property data
        print("Beginning property scraping...")
        start_time = time.time()
        property_data = scraper.scrape_properties()
        scrape_end_time = time.time()
        
        # Save the raw scraped data
        save_data(property_data, raw_output_file)
        
        # Print scraping summary
        scrape_duration = scrape_end_time - start_time
        print(f"Scraping completed in {scrape_duration:.2f} seconds")
        print(f"Scraped {len(property_data)} properties from Funda")
        
        # Post-process the data
        print("\nPost-processing the scraped data...")
        post_start_time = time.time()
        
        # Clean and standardize the data
        cleaned_data = clean_property_data(property_data)
        
        # Save cleaned data as JSON
        with open(processed_json, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        print(f"Cleaned data saved to: {processed_json}")
        
        # Convert to CSV
        convert_to_csv(cleaned_data, processed_csv)
        
        post_end_time = time.time()
        post_duration = post_end_time - post_start_time
        
        # Print a summary of the data
        print("\nData Summary:")
        print(f"Total properties: {len(cleaned_data)}")
        
        # Count properties with various fields
        field_counts = {}
        for prop in cleaned_data:
            for key in prop:
                if key not in field_counts:
                    field_counts[key] = 0
                if prop[key] is not None and prop[key] != "":
                    field_counts[key] += 1
        
        print("\nField coverage:")
        for key, count in sorted(field_counts.items()):
            percentage = (count / len(cleaned_data)) * 100
            print(f"  {key}: {count}/{len(cleaned_data)} ({percentage:.1f}%)")
        
        # Final timing summary
        total_duration = post_end_time - start_time
        print(f"\nTiming Summary:")
        print(f"  Scraping: {scrape_duration:.2f} seconds")
        print(f"  Post-processing: {post_duration:.2f} seconds")
        print(f"  Total execution: {total_duration:.2f} seconds")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure scraper is properly closed
        if 'scraper' in locals():
            scraper.close()
            print("Scraper resources released")
    
    print(f"Scraping process completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 