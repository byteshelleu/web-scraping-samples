"""Scrolling page class for handling infinite scrolling e-commerce sites."""

import time
from base_page import BasePage
from locators import ScrollingEcommerceLocators
from selenium.webdriver.common.by import By
import logging

class ScrollingPage(BasePage):
    """Page object for handling infinite scrolling e-commerce pages."""
    
    def __init__(self, driver, timeout=10):
        """Initialize the scrolling page.
        
        Args:
            driver: Selenium WebDriver instance
            timeout: Maximum wait time for elements
        """
        super().__init__(driver, timeout)
        self.logger = logging.getLogger(__name__)
        self.seen_product_ids = set()
    
    def load(self, url):
        """Load the scrolling e-commerce website.
        
        Args:
            url: URL of the e-commerce website
            
        Returns:
            True if the page loaded successfully
        """
        self.logger.info(f"Loading scrolling e-commerce page: {url}")
        success = self.open_url(url)
        if success:
            self.logger.info("Scrolling e-commerce page loaded successfully")
            return True
        return False
    
    def _get_product_identifier(self, product_element):
        """Generate a unique identifier for a product to detect duplicates.
        
        Args:
            product_element: WebElement representing a product
            
        Returns:
            String identifier for the product
        """
        title_element = self._get_element_safely(product_element, ScrollingEcommerceLocators.PRODUCT_TITLE)
        title = title_element.text if title_element else ""
        
        price_element = self._get_element_safely(product_element, ScrollingEcommerceLocators.PRODUCT_PRICE)
        price = price_element.text if price_element else ""
        
        description_element = self._get_element_safely(product_element, ScrollingEcommerceLocators.PRODUCT_DESCRIPTION)
        description = description_element.text[:50] if description_element else ""  # First 50 chars for efficiency
        
        return f"{title}|{price}|{description}"
    
    def is_loading_indicator_visible(self):
        """Check if loading indicator is visible.
        
        Returns:
            True if loading indicator is visible, False otherwise
        """
        indicators = self.find_elements_without_wait(ScrollingEcommerceLocators.LOADING_INDICATOR)
        if not indicators:
            return False
            
        return any(indicator.is_displayed() for indicator in indicators)
    
    def is_end_of_content_reached(self, previous_height, current_height, previous_product_count, current_product_count):
        """Determine if we've reached the end of content.
        
        Args:
            previous_height: Document height before scrolling
            current_height: Document height after scrolling
            previous_product_count: Number of products before scrolling
            current_product_count: Number of products after scrolling
            
        Returns:
            True if end of content is reached, False otherwise
        """
        # Check if document height hasn't changed
        height_unchanged = previous_height == current_height
        
        # Check if no new products were loaded
        no_new_products = previous_product_count == current_product_count
        
        # Check for end-of-content message (may not be present on all sites)
        end_messages = self.find_elements_without_wait(ScrollingEcommerceLocators.END_OF_CONTENT_MESSAGE)
        end_message_visible = any(msg.is_displayed() for msg in end_messages) if end_messages else False
        
        # Check for no-more-products message (may not be present on all sites)
        no_more_indicators = self.find_elements_without_wait(ScrollingEcommerceLocators.NO_MORE_PRODUCTS_INDICATOR)
        no_more_indicator_visible = any(ind.is_displayed() for ind in no_more_indicators) if no_more_indicators else False
        
        return height_unchanged or no_new_products or end_message_visible or no_more_indicator_visible
    
    def scroll_and_extract_products(self, max_scrolls=20, scroll_pause_time=1.5):
        """Scroll through the page and extract all products.
        
        Args:
            max_scrolls: Maximum number of scrolls to perform
            scroll_pause_time: Time to pause between scrolls
            
        Returns:
            List of dictionaries containing product data
        """
        self.logger.info("Starting scroll and extract process")
        all_products = []
        scroll_count = 0
        
        # Get initial products
        visible_products = self.get_visible_products()
        all_products.extend(visible_products)
        previous_product_count = len(visible_products)
        
        # Get initial document height
        previous_height = self.get_document_height()
        
        # Continue scrolling while we have more content and haven't exceeded max_scrolls
        while scroll_count < max_scrolls:
            self.logger.info(f"Scroll {scroll_count + 1}/{max_scrolls}")
            
            # Scroll down to the bottom of the currently loaded content
            self.scroll_to_bottom()
            
            # Wait for the page to load more content
            time.sleep(scroll_pause_time)
            
            # Wait for any loading indicator to disappear
            if self.is_loading_indicator_visible():
                self.logger.info("Waiting for loading indicator to disappear")
                # Give it a bit more time to disappear completely
                time.sleep(scroll_pause_time)
            
            # Get new document height
            current_height = self.get_document_height()
            
            # Get newly loaded products
            current_products = self.get_visible_products()
            current_product_count = len(current_products)
            
            # Check if we've reached the end of content
            if self.is_end_of_content_reached(previous_height, current_height, 
                                             previous_product_count, current_product_count):
                self.logger.info("Reached end of content")
                break
            
            # Extract only the newly loaded products (avoid duplicates)
            newly_loaded_products = []
            for product in current_products:
                product_id = self._get_product_identifier(product)
                if product_id not in self.seen_product_ids:
                    self.seen_product_ids.add(product_id)
                    data = self.extract_product_data(product)
                    if data:
                        newly_loaded_products.append(data)
            
            self.logger.info(f"Extracted {len(newly_loaded_products)} new products in this scroll")
            all_products.extend(newly_loaded_products)
            
            # Update for next iteration
            previous_height = current_height
            previous_product_count = current_product_count
            scroll_count += 1
        
        self.logger.info(f"Total scrolls: {scroll_count}, Total products extracted: {len(all_products)}")
        return all_products
    
    def get_visible_products(self):
        """Get all currently visible product elements on the page.
        
        Returns:
            List of product WebElements
        """
        products = self.find_elements_without_wait(ScrollingEcommerceLocators.PRODUCT_CONTAINER)
        
        # Track the IDs of seen products
        for product in products:
            product_id = self._get_product_identifier(product)
            self.seen_product_ids.add(product_id)
            
        return products
    
    def _get_element_safely(self, parent, locator):
        """Safely get an element without raising exceptions.
        
        Args:
            parent: Parent WebElement to search within
            locator: Locator tuple (By.XX, "selector")
            
        Returns:
            WebElement if found, None otherwise
        """
        if not parent:
            return None
            
        if hasattr(parent, 'find_element'):
            elements = parent.find_elements(*locator)
            if elements:
                return elements[0]
        return None
    
    def _get_elements_safely(self, parent, locator):
        """Safely get elements without raising exceptions.
        
        Args:
            parent: Parent WebElement to search within
            locator: Locator tuple (By.XX, "selector")
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        if not parent:
            return []
            
        if hasattr(parent, 'find_elements'):
            return parent.find_elements(*locator)
        return []
    
    def extract_product_data(self, product_element):
        """Extract data from a product element.
        
        Args:
            product_element: WebElement representing a product
            
        Returns:
            Dictionary containing product data
        """
        if not product_element:
            return {}
            
        product_data = {}
        
        # Extract title
        title_element = self._get_element_safely(product_element, ScrollingEcommerceLocators.PRODUCT_TITLE)
        product_data['title'] = title_element.text.strip() if title_element else ""
        
        # Extract price
        price_element = self._get_element_safely(product_element, ScrollingEcommerceLocators.PRODUCT_PRICE)
        product_data['price'] = price_element.text.strip() if price_element else ""
        
        # Extract description
        description_element = self._get_element_safely(product_element, ScrollingEcommerceLocators.PRODUCT_DESCRIPTION)
        product_data['description'] = description_element.text.strip() if description_element else ""
        
        # Extract rating information
        rating_elements = self._get_elements_safely(product_element, ScrollingEcommerceLocators.PRODUCT_RATING)
        if rating_elements:
            product_data['rating'] = rating_elements[0].text.strip()
            
            # Extract number of reviews
            review_count_elements = self._get_elements_safely(product_element, ScrollingEcommerceLocators.PRODUCT_REVIEW_COUNT)
            if review_count_elements:
                product_data['review_count'] = review_count_elements[0].text.strip()
            
            # Extract star rating
            star_elements = self._get_elements_safely(product_element, ScrollingEcommerceLocators.PRODUCT_STARS)
            product_data['stars'] = len(star_elements)
        
        # Get product URL
        if title_element:
            link_element = title_element if title_element.tag_name == 'a' else None
            if not link_element and hasattr(title_element, 'find_element'):
                # Try to find an anchor tag within the title element
                links = self._get_elements_safely(title_element, (By.TAG_NAME, "a"))
                link_element = links[0] if links else None
                
            if link_element:
                product_data['url'] = link_element.get_attribute('href')
        
        self.logger.info(f"Extracted data for product: {product_data.get('title', 'Unknown')}")
        return product_data
