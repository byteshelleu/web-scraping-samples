"""Data handling module for the web scraper."""

import pandas as pd
import os
from config import DEFAULT_OUTPUT_FILE
from logger import logger

class DataHandler:
    """Handler for processing and saving scraped data."""
    
    def save_to_csv(self, data, filename=DEFAULT_OUTPUT_FILE):
        """Save the scraped data to a CSV file."""
        if not data:
            logger.warning("No data to save")
            return False
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
        # Save to CSV
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        
        # Return full path to the saved file
        full_path = os.path.abspath(filename)
        return full_path
    
    def validate_data(self, data):
        """Validate the scraped data."""
        if not data:
            logger.warning("Empty data received")
            return False
            
        # Check if data is a list
        if not isinstance(data, list):
            logger.error("Data is not a list")
            return False
            
        # Check if each item in the list is a dictionary
        for item in data:
            if not isinstance(item, dict):
                logger.error("Data contains non-dictionary items")
                return False
                
        logger.info(f"Data validation passed: {len(data)} valid items")
        return True
    
    def process_table_data(self, data):
        """Process the table data for analysis."""
        if not self.validate_data(data):
            logger.error("Unable to process data - validation failed")
            return None
            
        # Extract numeric values from price column
        for item in data:
            if 'Price' in item:
                item['Price_Value'] = 0.0 if not item['Price'].replace('$', '').replace(',', '').isdigit() else float(item['Price'].replace('$', '').replace(',', ''))
                    
        logger.info("Processed table data with price extraction")
        return data
