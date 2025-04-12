"""Data handler for processing and saving scraped product data."""

import csv
import os
import re
import pandas as pd
import logging

class DataHandler:
    """Handler for processing and saving scraped data."""
    
    def __init__(self):
        """Initialize the data handler."""
        self.logger = logging.getLogger(__name__)
    
    def validate_data(self, data):
        """Validate the scraped data.
        
        Args:
            data: List of dictionaries containing product data
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data:
            self.logger.warning("No data to validate")
            return False
            
        valid_items = [item for item in data if 'title' in item and 'price' in item]
        self.logger.info(f"Data validation: {len(valid_items)} valid items out of {len(data)}")
        
        return len(valid_items) > 0
    
    def extract_price_value(self, price_str):
        """Extract numeric price value from a price string.
        
        Args:
            price_str: String containing price (e.g., "$1234.56")
            
        Returns:
            Float price value
        """
        if not price_str:
            return 0.0
            
        # Remove currency symbol and other non-numeric characters
        # Keep only digits, decimal point and negative sign
        price_numeric = re.sub(r'[^\d.-]', '', price_str)
        
        # Return 0.0 if no valid digits remain
        if not price_numeric or not any(c.isdigit() for c in price_numeric):
            self.logger.warning(f"Could not extract valid price from: {price_str}")
            return 0.0
        
        # Additional validation to ensure it's a valid float format
        if price_numeric.count('.') > 1:
            self.logger.warning(f"Invalid price format (multiple decimals): {price_str}")
            return 0.0
            
        return float(price_numeric) if price_numeric else 0.0
    
    def process_product_data(self, products):
        """Process the scraped product data.
        
        Args:
            products: List of dictionaries containing product data
            
        Returns:
            Processed data or None if validation fails
        """
        if not self.validate_data(products):
            return None
        
        for product in products:
            # Extract price value
            if 'price' in product:
                product['price_value'] = self.extract_price_value(product['price'])
                
            # Extract review count
            if 'rating' in product and 'review_count' not in product:
                # Try to extract review count from rating string
                match = re.search(r'(\d+)\s*reviews?', product.get('rating', ''))
                if match:
                    product['review_count'] = match.group(1)
        
        self.logger.info(f"Processed data for {len(products)} products")
        return products
    
    def save_to_csv(self, data, filename):
        """Save the processed data to a CSV file.
        
        Args:
            data: List of dictionaries containing product data
            filename: Name of the output CSV file
            
        Returns:
            True if save was successful, False otherwise
        """
        if not data:
            self.logger.warning("No data to save")
            return False
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        self.logger.info(f"Created DataFrame with {df.shape[0]} rows and {df.shape[1]} columns")
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        self.logger.info(f"Data saved to {filename}")
        
        # Get absolute path for better logging
        abs_path = os.path.abspath(filename)
        self.logger.info(f"Data saved to {abs_path}")
        
        return True
