"""Main script for scraping scrolling e-commerce website."""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

import config
from logger import setup_logger
from scrolling_page import ScrollingPage
from data_handler import DataHandler
from locators import ScrollingEcommerceLocators


def setup_driver(headless=True):
    """Set up the Selenium WebDriver.
    
    Args:
        headless: Whether to run the browser in headless mode
        
    Returns:
        Configured WebDriver instance
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    
    # Use a direct approach without ChromeDriverManager to avoid compatibility issues
    driver = webdriver.Chrome(options=chrome_options)
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
    
    # Load the base website
    page_loaded = page.load(config.BASE_URL)
    if not page_loaded:
        logger.error(f"Failed to load page: {config.BASE_URL}")
        driver.quit()
        return 0
        
    logger.info(f"Loaded page: {config.BASE_URL}")
    
    # Get all main categories
    all_products = []
    categories = page.get_categories()
    
    # If no categories found, scrape the main page
    if not categories:
        logger.info("No categories found. Scraping main page.")
        products = scrape_current_page(page)
        all_products.extend(products)
    else:
        # Iterate through each category
        for category_name, category_element in categories.items():
            logger.info(f"Processing category: {category_name}")
            
            # Navigate to the category
            success = page.navigate_to_category(category_name)
            if success:
                # Scrape the category page
                category_products = scrape_current_page(page)
                all_products.extend(category_products)
                
                # Get subcategories for this category
                subcategories = page.get_subcategories(category_name)
                
                # Process each subcategory
                for subcategory_name, subcategory_element in subcategories.items():
                    logger.info(f"Processing subcategory: {subcategory_name}")
                    
                    # Navigate to the subcategory
                    success = page.navigate_to_subcategory(category_name, subcategory_name)
                    if success:
                        # Scrape the subcategory page
                        subcategory_products = scrape_current_page(page)
                        all_products.extend(subcategory_products)
                    
                    # Navigate back to main page to continue with next category
                    page.load(config.BASE_URL)
            else:
                logger.warning(f"Failed to navigate to category: {category_name}")
    
    logger.info(f"Total products found across all categories: {len(all_products)}")
    
    # Process all extracted products
    processed_products = data_handler.process_product_data(all_products)
    
    # Save to CSV
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.OUTPUT_FILE)
    success = data_handler.save_to_csv(processed_products, output_file)
    
    # Clean up
    driver.quit()
    logger.info("WebDriver closed")
    
    return len(processed_products)


def scrape_current_page(page):
    """Scrape products from the current page.
    
    Args:
        page: ScrollingPage instance
        
    Returns:
        List of product dictionaries
    """
    logger = logging.getLogger(__name__)
    
    # Get current URL for logging
    current_url = page.driver.current_url
    logger.info(f"Scraping products from: {current_url}")
    
    # Scroll and extract products
    start_time = time.time()
    products = page.scroll_and_extract_products(
        max_scrolls=config.MAX_SCROLLS,
        scroll_pause_time=config.SCROLL_PAUSE_TIME
    )
    end_time = time.time()
    
    logger.info(f"Extraction complete. Time taken: {end_time - start_time:.2f} seconds")
    logger.info(f"Found {len(products)} products on this page")
    
    return products


if __name__ == "__main__":
    # Set up logger
    setup_logger()
    
    # Run the scraper
    product_count = run_scraper()
    
    logging.info(f"Scraping complete. Extracted {product_count} products.")
