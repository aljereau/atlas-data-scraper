import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_stealth_browser():
    """Setup a browser with anti-detection measures."""
    chrome_options = Options()
    
    # Core stealth options
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-browser-side-navigation")
    
    # Comment this out to see the browser window
    # chrome_options.add_argument("--headless")
    
    # Set a realistic user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    # Extra stealth settings
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Set up the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set reasonable page load timeout
    driver.set_page_load_timeout(30)
    
    # Execute CDP commands to hide automation
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    return driver

def debug_funda():
    """Debug Funda website access."""
    driver = None
    try:
        print("Setting up browser...")
        driver = setup_stealth_browser()
        
        # Get an example Funda URL from the Excel file (simplified for debug)
        # You could hard-code a test URL here or extract from the Excel
        example_url = "https://www.funda.nl/koop/amsterdam/appartement-43832980-frans-halsstraat-40-hs/"
        
        print(f"Loading URL: {example_url}")
        driver.get(example_url)
        
        # Add random waiting to simulate human behavior
        time.sleep(random.uniform(5, 8))
        
        # Save page source and screenshot for debugging
        os.makedirs("debug", exist_ok=True)
        screenshot_path = f"debug/funda_debug_screenshot_{int(time.time())}.png"
        html_path = f"debug/funda_debug_source_{int(time.time())}.html"
        
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"HTML source saved to {html_path}")
        
        # Check for common anti-bot indicators
        print(f"Page title: {driver.title}")
        
        # Check for key elements
        print("\nChecking for key elements:")
        elements_to_check = {
            "Property title": ".object-header__title",
            "Price": ".object-header__price",
            "Details table": ".object-kenmerken-list",
            "Main content": ".object-primary"
        }
        
        for name, selector in elements_to_check.items():
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Found: {name} ({selector})")
                print(f"  Text: {element.text[:100]}..." if element.text else "  No text")
            except Exception as e:
                print(f"✗ Not found: {name} ({selector})")
        
        # Check if we hit a protection page
        if "Je bent bijna op de pagina die je zoekt" in driver.title:
            print("\n⚠ PROTECTION PAGE DETECTED! We're being blocked.")
        elif "Toegang geweigerd" in driver.title or "Access denied" in driver.title:
            print("\n⚠ ACCESS DENIED PAGE DETECTED! IP might be blocked.")
        else:
            print("\nNo obvious protection page detected.")
            
        # Additional useful debug info
        cookies = driver.get_cookies()
        print(f"\nNumber of cookies: {len(cookies)}")
        
    except Exception as e:
        print(f"Error during debug: {str(e)}")
    finally:
        if driver:
            driver.quit()
            print("Browser closed")

if __name__ == "__main__":
    debug_funda() 