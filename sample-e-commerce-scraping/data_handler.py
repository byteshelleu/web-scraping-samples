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
            List of validated products
        """
        if not data:
            self.logger.warning("No data to validate")
            return []

        valid_items = []
        for item in data:
            if isinstance(item, dict) and 'title' in item and 'price' in item:
                valid_items.append(item)
            else:
                self.logger.warning("Invalid product data found - missing required fields")

        self.logger.info(f"Data validation: {len(valid_items)} valid items out of {len(data)}")

        return valid_items

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

    def save_to_csv(self, products, filename='scraped_products.csv'):
        """Save the product data to a CSV file.

        Args:
            products: List of product dictionaries
            filename: Name of the output CSV file

        Returns:
            Boolean indicating if save was successful
        """
        if not products:
            self.logger.warning("No data to save")
            return False

        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        # Validate product data and get valid products
        valid_products = self.validate_data(products)
        if not valid_products:
            self.logger.warning("No valid products to save")
            return False

        # Convert to DataFrame for easier handling
        df = pd.DataFrame(valid_products)

        # Check for and remove duplicates
        original_count = len(df)
        df = df.drop_duplicates()
        if len(df) < original_count:
            self.logger.info(f"Removed {original_count - len(df)} duplicate products")

        # Log category counts if available
        if 'category' in df.columns:
            category_counts = df['category'].value_counts().to_dict()
            self.logger.info("Products by category:")
            for category, count in category_counts.items():
                self.logger.info(f"  - {category}: {count} products")

        # Write to CSV
        df.to_csv(filename, index=False, quoting=csv.QUOTE_ALL)

        self.logger.info(f"Saved {len(df)} products to {filename}")
        return True
