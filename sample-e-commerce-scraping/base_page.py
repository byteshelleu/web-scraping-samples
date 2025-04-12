"""Base page class for web scraping projects."""

from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time


class BasePage:
    """Base class for all page objects."""

    def __init__(self, driver, timeout=10):
        """Initialize the base page.
        
        Args:
            driver: Selenium WebDriver instance
            timeout: Maximum wait time for elements
        """
        self.driver = driver
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def open_url(self, url):
        """Navigate to the specified URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if navigation is successful, False otherwise
        """
        self.logger.info(f"Navigating to {url}")
        self.driver.get(url)
        return True

    def find_element(self, locator):
        """Find a single element on the page.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            WebElement if found, None otherwise
        """
        # Custom polling implementation without exceptions
        start_time = time.time()
        
        # Poll until timeout
        while time.time() - start_time < self.timeout:
            # Direct element access
            elements = self.driver.find_elements(*locator)
            
            # Check if we found any elements
            if elements:
                element = elements[0]
                
                # Check if the element is a proper WebElement (not a boolean)
                if not isinstance(element, bool) and hasattr(element, 'is_displayed'):
                    return element  # Success - valid element found
            
            # Small sleep to avoid hammering the CPU
            time.sleep(0.5)
        
        # If we get here, we've timed out
        self.logger.warning(f"Element not found with locator: {locator}")
        return None

    def find_elements(self, locator):
        """Find multiple elements on the page.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        # Custom polling implementation without exceptions
        start_time = time.time()
        valid_elements = []
        
        # Poll until timeout
        while time.time() - start_time < self.timeout:
            # Direct elements access
            all_elements = self.driver.find_elements(*locator)
            
            # Filter out boolean values and invalid elements
            valid_elements = [e for e in all_elements if not isinstance(e, bool) and hasattr(e, 'is_displayed')]
            
            # If we found valid elements, return them
            if valid_elements:
                return valid_elements
            
            # Small sleep to avoid hammering the CPU
            time.sleep(0.5)
        
        # If we get here, we've timed out
        if not valid_elements:
            self.logger.warning(f"No valid elements found with locator: {locator}")
        
        return valid_elements
