# Atlas Data Scraper

A robust web scraper for collecting property data from Funda's real estate listings, featuring enhanced anti-detection measures and comprehensive data processing.

## Features

- **Robust Scraping**: Ethically scrapes real estate data from Funda with appropriate throttling and anti-detection measures
- **Smart Retry Logic**: Automatically retries failed requests with exponential backoff
- **Data Processing**: Cleans and structures scraped data for analysis
- **Multiple Export Formats**: Saves data in both JSON and CSV formats
- **Comprehensive Logging**: Detailed logs of the scraping process for debugging and monitoring

## Project Structure

```
├── config/                  # Configuration files
│   └── websites.json        # Website-specific configuration
├── data/                    # Data storage
│   ├── raw/                 # Raw scraped data
│   └── processed/           # Cleaned and processed data
├── debug/                   # Debug information (screenshots, HTML)
├── logs/                    # Logging output
├── reference_data/          # Reference data (Excel spreadsheets)
├── scrapers/                # Scraper implementations
│   ├── base_scraper.py      # Base scraper class
│   ├── funda_scraper.py     # Original Funda scraper
│   └── improved_funda_scraper.py # Enhanced Funda scraper with anti-detection
├── utils/                   # Utility functions
│   ├── excel_config.py      # Excel configuration parser
│   └── request_utils.py     # HTTP request utilities
├── analyze_excel.py         # Script to analyze Excel data
├── analyze_results.py       # Script to analyze scraped data
├── analyze_selectors.py     # Tool to analyze HTML selectors
├── debug_funda.py           # Debug script for Funda scraping
├── main.py                  # Main entry point for original scraper
├── main_improved.py         # Main entry point for improved scraper
├── post_process.py          # Data post-processing functions
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/atlas-data-scraper.git
cd atlas-data-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Scraper

To run the improved scraper with all anti-detection features:

```bash
python main_improved.py
```

This will:
1. Scrape property data from Funda
2. Save raw data to `data/raw/`
3. Process and clean the data
4. Save processed data to `data/processed/` (both JSON and CSV formats)
5. Generate a detailed log in `logs/`

### Analyzing Results

To analyze the scraped data:

```bash
python analyze_results.py
```

## Ethical Considerations

This scraper is designed for educational purposes and personal use. Please respect:

- Funda's terms of service
- Rate limiting through appropriate throttling
- Ethical web scraping practices

## Troubleshooting

If you encounter issues with anti-scraping measures:

1. Check the debug screenshots in the `debug/` directory
2. Adjust throttling parameters in `scrapers/improved_funda_scraper.py`
3. Try rotating user agents or using proxies (requires implementation)

## Dependencies

- Python 3.8+
- Selenium
- BeautifulSoup4
- Pandas
- Requests
- Faker

## License

This project is licensed under the MIT License - see the LICENSE file for details.
