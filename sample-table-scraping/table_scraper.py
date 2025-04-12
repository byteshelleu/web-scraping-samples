"""Main script that ties together all components of the table scraper."""

import os
import sys
import pandas
from selenium import webdriver

# Add absolute imports to ensure script runs locally
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from table_page import TablePage
from data_handler import DataHandler
from config import HEADLESS_MODE
from logger import logger

def main():
    """Main entry point for the table scraper application."""
    logger.info("Table scraping started")
    
    # Initialize the table page
    table_page = TablePage(headless=HEADLESS_MODE)
    
    # Create data handler
    data_handler = DataHandler()
    
    # Load the page and get table data
    table_page.load()
    
    # Check if pagination exists
    total_pages = table_page.check_pagination()
    
    # Initialize list to hold all table data
    all_table_data = []
    
    # Scrape data from all pages
    for page in range(1, total_pages + 1):
        if page > 1:
            # Navigate to next page if not on first page
            logger.info(f"Navigating to page {page}")
            table_page.navigate_to_page(page)
        
        # Get table data from current page
        page_data = table_page.get_table_data()
        
        if page_data:
            logger.info(f"Extracted {len(page_data)} rows from page {page}")
            all_table_data.extend(page_data)
        else:
            logger.warning(f"No data found on page {page}")
    
    # Process the data
    processed_data = data_handler.process_table_data(all_table_data)
    
    # Save to CSV if data was successfully processed
    if processed_data:
        logger.info(f"Successfully extracted {len(processed_data)} total rows")
        
        # Display summary of the data
        if 'Price' in processed_data[0]:
            # Calculate average price if price column exists
            prices = [float(item.get('Price_Value', 0)) for item in processed_data]
            avg_price = sum(prices) / len(prices) if prices else 0
            logger.info(f"Average price: ${avg_price:.2f}")
        
        # Save to CSV
        csv_path = data_handler.save_to_csv(processed_data)
        logger.info(f"Data saved to {csv_path}")
    else:
        logger.error("Unable to process data - no valid data found")
    
    # Close the browser
    table_page.close()
    logger.info("Table scraping completed")

if __name__ == "__main__":
    # Run the main function
    main()
    
    # Give user a chance to see results
    print("\nPress Enter to exit...")
    input()
