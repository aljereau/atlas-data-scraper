import os
import json
import re
import glob
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

def find_latest_raw_file() -> str:
    """Find the most recent JSON file in the data/raw directory."""
    json_files = glob.glob('data/raw/*.json')
    if not json_files:
        raise FileNotFoundError("No JSON files found in data/raw directory")
    
    # Sort by modification time (newest first)
    latest_file = max(json_files, key=os.path.getmtime)
    return latest_file

def clean_text(text: str) -> str:
    """Clean and fix character encoding issues in text."""
    if not text or not isinstance(text, str):
        return text
    
    # Fix common encoding issues
    replacements = {
        'â‚¬': '€',
        'Â': '',
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ã«': 'ë',
        'Ã¯': 'ï',
        'Ã´': 'ô',
        'Ã¶': 'ö',
        'Ã¼': 'ü',
        'Ã»': 'û'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def extract_numeric_price(price_text: str) -> float:
    """Extract numeric price from price text."""
    if not price_text:
        return None
    
    # Clean the text first
    price_text = clean_text(price_text)
    
    # Extract just the price part if it contains additional text
    price_match = re.search(r'€\s*([\d.,]+)', price_text)
    if price_match:
        price_str = price_match.group(1).replace('.', '').replace(',', '.')
        try:
            return float(price_str)
        except ValueError:
            pass
    
    return None

def extract_area(area_text: str) -> float:
    """Extract numeric area from area text."""
    if not area_text:
        return None
    
    # Clean the text first
    area_text = clean_text(area_text)
    
    # Extract just the area part if it contains additional text
    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*m[²²]', area_text)
    if area_match:
        area_str = area_match.group(1).replace(',', '.')
        try:
            return float(area_str)
        except ValueError:
            pass
    
    return None

def extract_year_built(year_text: str) -> int:
    """Extract year built as an integer."""
    if not year_text:
        return None
    
    # Extract just the year if it contains additional text
    year_match = re.search(r'(\d{4})', year_text)
    if year_match:
        try:
            return int(year_match.group(1))
        except ValueError:
            pass
    
    return None

def clean_property_data(property_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean and standardize the scraped property data."""
    cleaned_data = []
    
    for prop in property_data:
        cleaned_prop = {}
        
        # Copy and clean each field
        for key, value in prop.items():
            if isinstance(value, str):
                cleaned_prop[key] = clean_text(value)
            else:
                cleaned_prop[key] = value
        
        # Extract property address from Property Name if possible
        if 'Property Name' in cleaned_prop:
            name = cleaned_prop['Property Name']
            # Try to extract address and postcode
            address_match = re.search(r'([^\d]+\d+(?:[\-\s]*[a-zA-Z0-9]+)?)[^\d]*(\d{4}\s*[A-Z]{2})?', name)
            if address_match:
                address = address_match.group(1).strip()
                postcode = address_match.group(2).strip() if address_match.group(2) else None
                
                if address:
                    cleaned_prop['Address'] = address
                if postcode:
                    cleaned_prop['Postal Code'] = postcode
        
        # Extract and standardize price
        if 'Price' in cleaned_prop:
            price_numeric = extract_numeric_price(cleaned_prop['Price'])
            if price_numeric:
                cleaned_prop['Price (numeric)'] = price_numeric
        
        # Process Year Built
        if 'Year Built' in cleaned_prop:
            year_built = extract_year_built(cleaned_prop['Year Built'])
            if year_built:
                cleaned_prop['Year Built'] = year_built
        
        # Clean percentages and ensure numeric values
        for key in cleaned_prop:
            if isinstance(cleaned_prop[key], str) and '%' in cleaned_prop[key]:
                try:
                    # Convert percentage strings to actual numeric values
                    cleaned_prop[key] = float(cleaned_prop[key].replace('%', '').strip())
                except ValueError:
                    pass
        
        cleaned_data.append(cleaned_prop)
    
    return cleaned_data

def convert_to_csv(cleaned_data: List[Dict[str, Any]], output_file: str):
    """Convert the cleaned data to a CSV file."""
    # Convert to DataFrame
    df = pd.DataFrame(cleaned_data)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Data exported to CSV: {output_file}")

def post_process_data():
    """Main function to post-process the scraped data."""
    try:
        # Find the latest raw data file
        latest_file = find_latest_raw_file()
        print(f"Processing file: {latest_file}")
        
        # Load the raw data
        with open(latest_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        print(f"Loaded {len(raw_data)} properties")
        
        # Clean and standardize the data
        cleaned_data = clean_property_data(raw_data)
        
        # Create timestamp for output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save cleaned data as JSON
        processed_json = f"data/processed/funda_data_cleaned_{timestamp}.json"
        os.makedirs('data/processed', exist_ok=True)
        with open(processed_json, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        print(f"Cleaned data saved to: {processed_json}")
        
        # Convert to CSV
        processed_csv = f"data/processed/funda_data_cleaned_{timestamp}.csv"
        convert_to_csv(cleaned_data, processed_csv)
        
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
        
    except Exception as e:
        print(f"Error during post-processing: {str(e)}")

if __name__ == "__main__":
    post_process_data() 