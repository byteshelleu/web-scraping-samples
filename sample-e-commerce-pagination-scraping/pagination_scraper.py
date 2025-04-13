"""Main script for scraping e-commerce website with pagination."""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

import config
from logger import setup_logger
from pagination_page import PaginationPage
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
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # Use a direct approach without ChromeDriverManager to avoid compatibility issues
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def scrape_current_page(page, max_pages=config.MAX_PAGES):
    """Scrape products from the current page with pagination.
    
    Args:
        page: PaginationPage instance
        max_pages: Maximum number of pages to scrape
        
    Returns:
        List of product dictionaries
    """
    logger = logging.getLogger(__name__)
    
    # Get current URL for logging
    current_url = page.driver.current_url
    logger.info(f"Scraping products from: {current_url}")
    
    # Extract products with pagination
    products = page.extract_products_from_all_pages(max_pages=max_pages)
    
    logger.info(f"Found {len(products)} products on pages at {current_url}")
    
    return products


def run_scraper():
    """Run the e-commerce pagination scraper.
    
    Returns:
        Number of products scraped
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting e-commerce pagination scraper")
    
    # Initialize WebDriver
    driver = setup_driver(headless=config.HEADLESS_MODE)
    
    # Initialize page object and data handler
    page = PaginationPage(driver, timeout=config.WAIT_TIMEOUT)
    data_handler = DataHandler()
    
    # Load the base website
    page_loaded = page.load(config.BASE_URL)
    if not page_loaded:
        logger.error(f"Failed to load page: {config.BASE_URL}")
        driver.quit()
        return 0

    logger.info(f"Loaded page: {config.BASE_URL}")

    # Get all products from all pages and categories
    all_products = []
    categories = page.get_categories()
    
    if not categories:
        logger.warning("No categories found")
        
        # If no categories found, at least process the current page
        products = page.extract_products_from_all_pages(max_pages=config.MAX_PAGES)
        all_products.extend(products)
    else:
        # Process each main category
        for category_name, category_element in categories.items():
            logger.info(f"Processing category: {category_name}")
            
            # Navigate to the category
            success = page.navigate_to_category(category_name)
            if success:
                # Get products from main category page
                category_products = page.extract_products_from_all_pages(max_pages=config.MAX_PAGES)
                logger.info(f"Found {len(category_products)} products in category {category_name}")
                
                all_products.extend(category_products)
                
                # Get subcategories for this category
                subcategories = page.get_subcategories(category_name)
                
                if subcategories:
                    # Process each subcategory
                    for subcategory_name, subcategory_element in subcategories.items():
                        logger.info(f"Processing subcategory: {subcategory_name}")
                        
                        # Navigate to the subcategory
                        success = page.navigate_to_subcategory(category_name, subcategory_name)
                        if success:
                            # Scrape all pages in this subcategory with pagination
                            subcategory_products = page.extract_products_from_all_pages(max_pages=config.MAX_PAGES)
                            logger.info(f"Found {len(subcategory_products)} products in subcategory {subcategory_name}")
                            
                            all_products.extend(subcategory_products)
                        
                        # Go back to main category for next subcategory
                        page.load(config.BASE_URL)
                        page.navigate_to_category(category_name)
                else:
                    logger.info(f"No subcategories found for {category_name}")
            
            # Return to home page for next category
            page.load(config.BASE_URL)

    # Remove duplicate products based on title + price + description
    unique_products = []
    seen_identifiers = set()
    
    for product in all_products:
        title = product.get('title', '')
        price = product.get('price', '')
        description = product.get('description', '')[:50] if product.get('description') else ''
        
        # Create a composite identifier like the scrolling scraper
        product_id = f"{title}|{price}|{description}"
        
        if product_id and product_id not in seen_identifiers:
            seen_identifiers.add(product_id)
            unique_products.append(product)
        else:
            logger.debug(f"Skipping duplicate product: {title}")
    
    logger.info(f"Total unique products found: {len(unique_products)} (from {len(all_products)} total)")
    
    # Process all extracted products
    processed_products = data_handler.process_product_data(unique_products)

    # Save to CSV
    if processed_products:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.OUTPUT_FILE)
        data_handler.save_to_csv(processed_products, csv_path)

    # Clean up WebDriver
    driver.quit()
    logger.info("WebDriver closed")

    # Return the number of products scraped
    return len(unique_products)


if __name__ == "__main__":
    # Set up logger
    setup_logger()
    
    # Run the scraper
    products_count = run_scraper()
    
    # Log completion
    logging.getLogger().info(f"Scraping complete. Extracted {products_count} products.")
