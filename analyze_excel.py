import pandas as pd
import os
import numpy as np

def analyze_excel_file():
    print("Analyzing Excel file 'Ai Modeling Data File.xlsm'...")
    
    # Path to the Excel file
    file_path = os.path.join('reference_data', 'Ai Modeling Data File.xlsm')
    
    # Get all sheet names
    xl = pd.ExcelFile(file_path)
    sheet_names = xl.sheet_names
    print(f"Sheet names: {sheet_names}\n")
    
    # For each sheet, display basic information
    for sheet in sheet_names:
        print(f"===== Sheet: {sheet} =====")
        df = pd.read_excel(file_path, sheet_name=sheet)
        df = df.replace(np.nan, '', regex=True)  # Replace NaN with empty string for display
        
        # Display column names
        print(f"Columns: {df.columns.tolist()}")
        
        # Display shape of dataframe
        print(f"Shape: {df.shape} (rows, columns)")
        
        # Display sample of data (first 5 rows) with better formatting
        print("\nSample data (first 5 rows or less):")
        if df.shape[0] > 0:
            sample_rows = min(5, df.shape[0])
            for idx, row in df.iloc[:sample_rows].iterrows():
                print(f"\nRow {idx}:")
                for col in df.columns:
                    value = row[col]
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:97] + "..."
                    print(f"  {col}: {value}")
        else:
            print("  [No data in this sheet]")
        
        print("\n")
    
    # Specific analysis for property details sheet
    prop_sheet = next((s for s in sheet_names if 'property' in s.lower()), None)
    if prop_sheet:
        print(f"===== Property Details Analysis =====")
        property_df = pd.read_excel(file_path, sheet_name=prop_sheet)
        
        # Look for column that might contain links
        link_cols = [col for col in property_df.columns if 'link' in str(col).lower()]
        if link_cols:
            for link_col in link_cols:
                valid_links = property_df[link_col].dropna().tolist()
                print(f"Column '{link_col}' has {len(valid_links)} non-empty values")
                print("Sample values:")
                for link in valid_links[:3]:
                    print(f"  - {link}")
                print()
        else:
            print("No columns containing 'link' found in Property Details sheet\n")
    
    # Specific analysis for example data sheet
    example_sheet = next((s for s in sheet_names if 'example' in s.lower()), None)
    if example_sheet:
        print(f"===== Example Data Analysis =====")
        example_df = pd.read_excel(file_path, sheet_name=example_sheet)
        
        # Count unique categories
        cat_col = next((col for col in example_df.columns if 'category' in str(col).lower()), None)
        if cat_col:
            categories = example_df[cat_col].dropna().unique()
            print(f"Unique categories: {len(categories)}")
            for cat in categories:
                count = len(example_df[example_df[cat_col] == cat])
                print(f"  - {cat} ({count} items)")
            print()
        
        # Count data sources
        source_col = next((col for col in example_df.columns if 'source' in str(col).lower() and 'url' not in str(col).lower()), None)
        if source_col:
            sources = example_df[source_col].dropna().unique()
            print(f"Unique data sources: {len(sources)}")
            for source in sources:
                if isinstance(source, str):
                    count = len(example_df[example_df[source_col] == source])
                    print(f"  - {source} ({count} items)")
            print()
            
            # Count mock data points
            mock_data = example_df[example_df[source_col].astype(str).str.contains('mock', case=False, na=False)]
            print(f"Number of mock data points: {len(mock_data)}")
            if not mock_data.empty:
                mock_metrics = mock_data.get('Metric', mock_data.iloc[:, 1])  # Fallback to second column if 'Metric' not found
                print("Mock data metrics:")
                for metric in mock_metrics:
                    print(f"  - {metric}")
            print()

if __name__ == "__main__":
    analyze_excel_file() 