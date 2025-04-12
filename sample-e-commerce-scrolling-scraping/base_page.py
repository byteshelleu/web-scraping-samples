"""Base page class for web scraping projects."""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
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
        def _predicate(_):
            return self.driver.find_element(*locator)
            
        return self._wait_for(_predicate)
    
    def find_elements(self, locator):
        """Find multiple elements on the page.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        def _predicate(_):
            elements = self.driver.find_elements(*locator)
            if not elements:
                return False
            return elements
            
        return self._wait_for(_predicate)
    
    def find_elements_without_wait(self, locator):
        """Find multiple elements on the page without waiting.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        return self.driver.find_elements(*locator)
    
    def is_element_present(self, locator, wait_time=None):
        """Check if an element is present on the page.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            wait_time: Optional custom wait time
            
        Returns:
            True if element is present, False otherwise
        """
        wait_time = wait_time if wait_time is not None else self.timeout
        
        def _predicate(_):
            elements = self.driver.find_elements(*locator)
            return len(elements) > 0
        
        result = self._wait_for_no_exception(_predicate, wait_time=wait_time)
        return result is not None and result
    
    def wait_for_element_to_be_visible(self, locator, timeout=None):
        """Wait for an element to be visible.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            timeout: Optional custom timeout
            
        Returns:
            WebElement if element becomes visible, None otherwise
        """
        timeout = timeout if timeout is not None else self.timeout
        
        def _predicate(_):
            elements = self.driver.find_elements(*locator)
            if not elements:
                return False
            element = elements[0]
            if not element.is_displayed():
                return False
            return element
            
        return self._wait_for(_predicate, wait_time=timeout)
    
    def wait_for_element_to_disappear(self, locator, timeout=None):
        """Wait for an element to disappear from the page.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            timeout: Optional custom timeout
            
        Returns:
            True if element disappears, False otherwise
        """
        timeout = timeout if timeout is not None else self.timeout
        
        def _predicate(_):
            elements = self.driver.find_elements(*locator)
            if not elements:
                return True
            element = elements[0]
            if not element.is_displayed():
                return True
            return False
            
        return self._wait_for(_predicate, wait_time=timeout)
    
    def click_element(self, locator):
        """Click on an element.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            True if click is successful, False otherwise
        """
        element = self.find_element(locator)
        element.click()
        return True
    
    def get_text(self, locator):
        """Get text from an element.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            Text as string if element is found, empty string otherwise
        """
        element = self.find_element(locator)
        return element.text
        
    def get_attribute(self, locator, attribute):
        """Get attribute value from an element.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            attribute: Name of the attribute
            
        Returns:
            Attribute value as string if found, empty string otherwise
        """
        element = self.find_element(locator)
        return element.get_attribute(attribute) or ""
    
    def execute_script(self, script, *args):
        """Execute JavaScript on the page.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            Result of the JavaScript execution
        """
        return self.driver.execute_script(script, *args)
    
    def get_window_height(self):
        """Get the current window height.
        
        Returns:
            Window height as integer
        """
        return self.execute_script("return window.innerHeight")
    
    def get_document_height(self):
        """Get the current document height.
        
        Returns:
            Document height as integer
        """
        return self.execute_script("return document.body.scrollHeight")
    
    def get_scroll_position(self):
        """Get the current scroll position.
        
        Returns:
            Current scroll position as integer
        """
        return self.execute_script("return window.pageYOffset")
    
    def scroll_to_position(self, position):
        """Scroll to a specific position on the page.
        
        Args:
            position: Y-coordinate to scroll to
            
        Returns:
            New scroll position
        """
        self.execute_script(f"window.scrollTo(0, {position})")
        return self.get_scroll_position()
    
    def scroll_by_amount(self, amount):
        """Scroll the page by a specific amount.
        
        Args:
            amount: Amount to scroll by in pixels
            
        Returns:
            New scroll position
        """
        current_position = self.get_scroll_position()
        new_position = current_position + amount
        return self.scroll_to_position(new_position)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page.
        
        Returns:
            New scroll position at the bottom
        """
        return self.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    
    def scroll_into_view(self, element):
        """Scroll an element into view.
        
        Args:
            element: WebElement to scroll into view
            
        Returns:
            True if successful
        """
        self.execute_script("arguments[0].scrollIntoView(true)", element)
        return True
        
    def _wait_for(self, predicate, wait_time=None):
        """Custom wait function that waits for a predicate to return a truthy value.
        
        Args:
            predicate: Function that takes a driver parameter and returns a truthy value when condition is met
            wait_time: Optional custom wait time
            
        Returns:
            The value returned by the predicate when condition is met
            
        Raises:
            TimeoutException: If condition is not met within the wait time
        """
        wait_time = wait_time if wait_time is not None else self.timeout
        poll_frequency = 0.5
        max_attempts = int(wait_time / poll_frequency)
        last_exception_message = None
        
        for attempt in range(max_attempts):
            # Execute the predicate safely, catching common exceptions
            result = self._safely_execute_predicate(predicate, self.driver)
            
            # If we got a valid result, return it
            if result:
                return result
                
            # If there was an exception, note it for later reporting
            if hasattr(result, 'error_message'):
                last_exception_message = result.error_message
            
            # Wait before next attempt
            time.sleep(poll_frequency)
        
        # Condition not met within wait time
        if last_exception_message:
            raise TimeoutException(f"Timed out after {wait_time} seconds. Last exception: {last_exception_message}")
        raise TimeoutException(f"Timed out after {wait_time} seconds.")
    
    def _wait_for_no_exception(self, predicate, wait_time=None):
        """Custom wait function that returns None instead of raising TimeoutException.
        
        Args:
            predicate: Function that takes a driver parameter and returns a truthy value when condition is met
            wait_time: Optional custom wait time
            
        Returns:
            The value returned by the predicate when condition is met, or None if TimeoutException would occur
        """
        wait_time = wait_time if wait_time is not None else self.timeout
        poll_frequency = 0.5
        max_attempts = int(wait_time / poll_frequency)
        
        for attempt in range(max_attempts):
            result = self._safely_execute_predicate(predicate, self.driver)
            if result:
                return result
            
            # Wait before next attempt
            time.sleep(poll_frequency)
        
        # Condition not met within wait time
        return None
    
    def _safely_execute_predicate(self, predicate, driver):
        """Execute a predicate function safely handling common exceptions.
        
        Args:
            predicate: Function to execute
            driver: WebDriver instance to pass to the predicate
            
        Returns:
            Result of predicate execution or False if an exception occurred
        """
        # Check for NoSuchElementException
        elements_present = True
        if hasattr(driver, 'find_elements'):
            # If this is a standard NoSuchElementException scenario, 
            # we can detect it without letting the exception occur
            if isinstance(predicate, tuple) and len(predicate) == 2:
                elements = driver.find_elements(*predicate)
                elements_present = len(elements) > 0
                if not elements_present:
                    return False
        
        # Check for StaleElementReferenceException
        if not hasattr(driver, 'is_enabled') and hasattr(driver, 'find_element'):
            # If driver is actually a WebElement that might be stale
            if not self._element_is_valid(driver):
                return False
        
        # If we got past all the exception scenarios, execute the predicate
        if callable(predicate):
            return predicate(driver)
        
        return False
    
    def _element_is_valid(self, element):
        """Check if a WebElement is still valid (not stale).
        
        Args:
            element: WebElement to check
            
        Returns:
            True if element is valid, False otherwise
        """
        if not element:
            return False
            
        # A simple attribute access that shouldn't change element state
        # but will fail for stale elements
        valid = False
        if hasattr(element, 'is_enabled'):
            enabled = element.is_enabled()
            valid = True
            
        return valid
