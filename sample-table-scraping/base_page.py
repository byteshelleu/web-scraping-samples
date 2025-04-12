"""Base page object for common Selenium functionality."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import WEBDRIVER_TIMEOUT
from logger import logger
import time
from selenium.webdriver.common.by import By


class BasePage:
    """Base class for all page objects providing common functionality."""
    
    def __init__(self, driver=None, headless=False):
        """Initialize the WebDriver with optional headless mode.
        
        Args:
            driver: An existing WebDriver instance, or None to create a new one
            headless: Whether to run the browser in headless mode
        """
        if driver:
            self.driver = driver
        else:
            # Set up Chrome options
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            # Create Service object with the ChromeDriverManager
            driver_service = Service()
            
            # Set up the Chrome driver with the specified options
            self.driver = webdriver.Chrome(
                service=driver_service,
                options=chrome_options
            )
            
            logger.info("WebDriver initialized")
    
    def navigate_to(self, url):
        """Navigate to a specific URL.
        
        Args:
            url: The URL to navigate to
        """
        logger.info(f"Navigating to {url}")
        self.driver.get(url)
    
    def find_element(self, locator):
        """Find a single element on the page using polling-based approach.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
            
        Returns:
            The WebElement if found, None otherwise
        """
        # Custom polling implementation without exceptions
        start_time = time.time()
        
        # Poll until timeout
        while time.time() - start_time < WEBDRIVER_TIMEOUT:
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
        logger.warning(f"Element not found with locator: {locator}")
        return None
    
    def find_elements(self, locator):
        """Find multiple elements on the page using polling-based approach.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the elements
            
        Returns:
            A list of WebElements if found, or an empty list
        """
        # Custom polling implementation without exceptions
        start_time = time.time()
        valid_elements = []
        
        # Poll until timeout
        while time.time() - start_time < WEBDRIVER_TIMEOUT:
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
            logger.warning(f"No valid elements found with locator: {locator}")
        
        return valid_elements
    
    def click(self, locator):
        """Click on an element with null safety and attribute checking.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
            
        Returns:
            True if click is successful, False otherwise
        """
        element = self.find_element(locator)
        
        # Check if element is valid and has click method
        if element is None or isinstance(element, bool) or not hasattr(element, 'click'):
            logger.warning(f"Cannot click invalid element with locator: {locator}")
            return False
        
        # Check if element is displayed
        if hasattr(element, 'is_displayed') and not element.is_displayed():
            logger.warning(f"Cannot click non-visible element with locator: {locator}")
            return False
            
        # Perform the click
        element.click()
        return True
    
    def get_attribute(self, locator, attribute):
        """Get an attribute value from an element with null safety.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
            attribute: The attribute name to get
            
        Returns:
            The attribute value, or empty string if not found
        """
        element = self.find_element(locator)
        
        # Check if element is valid and has get_attribute method
        if element is None or isinstance(element, bool) or not hasattr(element, 'get_attribute'):
            return ""
            
        result = element.get_attribute(attribute)
        return result if result is not None else ""
    
    def close(self):
        """Close the browser with null safety."""
        logger.info("Closing WebDriver")
        if hasattr(self, 'driver') and self.driver:
            if hasattr(self.driver, 'quit'):
                self.driver.quit()
