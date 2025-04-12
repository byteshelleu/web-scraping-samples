"""Base page class for web scraping projects."""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

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
        self.wait = WebDriverWait(self.driver, self.timeout)
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
        try:
            element = self.wait.until(
                EC.presence_of_element_located(locator)
            )
            return element
        except (TimeoutException, NoSuchElementException):
            self.logger.warning(f"Element not found with locator: {locator}")
            return None
    
    def find_elements(self, locator):
        """Find multiple elements on the page.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        try:
            elements = self.wait.until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except (TimeoutException, NoSuchElementException):
            self.logger.warning(f"Elements not found with locator: {locator}")
            return []
    
    def is_element_present(self, locator):
        """Check if an element is present on the page.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            True if element is present, False otherwise
        """
        try:
            self.wait.until(
                EC.presence_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False
    
    def click_element(self, locator):
        """Click on an element.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            True if click is successful, False otherwise
        """
        element = self.find_element(locator)
        if element:
            try:
                element.click()
                return True
            except Exception as e:
                self.logger.warning(f"Failed to click element {locator}: {e}")
                return False
        return False
    
    def get_text(self, locator):
        """Get text from an element.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            Text as string if element is found, empty string otherwise
        """
        element = self.find_element(locator)
        if element:
            return element.text
        return ""
        
    def get_attribute(self, locator, attribute):
        """Get attribute value from an element.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            attribute: Name of the attribute
            
        Returns:
            Attribute value as string if found, empty string otherwise
        """
        element = self.find_element(locator)
        if element:
            return element.get_attribute(attribute) or ""
        return ""
