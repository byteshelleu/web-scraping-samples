"""Data handler for processing and saving scraped product data."""

import csv
import os
import re
import pandas as pd
import logging


def extract_price_value(price_string):
    """Extract numeric price value from price string.

    Args:
        price_string: String containing the price

    Returns:
        Float price value
    """
    if not price_string:
        return 0.0

    # Remove currency symbols and other non-numeric characters
    numeric_chars = re.sub(r'[^0-9.]', '', price_string)

    # Handle case where no valid numeric characters are found
    if not numeric_chars:
        return 0.0

    return float(numeric_chars)


class DataHandler:
    """Handler for processing and saving scraped data."""

    def __init__(self):
        """Initialize the data handler."""
        self.logger = logging.getLogger(__name__)

    def validate_data(self, data):
        """Validate the scraped data.

        Args:
            data: List of dictionaries containing scraped product data

        Returns:
            List of valid products
        """
        if not data:
            self.logger.warning("No data to validate")
            return []

        if not isinstance(data, list):
            self.logger.warning("Data is not a list")
            return []

        valid_data = []
        for item in data:
            if not isinstance(item, dict):
                self.logger.warning("Data item is not a dictionary")
                continue

            # Check for minimum required fields
            if not item.get('title'):
                self.logger.warning("Product missing required title field")
                continue

            valid_data.append(item)

        self.logger.info(f"Data validation successful for {len(valid_data)} items")
        return valid_data

    def extract_review_count(self, rating_string):
        """Extract review count from rating string.
        
        Args:
            rating_string: String containing the rating info
            
        Returns:
            Integer review count
        """
        if not rating_string:
            return 0

        # Extract numbers from strings like "10 reviews"
        match = re.search(r'(\d+)\s*reviews?', rating_string)
        if match:
            return int(match.group(1))
        return 0

    def process_product_data(self, products):
        """Process the scraped product data.
        
        Args:
            products: List of dictionaries containing raw product data
            
        Returns:
            Processed product data
        """
        if not self.validate_data(products):
            self.logger.error("Data validation failed")
            return []

        processed_products = []

        for product in products:
            processed_product = product.copy()

            # Process price to extract numeric value
            if 'price' in processed_product:
                processed_product['price_value'] = extract_price_value(processed_product['price'])

            # Process rating to extract review count if not already present
            if 'rating' in processed_product and 'review_count' not in processed_product:
                processed_product['review_count'] = self.extract_review_count(processed_product['rating'])

            # Ensure all products have consistent fields
            for field in ['url', 'description', 'stars', 'review_count']:
                if field not in processed_product:
                    processed_product[field] = "" if field in ['url', 'description'] else 0

            processed_products.append(processed_product)

        self.logger.info(f"Processed {len(processed_products)} products")
        return processed_products

    def filter_products(self, products, min_price=None, max_price=None, min_stars=None):
        """Filter products based on criteria.
        
        Args:
            products: List of processed product dictionaries
            min_price: Minimum price value
            max_price: Maximum price value
            min_stars: Minimum star rating
            
        Returns:
            Filtered list of products
        """
        if not products:
            return []

        filtered_products = products.copy()

        # Apply price filters
        if min_price is not None:
            filtered_products = [p for p in filtered_products
                                 if 'price_value' in p and p['price_value'] >= min_price]

        if max_price is not None:
            filtered_products = [p for p in filtered_products
                                 if 'price_value' in p and p['price_value'] <= max_price]

        # Apply star rating filter
        if min_stars is not None:
            filtered_products = [p for p in filtered_products
                                 if 'stars' in p and p['stars'] >= min_stars]

        self.logger.info(f"Filtered from {len(products)} to {len(filtered_products)} products")
        return filtered_products

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
        self.logger.info(f"Processed {len(valid_products)} products")

        # Check for duplicates by creating a dataframe
        df = pd.DataFrame(valid_products)

        # Remove duplicates
        original_count = len(df)
        df = df.drop_duplicates()
        if len(df) < original_count:
            self.logger.info(f"Removed {original_count - len(df)} duplicate products")

        # Print category counts if available
        if 'category' in df.columns:
            category_counts = df['category'].value_counts().to_dict()
            self.logger.info("Products by category:")
            for category, count in category_counts.items():
                self.logger.info(f"  - {category}: {count} products")

        # Write to CSV
        df.to_csv(filename, index=False, quoting=csv.QUOTE_ALL)

        self.logger.info(f"Saved {len(df)} products to {filename}")
        return True

    def load_from_csv(self, filename):
        """Load product data from a CSV file.
        
        Args:
            filename: Name of the CSV file to load
            
        Returns:
            List of product dictionaries
        """
        if not os.path.exists(filename):
            self.logger.warning(f"File {filename} does not exist")
            return []

        # Check if file is readable
        if not os.access(filename, os.R_OK):
            self.logger.error(f"File {filename} is not readable")
            return []

        # Check if file is not empty
        if os.path.getsize(filename) == 0:
            self.logger.warning(f"File {filename} is empty")
            return []

        # Read CSV file
        df = pd.read_csv(filename)
        if df.empty:
            self.logger.warning(f"No data found in {filename}")
            return []

        products = df.to_dict('records')
        self.logger.info(f"Loaded {len(products)} products from {filename}")
        return products
