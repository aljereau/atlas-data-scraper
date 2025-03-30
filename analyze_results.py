import json
import os
import glob
from collections import Counter

def analyze_scraped_data():
    # Find the most recent JSON file in the data/raw directory
    json_files = glob.glob('data/raw/*.json')
    if not json_files:
        print("No JSON files found in data/raw directory.")
        return
    
    # Get the most recent file by modification time
    latest_file = max(json_files, key=os.path.getmtime)
    print(f"Analyzing file: {latest_file}")
    
    # Load the JSON data
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Basic statistics
    property_count = len(data)
    print(f"Total properties scraped: {property_count}")
    
    # Analyze which fields were successfully scraped
    print("\nFields captured in the data:")
    all_fields = set()
    field_counts = Counter()
    
    for property_data in data:
        fields = set(property_data.keys())
        all_fields.update(fields)
        for field in fields:
            field_counts[field] += 1
    
    # Print field statistics
    for field in sorted(all_fields):
        count = field_counts[field]
        percentage = (count / property_count) * 100
        print(f"  - {field}: {count} properties ({percentage:.1f}%)")
    
    # Analyze mock data
    mock_fields = [
        "Land Ownership Type",
        "Renovation History",
        "Vacancy Rate (%)",
        "Tenant Demand Score (1-10)",
        "Market Volatility (Price Swings %)",
        "Market Liquidity Score (1-10)",
        "Gov. Housing Regs Score (1-10)",
        "Short-Term Rental Potential (%)"
    ]
    
    print("\nMock Data Analysis:")
    for field in mock_fields:
        if field in field_counts:
            # Collect all values for this field
            values = [p.get(field) for p in data if field in p]
            if values:
                if field == "Land Ownership Type":
                    # Count different types
                    type_counts = Counter(values)
                    print(f"  - {field}:")
                    for type_name, count in type_counts.most_common():
                        print(f"      {type_name}: {count} properties")
                
                elif "Score" in field:
                    # Analyze numeric scores
                    try:
                        numeric_values = [float(v) for v in values if v is not None]
                        if numeric_values:
                            avg = sum(numeric_values) / len(numeric_values)
                            min_val = min(numeric_values)
                            max_val = max(numeric_values)
                            print(f"  - {field}: Avg: {avg:.1f}, Min: {min_val:.1f}, Max: {max_val:.1f}")
                    except (ValueError, TypeError):
                        print(f"  - {field}: Could not analyze numeric values")
                
                elif "%" in field:
                    # Analyze percentage fields
                    print(f"  - {field}: {len(values)} values")
                    
                else:
                    # General field
                    print(f"  - {field}: {len(values)} values")

if __name__ == "__main__":
    analyze_scraped_data() 