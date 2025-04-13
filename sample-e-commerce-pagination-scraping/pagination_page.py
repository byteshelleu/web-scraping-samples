"""Pagination page class for handling e-commerce sites with pagination."""

import time
from base_page import BasePage
from locators import PaginationEcommerceLocators
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class PaginationPage(BasePage):
    """Page object for handling e-commerce pages with pagination."""
    
    def __init__(self, driver, timeout=10):
        """Initialize the pagination page.
        
        Args:
            driver: Selenium WebDriver instance
            timeout: Maximum wait time for elements
        """
        super().__init__(driver, timeout)
        self.logger = logging.getLogger(__name__)
        self.seen_product_ids = set()
    
    def load(self, url):
        """Load the e-commerce website with pagination.
        
        Args:
            url: URL of the e-commerce website
            
        Returns:
            True if the page loaded successfully
        """
        self.logger.info(f"Loading e-commerce page with pagination: {url}")
        success = self.open_url(url)
        if success:
            self.logger.info("E-commerce page loaded successfully")
            return True
        return False
    
    def _get_product_identifier(self, product_element):
        """Generate a unique identifier for a product to detect duplicates.
        
        Args:
            product_element: WebElement representing a product
            
        Returns:
            String identifier for the product
        """
        title_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_TITLE)
        title = self.get_text(title_element)
        
        price_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_PRICE)
        price = self.get_text(price_element)
        
        description_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_DESCRIPTION)
        description = self.get_text(description_element)[:50] if description else ""  # First 50 chars for efficiency
        
        return f"{title}|{price}|{description}"
    
    def get_text(self, element):
        """Safely get text from an element with proper checks.
        
        Args:
            element: WebElement to extract text from
            
        Returns:
            Text content or empty string if element is None or has no text
        """
        if element is None or isinstance(element, bool):
            return ""
        
        if hasattr(element, 'text'):
            return element.text if element.text else ""
        
        return ""
    
    def get_attribute(self, element, attribute):
        """Safely get attribute from an element with proper checks.
        
        Args:
            element: WebElement to extract attribute from
            attribute: Name of the attribute to extract
            
        Returns:
            Attribute value or empty string if element is None or has no such attribute
        """
        if element is None or isinstance(element, bool):
            return ""
        
        if hasattr(element, 'get_attribute'):
            value = element.get_attribute(attribute)
            return value if value else ""
        
        return ""
    
    def is_loading_indicator_visible(self):
        """Check if loading indicator is visible.
        
        Returns:
            True if loading indicator is visible, False otherwise
        """
        indicators = self.find_elements_without_wait(PaginationEcommerceLocators.LOADING_INDICATOR)
        if not indicators:
            return False
            
        return any(indicator.is_displayed() for indicator in indicators)
    
    def get_document_height(self):
        """Get the current document height.
        
        Returns:
            Current document height as integer
        """
        return self.driver.execute_script("return document.body.scrollHeight")
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def _short_wait(self, seconds=0.5):
        """Short wait to allow page to process events.
        
        Args:
            seconds: Time to wait in seconds
        """
        WebDriverWait(self.driver, seconds).until(lambda d: True)
    
    def get_visible_products(self):
        """Get all visible product elements on the current page.
        
        Returns:
            List of WebElements representing products
        """
        return self.find_elements(PaginationEcommerceLocators.PRODUCT_CONTAINER)
    
    def extract_product_data(self, product_element):
        """Extract data from a product element.
        
        Args:
            product_element: WebElement representing a product
            
        Returns:
            Dictionary with product data or None if product was already seen
        """
        # Generate a unique identifier for the product
        product_id = self._get_product_identifier(product_element)
        
        # Skip if we've already seen this product
        if product_id in self.seen_product_ids:
            self.logger.debug(f"Skipping duplicate product: {product_id[:30]}...")
            return None
            
        # Add to seen products
        self.seen_product_ids.add(product_id)
        
        # Extract product information
        title_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_TITLE)
        title = self.get_text(title_element)
        
        price_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_PRICE)
        price = self.get_text(price_element)
        
        description_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_DESCRIPTION)
        description = self.get_text(description_element)
        
        # Extract rating information
        rating_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_RATING)
        
        # Get review count
        review_count_element = self._get_element_safely(product_element, PaginationEcommerceLocators.PRODUCT_REVIEW_COUNT)
        review_count_text = self.get_text(review_count_element)
        review_count = review_count_text.split()[0] if review_count_text else "0"
        
        # Get star rating by counting stars
        star_elements = []
        if rating_element:
            star_elements = self.find_nested_elements(rating_element, PaginationEcommerceLocators.PRODUCT_STARS[1])
        
        stars = len(star_elements) if star_elements else 0
        
        # Return a dictionary with product information
        return {
            "title": title,
            "price": price,
            "description": description,
            "stars": stars,
            "reviews": review_count
        }
    
    def is_pagination_present(self):
        """Check if pagination is present on the page.
        
        Returns:
            True if pagination is present, False otherwise
        """
        pagination = self.find_element_without_wait(PaginationEcommerceLocators.PAGINATION_CONTAINER)
        return pagination is not None and pagination.is_displayed()
    
    def has_next_page(self):
        """Check if there is a next page available.
        
        Returns:
            True if next page is available, False otherwise
        """
        # Check if the next button is disabled
        disabled_next = self.find_element_without_wait(PaginationEcommerceLocators.NEXT_PAGE_DISABLED)
        if disabled_next:
            return False
            
        # Check if there's an active next button
        next_button = self.find_element_without_wait(PaginationEcommerceLocators.PAGINATION_NEXT_BUTTON)
        return next_button is not None and next_button.is_displayed()
    
    def get_current_page_number(self):
        """Get the current page number.
        
        Returns:
            Current page number as integer, or 1 if not found
        """
        active_page = self.find_element_without_wait(PaginationEcommerceLocators.ACTIVE_PAGE)
        if active_page is None:
            return 1
            
        page_text = self.get_text(active_page)
        try:
            return int(page_text)
        except ValueError:
            return 1
    
    def go_to_next_page(self):
        """Navigate to the next page.
        
        Returns:
            True if successfully navigated to next page, False otherwise
        """
        if not self.has_next_page():
            self.logger.info("No next page available")
            return False
            
        current_page = self.get_current_page_number()
        next_button = self.find_element(PaginationEcommerceLocators.PAGINATION_NEXT_BUTTON)
        
        if next_button is None:
            self.logger.warning("Next button not found")
            return False
            
        # Click on the next button
        next_button.click()
        
        # Wait for the page to load and verify we're on the next page
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: self.get_current_page_number() > current_page
        )
        
        self.logger.info(f"Navigated to page {self.get_current_page_number()}")
        return True
    
    def extract_products_from_all_pages(self, max_pages=10):
        """Extract products from all pages up to max_pages.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of dictionaries containing product data
        """
        all_products = []
        current_page = 1
        
        while current_page <= max_pages:
            self.logger.info(f"Processing page {current_page}/{max_pages}")
            
            # Scroll to bottom of current page to ensure all products are loaded
            self.scroll_to_bottom()
            self._short_wait(1)  # Wait for any dynamic content to load
            
            # Extract products from current page
            visible_products = self.get_visible_products()
            self.logger.info(f"Found {len(visible_products)} products on page {current_page}")
            
            for product in visible_products:
                product_data = self.extract_product_data(product)
                if product_data:
                    all_products.append(product_data)
            
            # Check if there's a next page
            if not self.has_next_page():
                self.logger.info("Reached the last page")
                break
                
            # Go to next page
            if not self.go_to_next_page():
                self.logger.warning("Failed to navigate to next page")
                break
                
            current_page += 1
            self._short_wait(2)  # Wait for the new page to load
        
        self.logger.info(f"Extracted a total of {len(all_products)} unique products from {current_page} pages")
        return all_products
