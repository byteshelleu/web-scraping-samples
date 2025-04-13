"""Data handling module for the web scraper."""

import pandas as pd
import os
import re
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
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        
        # Return full path to the saved file
        full_path = os.path.abspath(filename)
        return full_path
    
    def to_dataframe(self, data):
        """Convert the data to a pandas DataFrame.
        
        Args:
            data: List of dictionaries to convert
            
        Returns:
            pandas DataFrame
        """
        if not data:
            return pd.DataFrame()
            
        return pd.DataFrame(data)
    
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
                
            # Check if dictionary has required keys
            if not item:
                logger.warning("Data contains an empty dictionary")
                
        logger.info(f"Data validation passed: {len(data)} valid items")
        return True
    
    def process_table_data(self, data):
        """Process the table data for analysis."""
        if not self.validate_data(data):
            logger.error("Unable to process data - validation failed")
            return None
            
        # Extract numeric values from price column
        for item in data:
            # Process Price column if it exists
            if 'Price' in item:
                # Extract numeric values using regex to handle various formats
                # This handles formats like $1,234.56, 1234.56, €1.234,56, etc.
                price_text = item['Price']
                if price_text is None:
                    item['Price_Value'] = 0.0
                    continue
                    
                # Remove currency symbols and spaces
                clean_price = price_text.replace('$', '').replace('€', '').replace('£', '').strip()
                
                # Extract numbers (allowing for different decimal/thousand separators)
                price_match = re.search(r'([\d,\.]+)', clean_price)
                if price_match:
                    # Get the matched price and prepare for conversion
                    price_str = price_match.group(1)
                    
                    # Handle US format ($1,234.56)
                    if ',' in price_str and '.' in price_str and price_str.index(',') < price_str.index('.'):
                        price_str = price_str.replace(',', '')
                    # Handle European format (€1.234,56)
                    elif ',' in price_str and '.' in price_str and price_str.index('.') < price_str.index(','):
                        price_str = price_str.replace('.', '').replace(',', '.')
                    # Handle simple comma as decimal (€1,99)
                    elif ',' in price_str and '.' not in price_str:
                        price_str = price_str.replace(',', '.')
                    
                    try:
                        item['Price_Value'] = float(price_str)
                    except ValueError:
                        logger.warning(f"Could not convert price '{price_text}' to float")
                        item['Price_Value'] = 0.0
                else:
                    logger.warning(f"No numeric value found in price: '{price_text}'")
                    item['Price_Value'] = 0.0
            
            # Process any other numeric columns as needed
            
        logger.info("Processed table data with enhanced price extraction")
        return data
        
    def get_price_statistics(self, data):
        """Calculate price statistics from the processed data."""
        if not data:
            logger.warning("No data for price statistics")
            return None
            
        # Process data if not already processed
        processed_data = self.process_table_data(data) if 'Price_Value' not in data[0] else data
        
        if not processed_data:
            return None
            
        # Extract price values
        price_values = [item.get('Price_Value', 0.0) for item in processed_data]
        
        # Calculate statistics
        stats = {
            'count': len(price_values),
            'min': min(price_values) if price_values else 0,
            'max': max(price_values) if price_values else 0,
            'avg': sum(price_values) / len(price_values) if price_values else 0,
            'total': sum(price_values)
        }
        
        logger.info(f"Calculated price statistics: {stats}")
        return stats
