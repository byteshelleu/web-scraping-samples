"""Base page object for common Selenium functionality."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import WEBDRIVER_TIMEOUT
from logger import logger

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
        """Find a single element on the page.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
            
        Returns:
            The WebElement if found
        """
        return self.driver.find_element(*locator)
    
    def find_elements(self, locator):
        """Find multiple elements on the page.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the elements
            
        Returns:
            A list of WebElements if found, or an empty list
        """
        return self.driver.find_elements(*locator)
    
    def wait_for_element(self, locator, timeout=WEBDRIVER_TIMEOUT):
        """Wait for an element to be present and visible.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
            timeout: Maximum time to wait in seconds
            
        Returns:
            The WebElement once it is present and visible
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    
    def click(self, locator):
        """Click on an element.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
        """
        self.find_element(locator).click()
    
    def type_text(self, locator, text):
        """Type text into an input field.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
            text: The text to type
        """
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator):
        """Get text from an element.
        
        Args:
            locator: A tuple of (By.X, "value") defining how to locate the element
            
        Returns:
            The text of the element
        """
        return self.find_element(locator).text
    
    def close(self):
        """Close the browser."""
        logger.info("Closing WebDriver")
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
