"""Main script that ties together all components of the table scraper."""

import os
import sys
from table_page import TablePage
from data_handler import DataHandler
from config import HEADLESS_MODE
from logger import logger

# Add absolute imports to ensure script runs locally
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main entry point for the table scraper application."""
    logger.info("Table scraping started")

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

    # Extract data from all tables across navigation links
    logger.info("Extracting data from all tables across all navigation links")
    all_pages_data = table_page.get_all_tables_data()

    # Process each page's data
    all_processed_data = {}
    combined_data = []

    for page_name, page_data in all_pages_data.items():
        logger.info(f"Processing data from page: {page_name}")
        if not page_data:
            logger.warning(f"No data found for page: {page_name}")
            continue

        # Process data
        if hasattr(data_handler, 'process_table_data'):
            processed_data = data_handler.process_table_data(page_data)

            # Validate the processed data - just use the return value directly
            if hasattr(data_handler, 'validate_data'):
                is_valid = data_handler.validate_data(processed_data)
                if is_valid:
                    # We'll get the count directly from the data
                    count = len(processed_data) if processed_data else 0
                    logger.info(f"Data validation passed: {count} valid items")
                else:
                    logger.warning(f"Data validation failed for page: {page_name}")

            # Process price data
            if hasattr(data_handler, 'extract_prices'):
                processed_data = data_handler.extract_prices(processed_data)

                is_valid = data_handler.validate_data(processed_data)
                if is_valid:
                    count = len(processed_data) if processed_data else 0
                    logger.info(f"Data validation passed: {count} valid items")
                else:
                    logger.warning(f"Data validation failed after price extraction for page: {page_name}")

            # Calculate price statistics
            if hasattr(data_handler, 'calculate_price_statistics'):
                price_stats = data_handler.calculate_price_statistics(processed_data)
                logger.info(f"Calculated price statistics: {price_stats}")

                min_price = price_stats.get('min', 0)
                max_price = price_stats.get('max', 0)
                avg_price = price_stats.get('avg', 0)
                total_price = price_stats.get('total', 0)

                logger.info(
                    f"{page_name} price statistics: Min=${min_price:.2f}, Max=${max_price:.2f}, "
                    f"Average=${avg_price:.2f}, Total=${total_price:.2f}")

            # Add a source column to identify which page the data came from
            for item in processed_data:
                if item is not None and isinstance(item, dict):
                    item['source_page'] = page_name

            all_processed_data[page_name] = processed_data
            combined_data.extend(processed_data)
        else:
            logger.warning("DataHandler missing process_table_data method")

    # Create a single CSV file with all data
    if combined_data:
        # Single output file for all data
        csv_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_table_data.csv")
        if hasattr(data_handler, 'to_dataframe'):
            combined_df = data_handler.to_dataframe(combined_data)
            # Safe CSV writing without try/except
            if os.path.exists(os.path.dirname(csv_output_path)):
                combined_df.to_csv(csv_output_path, index=False)
                logger.info(f"All scraped data saved to {csv_output_path} ({len(combined_df)} rows)")
            else:
                logger.error(f"Output directory does not exist: {os.path.dirname(csv_output_path)}")
        else:
            logger.warning("DataHandler missing to_dataframe method, skipping CSV export")
    else:
        logger.warning("No data collected, skipping CSV export")

    # Clean up
    if hasattr(table_page, 'driver') and table_page.driver:
        logger.info("Closing WebDriver")
        table_page.driver.quit()

    logger.info("Table scraping completed")

    # Pause before exiting
    input("Press Enter to exit...")

    return


if __name__ == "__main__":
    # Run the main function
    main()

    # Handle any final cleanup
    # All proper cleanup is handled inside the main function
    pass
