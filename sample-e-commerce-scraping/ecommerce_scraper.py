"""Main script for the e-commerce scraper."""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Add absolute imports to ensure script runs locally
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ecommerce_page import EcommercePage
from data_handler import DataHandler
from config import BASE_URL, HEADLESS_MODE, OUTPUT_FILE
from logger import logger


def setup_driver():
    """Set up and configure the WebDriver.
    
    Returns:
        WebDriver instance or None if setup fails
    """
    logger.info("Setting up WebDriver")
    chrome_options = Options()

    if HEADLESS_MODE:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Use the known working ChromeDriver path
    driver_path = r"C:\Users\drago\.wdm\drivers\chromedriver\win64\130.0.6723.58\chromedriver-win32\chromedriver.exe"

    if not os.path.exists(driver_path):
        logger.error(f"ChromeDriver not found at {driver_path}")
        return None

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    logger.info("WebDriver initialized")
    return driver


def process_products_page(ecommerce_page, category_path):
    """Process a single page of products.
    
    Args:
        ecommerce_page: EcommercePage instance
        category_path: String representing the category path (e.g., "Computers > Laptops")
        
    Returns:
        List of products from the current page
    """
    # Wait for products to load
    time.sleep(2)

    # Get all products from current page
    products = ecommerce_page.get_products_on_page()

    # Add category path information to products
    for product in products:
        product['category_path'] = category_path

    logger.info(f"Extracted {len(products)} products from {category_path}")
    return products


def process_pagination(ecommerce_page, category_path):
    """Process pagination for the current page.
    
    Args:
        ecommerce_page: EcommercePage instance
        category_path: String representing the category path
        
    Returns:
        List of products from additional pages
    """
    pagination_products = []
    page_counter = 1

    while ecommerce_page.has_next_page():
        logger.info(f"Navigating to page {page_counter + 1}")

        navigation_success = ecommerce_page.go_to_next_page()
        if not navigation_success:
            logger.warning("Failed to navigate to next page, stopping pagination")
            break

        # Process products on the next page
        page_products = process_products_page(ecommerce_page, category_path)
        pagination_products.extend(page_products)

        page_counter += 1

    return pagination_products


def process_subcategory(ecommerce_page, parent_category, subcategory_name):
    """Process a subcategory and extract all products.
    
    Args:
        ecommerce_page: EcommercePage instance
        parent_category: Name of the parent category
        subcategory_name: Name of the subcategory
        
    Returns:
        List of products in the subcategory
    """
    category_path = f"{parent_category} > {subcategory_name}"
    logger.info(f"Processing subcategory: {category_path}")

    # Navigate to the subcategory
    navigation_success = ecommerce_page.navigate_to_subcategory(parent_category, subcategory_name)
    if not navigation_success:
        logger.warning(f"Failed to navigate to subcategory {subcategory_name}, skipping")
        return []

    # Get products from the first page
    products = process_products_page(ecommerce_page, category_path)

    # Process pagination if available
    pagination_products = process_pagination(ecommerce_page, category_path)
    products.extend(pagination_products)

    logger.info(f"Total products in {category_path}: {len(products)}")
    return products


def process_category(ecommerce_page, category_name):
    """Process a main category and all its subcategories.
    
    Args:
        ecommerce_page: EcommercePage instance
        category_name: Name of the category
        
    Returns:
        List of all products in the category and its subcategories
    """
    logger.info(f"Processing main category: {category_name}")
    all_products = []

    # First navigate to the main category
    navigation_success = ecommerce_page.navigate_to_category(category_name)
    if not navigation_success:
        logger.warning(f"Failed to navigate to category {category_name}, skipping")
        return []

    # Get products from the main category page
    main_category_products = process_products_page(ecommerce_page, category_name)
    all_products.extend(main_category_products)

    # Check for pagination in the main category
    pagination_products = process_pagination(ecommerce_page, category_name)
    all_products.extend(pagination_products)

    # Get subcategories for this category
    subcategories = ecommerce_page.get_subcategories(category_name)

    # Process each subcategory
    for subcategory_name in subcategories:
        # Navigate back to the main category first
        ecommerce_page.navigate_to_category(category_name)

        # Process the subcategory
        subcategory_products = process_subcategory(ecommerce_page, category_name, subcategory_name)
        all_products.extend(subcategory_products)

    logger.info(f"Total products in category {category_name} (including subcategories): {len(all_products)}")
    return all_products


def main():
    """Main entry point for the e-commerce scraper."""
    logger.info("E-commerce scraping started")

    # Initialize the WebDriver
    driver = setup_driver()
    if not driver:
        logger.error("Failed to initialize WebDriver, exiting")
        return

    # Initialize the e-commerce page
    ecommerce_page = EcommercePage(driver)

    # Create data handler
    data_handler = DataHandler()

    # Load the page
    page_load_success = ecommerce_page.load(BASE_URL)
    if not page_load_success:
        logger.error("Failed to load base page, exiting")
        driver.quit()
        return

    # Get the navigation structure
    logger.info("Analyzing site navigation structure")
    nav_structure = ecommerce_page.get_navigation_structure()

    # Initialize list to hold all product data
    all_products = []

    # Process each main category
    for category_name in nav_structure:
        # Process the category and its subcategories
        category_products = process_category(ecommerce_page, category_name)
        all_products.extend(category_products)

    # Process the product data
    processed_data = data_handler.process_product_data(all_products)

    # Save data to CSV if valid
    if processed_data:
        save_success = data_handler.save_to_csv(processed_data, OUTPUT_FILE)
        if save_success:
            logger.info(f"Successfully extracted and saved {len(processed_data)} total products")
        else:
            logger.warning("Failed to save product data to CSV")
    else:
        logger.warning("No valid product data to save")

    # Clean up
    driver.quit()
    logger.info("WebDriver closed")


if __name__ == "__main__":
    main()
