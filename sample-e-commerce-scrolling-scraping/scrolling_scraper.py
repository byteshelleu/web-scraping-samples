"""Main script for scraping scrolling e-commerce website."""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import logging

import config
from logger import setup_logger
from scrolling_page import ScrollingPage
from data_handler import DataHandler

def setup_driver(headless=True):
    """Set up the Selenium WebDriver.
    
    Args:
        headless: Whether to run the browser in headless mode
        
    Returns:
        Configured WebDriver instance
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    
    # Set up Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def run_scraper():
    """Run the scrolling e-commerce scraper.
    
    Returns:
        Number of products scraped
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting scrolling e-commerce scraper")
    
    # Initialize WebDriver
    driver = setup_driver(headless=config.HEADLESS_MODE)
    driver.maximize_window()
    
    # Initialize page object and data handler
    page = ScrollingPage(driver, timeout=config.WAIT_TIMEOUT)
    data_handler = DataHandler()
    
    # Load the website
    page_loaded = page.load(config.BASE_URL)
    if not page_loaded:
        logger.error(f"Failed to load page: {config.BASE_URL}")
        driver.quit()
        return 0
        
    logger.info(f"Loaded page: {config.BASE_URL}")
    
    # Scroll and extract products
    start_time = time.time()
    products = page.scroll_and_extract_products(
        max_scrolls=config.MAX_SCROLLS,
        scroll_pause_time=config.SCROLL_PAUSE_TIME
    )
    end_time = time.time()
    
    logger.info(f"Extraction complete. Time taken: {end_time - start_time:.2f} seconds")
    logger.info(f"Found {len(products)} products")
    
    # Process the extracted products
    processed_products = data_handler.process_product_data(products)
    
    # Save to CSV
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.OUTPUT_FILE)
    success = data_handler.save_to_csv(processed_products, output_file)
    
    # Clean up
    driver.quit()
    logger.info("WebDriver closed")
    
    return len(processed_products)

if __name__ == "__main__":
    # Set up logger
    setup_logger()
    
    # Run the scraper
    product_count = run_scraper()
    
    logging.info(f"Scraping complete. Extracted {product_count} products.")
