"""Selenium behavior patterns for interacting with web elements."""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from logger import logger

class SeleniumBehavior:
    """Common interaction patterns for Selenium WebDriver."""
    
    def __init__(self, driver=None):
        """Initialize with a WebDriver instance."""
        self.driver = driver
    
    def set_driver(self, driver):
        """Set the WebDriver instance."""
        self.driver = driver
        return self
    
    def wait_for_page_load(self, timeout=5):
        """Wait for page to load completely."""
        time.sleep(timeout)
        return self
    
    def enter_text(self, locator, text, clear_first=True):
        """Enter text into an input field."""
        element = self.driver.find_element(*locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.info(f"Entered text '{text}' into {locator}")
        return element
    
    def enter_text_and_submit(self, locator, text, clear_first=True):
        """Enter text into an input field and press Enter to submit."""
        element = self.driver.find_element(*locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.info(f"Entered text '{text}' into {locator}")
        
        # Press Enter to submit
        element.send_keys(Keys.RETURN)
        logger.info("Pressed Enter key to submit")
        return element
    
    def click_element(self, locator):
        """Click on an element using standard click."""
        element = self.driver.find_element(*locator)
        element.click()
        logger.info(f"Clicked element {locator}")
        return element
    
    def js_click(self, locator):
        """Click on an element using JavaScript."""
        element = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].click();", element)
        logger.info(f"Clicked element {locator} using JavaScript")
        return element
    
    def get_element_attribute(self, locator, attribute):
        """Get an attribute value from an element."""
        element = self.driver.find_element(*locator)
        value = element.get_attribute(attribute)
        logger.info(f"Got attribute {attribute}={value} from {locator}")
        return value
    
    def multi_attempt_search(self, input_locator, button_locator, search_text):
        """Try multiple approaches to submit a search, staying on weather.gov."""
        # Clear and enter text first
        search_box = self.driver.find_element(*input_locator)
        search_box.clear()
        search_box.send_keys(search_text)
        logger.info(f"Entered search text: {search_text}")
        
        initial_url = self.driver.current_url
        
        # Attempt 1: Press Enter key
        logger.info("Attempt 1: Pressing Enter key")
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)
        if self.driver.current_url != initial_url and "search.usa.gov" not in self.driver.current_url:
            logger.info(f"URL changed from {initial_url} to {self.driver.current_url}")
            return self.driver.current_url
        
        # Go back if we navigated to search.usa.gov
        if "search.usa.gov" in self.driver.current_url:
            logger.warning("Redirected to search.usa.gov, navigating back")
            self.driver.back()
            time.sleep(2)
        
        # Attempt 2: Regular button click
        logger.info("Attempt 2: Regular button click")
        button = self.driver.find_element(*button_locator)
        button.click()
        time.sleep(2)
        if self.driver.current_url != initial_url and "search.usa.gov" not in self.driver.current_url:
            logger.info(f"URL changed from {initial_url} to {self.driver.current_url}")
            return self.driver.current_url
            
        # Go back if we navigated to search.usa.gov
        if "search.usa.gov" in self.driver.current_url:
            logger.warning("Redirected to search.usa.gov, navigating back")
            self.driver.back()
            time.sleep(2)
        
        # Attempt 3: JavaScript click
        logger.info("Attempt 3: JavaScript button click")
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(2)
        if self.driver.current_url != initial_url and "search.usa.gov" not in self.driver.current_url:
            logger.info(f"URL changed from {initial_url} to {self.driver.current_url}")
            return self.driver.current_url
        
        # If we haven't found a good URL, return the current one
        logger.warning(f"URL remained at {self.driver.current_url} or redirected to search.usa.gov")
        return self.driver.current_url
