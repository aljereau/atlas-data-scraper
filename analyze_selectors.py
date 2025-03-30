import os
import re
from bs4 import BeautifulSoup

def analyze_html(html_path):
    """Analyze HTML structure to find appropriate selectors."""
    print(f"Analyzing HTML file: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Print page title for context
    title = soup.title.text if soup.title else "No title found"
    print(f"Page title: {title}")
    
    # Looking for property title/address
    print("\nSearching for property title/address...")
    potential_title_selectors = [
        'h1', 'h1.fd-m-top-xs', '.fd-m-top-xs',
        '.fd-h1', '.fd-flex--bp-m'
    ]
    
    for selector in potential_title_selectors:
        elements = soup.select(selector)
        for i, elem in enumerate(elements[:3]):  # Check first 3 of each selector type
            text = elem.text.strip()
            if text and len(text) > 5:
                print(f"Potential title ({selector}): {text[:100]}...")
    
    # Looking for price
    print("\nSearching for price...")
    potential_price_selectors = [
        '.fd-text-size-l', '.fd-color-price-primary',
        '[data-testid*="price"]', '.fd-u-font-bold'
    ]
    
    for selector in potential_price_selectors:
        elements = soup.select(selector)
        for i, elem in enumerate(elements[:5]):  # Check first 5 of each selector type
            text = elem.text.strip()
            if text and ('€' in text or 'euro' in text.lower()):
                print(f"Potential price ({selector}): {text}")
    
    # Looking for property details table
    print("\nSearching for property details table...")
    potential_table_selectors = [
        'dl', '.fd-dl', 'section', '.fd-p-horizontal-xl',
        '[data-testid*="kenmerken"]', '[data-testid*="features"]', '.fd-border-horizontal-remove-s'
    ]
    
    for selector in potential_table_selectors:
        elements = soup.select(selector)
        for i, elem in enumerate(elements[:3]):  # Check first 3 of each type
            # Look for dt/dd pairs or similar structures
            dts = elem.select('dt') or elem.select('.fd-dt')
            dds = elem.select('dd') or elem.select('.fd-dd')
            
            if dts and dds:
                print(f"Potential details table ({selector}):")
                for j, (dt, dd) in enumerate(zip(dts[:5], dds[:5])):  # Show first 5 pairs
                    dt_text = dt.text.strip()
                    dd_text = dd.text.strip()
                    if dt_text and dd_text:
                        print(f"  {dt_text}: {dd_text}")
    
    # Looking for key data attributes
    print("\nSearching for data-testid attributes...")
    elements_with_data = soup.select('[data-testid]')
    data_testids = {}
    
    for elem in elements_with_data:
        testid = elem.get('data-testid')
        if testid:
            text = elem.text.strip()
            if text:
                data_testids[testid] = text[:50] + ('...' if len(text) > 50 else '')
    
    for testid, text in list(data_testids.items())[:15]:  # Show first 15
        print(f"data-testid=\"{testid}\": {text}")
    
    # Generate recommendations
    print("\n----------- RECOMMENDED SELECTORS -----------")
    
    # Find a strong h1 or title element
    h1s = soup.select('h1')
    title_rec = None
    for h1 in h1s:
        text = h1.text.strip()
        if text and len(text) > 10 and any(char.isdigit() for char in text):
            title_rec = h1
            break
    
    if title_rec:
        print(f"Property Title: '{get_css_selector_of_element(title_rec)}'")
        print(f"  Example: {title_rec.text.strip()}")
    
    # Find price
    price_rec = None
    for elem in soup.select('.fd-color-price-primary, [data-testid*="price"]'):
        text = elem.text.strip()
        if text and '€' in text:
            price_rec = elem
            break
    
    if price_rec:
        print(f"Price: '{get_css_selector_of_element(price_rec)}'")
        print(f"  Example: {price_rec.text.strip()}")
    
    # Find details table
    details_table = None
    for elem in soup.select('dl, [data-testid*="kenmerken"]'):
        dts = elem.select('dt, .fd-dt')
        dds = elem.select('dd, .fd-dd')
        if len(dts) >= 3 and len(dds) >= 3:
            details_table = elem
            break
    
    if details_table:
        print(f"Details Table: '{get_css_selector_of_element(details_table)}'")
        print("  Example items:")
        dts = details_table.select('dt, .fd-dt')
        dds = details_table.select('dd, .fd-dd')
        for i, (dt, dd) in enumerate(zip(dts[:3], dds[:3])):
            print(f"    {dt.text.strip()}: {dd.text.strip()}")

def get_css_selector_of_element(element):
    """Generate a reasonable CSS selector for an element."""
    if element.get('id'):
        return f"#{element['id']}"
    
    if element.get('data-testid'):
        return f"[data-testid=\"{element['data-testid']}\"]"
    
    if element.get('class'):
        class_selector = '.{}'.format('.'.join(element['class']))
        return class_selector
    
    # If no good identifiers, use tag name and position
    return element.name

if __name__ == "__main__":
    # Find the most recent debug HTML file
    debug_dir = "debug"
    html_files = [f for f in os.listdir(debug_dir) if f.endswith('.html')]
    
    if html_files:
        # Sort by modification time (newest first)
        html_files.sort(key=lambda x: os.path.getmtime(os.path.join(debug_dir, x)), reverse=True)
        most_recent = os.path.join(debug_dir, html_files[0])
        analyze_html(most_recent)
    else:
        print("No HTML files found in debug directory.") 