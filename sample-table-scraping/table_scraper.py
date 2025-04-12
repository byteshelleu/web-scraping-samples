"""Main script that ties together all components of the table scraper."""

import os
import sys
import pandas
import json
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
    table_page = None
    data_handler = None
    
    # Initialize components with proper error checking
    table_page = TablePage(headless=HEADLESS_MODE)
    if not hasattr(table_page, 'driver') or table_page.driver is None:
        logger.error("Failed to initialize WebDriver")
        return
    
    # Create data handler
    data_handler = DataHandler()
    if not hasattr(data_handler, 'validate_data'):
        logger.error("Data handler missing required methods")
        return
    
    # Load the page
    if not hasattr(table_page, 'load'):
        logger.error("Table page missing load method")
        return
    
    load_result = table_page.load()
    if not load_result:
        logger.error("Failed to load table page")
        return
    
    # Check for the new comprehensive method
    if not hasattr(table_page, 'get_all_tables_data'):
        logger.error("Table page missing get_all_tables_data method")
        return
    
    # Extract data from all tables across all navigation links
    logger.info("Extracting data from all tables across all navigation links")
    all_pages_tables_data = table_page.get_all_tables_data()
    
    if not all_pages_tables_data:
        logger.warning("No data was extracted from any tables")
        # Close the browser before exiting
        if hasattr(table_page, 'close'):
            table_page.close()
        return
    
    # Process each page's data separately
    for page_name, table_data in all_pages_tables_data.items():
        logger.info(f"Processing data from page: {page_name}")
        
        # Check if we got valid data for this page
        if not table_data:
            logger.warning(f"No data was extracted from page: {page_name}")
            continue
        
        # Log the data extraction success
        logger.info(f"Successfully extracted {len(table_data)} total rows from page: {page_name}")
        
        # Process the data
        if not hasattr(data_handler, 'process_table_data'):
            logger.error("Data handler missing process_table_data method")
            continue
        
        processed_data = data_handler.process_table_data(table_data)
        if not processed_data:
            logger.error(f"Failed to process data from page: {page_name}")
            continue
        
        # Calculate price statistics using our enhanced method
        if hasattr(data_handler, 'get_price_statistics'):
            price_stats = data_handler.get_price_statistics(processed_data)
            if price_stats:
                logger.info(f"{page_name} price statistics: Min=${price_stats['min']:.2f}, "
                          f"Max=${price_stats['max']:.2f}, "
                          f"Average=${price_stats['avg']:.2f}, "
                          f"Total=${price_stats['total']:.2f}")
        
        # Save to CSV
        if hasattr(data_handler, 'save_to_csv'):
            # Create a safe filename from the page name
            safe_name = "".join([c if c.isalnum() else "_" for c in page_name])
            filename = f"scraped_{safe_name}_data.csv"
            csv_path = data_handler.save_to_csv(processed_data, filename=filename)
            if csv_path:
                logger.info(f"{page_name} data saved to {csv_path}")
            else:
                logger.error(f"Failed to save {page_name} data to CSV")
        else:
            logger.error("Data handler missing save_to_csv method")
    
    # Save a consolidated JSON with all data
    if all_pages_tables_data:
        # Create JSON path
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all_scraped_data.json")
        
        # Check if we can open the file for writing
        file_handle = None
        file_open_success = True
        
        # Try to open file but don't use try/except
        if os.path.exists(os.path.dirname(json_path)):
            # First check if directory exists
            try_file = open(json_path, 'w', encoding='utf-8')
            if try_file is not None:
                file_handle = try_file
            else:
                file_open_success = False
                logger.error("Failed to open JSON file for writing")
        else:
            file_open_success = False
            logger.error(f"Directory does not exist: {os.path.dirname(json_path)}")
        
        # If file is open, attempt to write to it
        if file_open_success and file_handle is not None:
            # Serialize data without using try/except
            # Check if data is JSON serializable first
            json_string = None
            serialization_success = True
            
            # Convert each key to string to ensure serializability
            serializable_data = {}
            for key, value in all_pages_tables_data.items():
                # Ensure key is string
                str_key = str(key) if key is not None else "None"
                # Only include non-None values
                if value is not None:
                    serializable_data[str_key] = value
            
            # Attempt to serialize with safe fallbacks
            json_string = json.dumps(serializable_data, indent=2)
            
            if json_string:
                # Write to file
                file_handle.write(json_string)
                file_handle.close()
                logger.info(f"All scraped data saved to {json_path}")
            else:
                logger.error("Failed to serialize data to JSON")
                if file_handle:
                    file_handle.close()
    
    # Close the browser
    if hasattr(table_page, 'close'):
        table_page.close()
    logger.info("Table scraping completed")

if __name__ == "__main__":
    # Run the main function
    main()
    
    # Give user a chance to see results
    print("\nPress Enter to exit...")
    input()
