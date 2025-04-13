"""Scrolling page class for handling infinite scrolling e-commerce sites."""

import time
from base_page import BasePage
from locators import ScrollingEcommerceLocators
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


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
        # Check if document height hasn't changed AND no new products were loaded
        # Both conditions must be true to consider we've reached the end
        height_unchanged = previous_height == current_height
        no_new_products = previous_product_count == current_product_count
        
        # Check for end-of-content message (may not be present on all sites)
        end_messages = self.find_elements_without_wait(ScrollingEcommerceLocators.END_OF_CONTENT_MESSAGE)
        end_message_visible = any(msg.is_displayed() for msg in end_messages) if end_messages else False
        
        # Check for no-more-products message (may not be present on all sites)
        no_more_indicators = self.find_elements_without_wait(ScrollingEcommerceLocators.NO_MORE_PRODUCTS_INDICATOR)
        no_more_indicator_visible = any(ind.is_displayed() for ind in no_more_indicators) if no_more_indicators \
            else False
        
        # We need BOTH unchanged height AND no new products to conclude we're at the end
        # OR explicit end indicators
        return (height_unchanged and no_new_products) or end_message_visible or no_more_indicator_visible
    
    def get_document_height(self):
        """Get the current document height.
        
        Returns:
            Current document height as integer
        """
        return self.driver.execute_script("return document.body.scrollHeight")
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
    def smooth_scroll_to_bottom(self):
        """Scroll to the bottom with intermediate steps to ensure content triggers properly."""
        
        # First do a complete scroll to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Then do some smaller scrolls at different positions to trigger lazy loading
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
        WebDriverWait(self.driver, 0.2).until(lambda d: True)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
        WebDriverWait(self.driver, 0.2).until(lambda d: True)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.9);")
        WebDriverWait(self.driver, 0.2).until(lambda d: True)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def wait_for_page_height_change(self, previous_height, timeout=None):
        """Wait for the page height to change after scrolling.
        
        Args:
            previous_height: Height before scrolling
            timeout: Optional custom timeout
            
        Returns:
            New document height if changed, or previous_height if timed out
        """
        timeout = timeout if timeout is not None else self.timeout

        def height_changed():
            current_height = self.get_document_height()
            if current_height > previous_height:
                return current_height
            return False
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            result = height_changed()
            if result:
                return result
            WebDriverWait(self.driver, 0.2).until(lambda d: True)

        return previous_height
    
    def wait_for_loading_indicator_to_disappear(self, timeout=None):
        """Wait for the loading indicator to disappear.
        
        Args:
            timeout: Optional custom timeout
            
        Returns:
            True if loading indicator disappeared, False if timed out
        """
        timeout = timeout if timeout is not None else self.timeout
        
        if not self.is_loading_indicator_visible():
            return True
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            if not self.is_loading_indicator_visible():
                return True
            WebDriverWait(self.driver, 0.2).until(lambda d: True)
            
        self.logger.warning("Loading indicator did not disappear within timeout")
        return False

    def scroll_and_extract_products(self, max_scrolls=50, scroll_pause_time=2.5):
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
        consecutive_no_new_products = 0
        max_consecutive_no_new = 5  # Increased for more persistence

        # Get initial product count and extract their data
        visible_products = self.get_visible_products()
        initial_count = len(visible_products)
        self.logger.info(f"Initial product count: {initial_count}")

        # Extract initial products
        for product in visible_products:
            product_data = self.extract_product_data(product)
            if product_data:
                all_products.append(product_data)

        # Keep track of the number of products we've already seen
        prev_product_count = initial_count

        # Simple scroll loop: scroll to bottom, wait, extract new products, repeat
        while scroll_count < max_scrolls and consecutive_no_new_products < max_consecutive_no_new:
            self.logger.info(f"Scroll {scroll_count + 1}/{max_scrolls}")

            # 1. Simple, direct scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 2. Wait for new content to load
            self._short_wait(scroll_pause_time)

            # 3. Get all visible products after scrolling
            current_products = self.get_visible_products()
            current_product_count = len(current_products)
            self.logger.info(f"Current product count: {current_product_count}")

            # 4. Extract new products if we found any
            if current_product_count > prev_product_count:
                # Extract only new products (those we haven't seen before)
                new_products = current_products[prev_product_count:]
                new_product_count = 0

                for product in new_products:
                    product_data = self.extract_product_data(product)
                    if product_data:
                        all_products.append(product_data)
                        new_product_count += 1

                self.logger.info(f"Extracted {new_product_count} new products")
                consecutive_no_new_products = 0
            else:
                consecutive_no_new_products += 1
                self.logger.info(f"No new products found in {consecutive_no_new_products} consecutive scrolls")

                # If we're stuck, try a different approach
                if consecutive_no_new_products == 3:
                    self.logger.info("Trying alternative scrolling technique")

                    # Scroll back up then down to trigger loading
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    self._short_wait(scroll_pause_time / 2)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    self._short_wait(scroll_pause_time)

                    # Check for new products again
                    current_products = self.get_visible_products()
                    current_product_count = len(current_products)
                    self.logger.info(f"After alternative scrolling: {current_product_count} products")

                    # If we found new products, process them
                    if current_product_count > prev_product_count:
                        new_products = current_products[prev_product_count:]
                        new_product_count = 0

                        for product in new_products:
                            product_data = self.extract_product_data(product)
                            if product_data:
                                all_products.append(product_data)
                                new_product_count += 1

                        self.logger.info(f"Extracted {new_product_count} new products after alternative scrolling")
                        consecutive_no_new_products = 0

            # 5. Update product count for next iteration
            prev_product_count = current_product_count
            scroll_count += 1

        if consecutive_no_new_products >= max_consecutive_no_new:
            self.logger.info("Reached end of content - no new products after multiple scrolls")
        elif scroll_count >= max_scrolls:
            self.logger.info("Reached maximum number of scrolls")

        self.logger.info(f"Total scrolls: {scroll_count}, Total products extracted: {len(all_products)}")
        return all_products
        
    def _trigger_content_loading(self):
        """Use multiple methods to trigger content loading."""
        # Method 1: Scroll to bottom
        self.scroll_to_bottom()
        
        # Method 2: Send Page Down key if html element exists
        html_elements = self.driver.find_elements(By.TAG_NAME, "html")
        if html_elements and len(html_elements) > 0:
            html_elements[0].send_keys(Keys.PAGE_DOWN)
        
        # Method 3: Execute JavaScript to scroll incrementally
        self.driver.execute_script("window.scrollBy(0, window.innerHeight);")

    def _try_alternative_scrolling(self):
        """Try different scrolling approaches to trigger content loading."""
        # Try different scroll positions
        scroll_positions = [0.3, 0.5, 0.7, 0.9, 1.0]
        for position in scroll_positions:
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {position});")
            self._short_wait(0.3)
            
        # Try scrolling up then down
        self.driver.execute_script("window.scrollTo(0, 0);")
        self._short_wait(0.5)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Try moving mouse to bottom of page with ActionChains if body element exists
        body_elements = self.driver.find_elements(By.TAG_NAME, "body")
        if body_elements and len(body_elements) > 0:
            action = ActionChains(self.driver)
            action.move_to_element(body_elements[0]).perform()
            action.send_keys(Keys.END).perform()
    
    def _short_wait(self, seconds):
        """A very short wait without using time.sleep.
        
        Args:
            seconds: Number of seconds to wait
        """
        WebDriverWait(self.driver, seconds).until(lambda d: True)
    
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

    @staticmethod
    def _get_element_safely(parent, locator):
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

    @staticmethod
    def _get_elements_safely(parent, locator):
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
            review_count_elements = self._get_elements_safely(product_element, ScrollingEcommerceLocators.
                                                              PRODUCT_REVIEW_COUNT)
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
    
    def get_categories(self):
        """Get all categories available in the sidebar navigation.
        
        Returns:
            Dictionary mapping category names to their WebElements
        """
        self.logger.info("Getting all categories")
        categories = {}
        
        category_links = self.find_elements_without_wait(ScrollingEcommerceLocators.CATEGORY_LINK)
        
        for element in category_links:
            if element.is_displayed() and element.text.strip():
                # Check if this is a top-level category (direct child of sidebar-nav)
                parent = self.driver.execute_script("return arguments[0].parentElement", element)
                if parent:
                    parent_class = parent.get_attribute("class") or ""
                    # Only include top-level items
                    if ("sidebar-nav" in parent_class or parent.tag_name == "li" and
                            parent.get_attribute("class") != "li"):
                        name = element.text.strip()
                        categories[name] = element
                        self.logger.info(f"Found category: {name}")
        
        return categories

    def expand_category_if_needed(self, category_name):
        """Expand a category menu if it's not already expanded.

        Args:
            category_name: Name of the category to expand

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Checking if category needs expanding: {category_name}")

        # First check if the category is already expanded
        expanded_menus = self.find_elements(ScrollingEcommerceLocators.EXPANDED_MENU)
        for menu in expanded_menus:
            # Check if menu is a valid element
            if menu is None or isinstance(menu, bool) or not hasattr(menu, 'is_displayed'):
                continue

            link = self._get_element_safely(menu, (By.TAG_NAME, "a"))
            # Check if link is a valid element with text attribute
            if link and hasattr(link, 'text') and link.text.strip() == category_name:
                self.logger.info(f"Category {category_name} is already expanded")
                return True

        # If not expanded, find and click the category
        categories = self.get_categories()
        if category_name in categories:
            category_element = categories[category_name]
            # Check if the category element is valid and can be clicked
            if category_element is None or isinstance(category_element, bool) or not hasattr(category_element, 'click'):
                self.logger.warning(f"Invalid category element for: {category_name}")
                return False

            category_element.click()
            time.sleep(1)  # Wait for animation
            self.logger.info(f"Expanded category: {category_name}")
            return True

        self.logger.warning(f"Could not expand category: {category_name}")
        return False
    
    def get_subcategories(self, parent_category):
        """Get subcategories for a specific parent category.
        
        Args:
            parent_category: Name of the parent category
            
        Returns:
            Dictionary mapping subcategory names to their elements
        """
        self.logger.info(f"Getting subcategories for {parent_category}")
        
        # First ensure the parent category is expanded
        if not self.expand_category_if_needed(parent_category):
            return {}
        
        # Find all expanded category containers
        expanded_containers = self.find_elements_without_wait(ScrollingEcommerceLocators.EXPANDED_MENU)
        for container in expanded_containers:
            # Check if this is the container for our parent category
            header = self._get_element_safely(container, (By.TAG_NAME, "a"))
            if header and header.text.strip() == parent_category:
                # If this is our category, find all subcategory links
                subcategory_links = container.find_elements(By.CSS_SELECTOR, "ul li a")
                subcategories = {}
                
                for link in subcategory_links:
                    name = link.text.strip()
                    if name:
                        subcategories[name] = link
                        self.logger.info(f"Found subcategory: {name}")
                
                return subcategories
        
        return {}
    
    def navigate_to_category(self, category_name):
        """Navigate to a specific category.
        
        Args:
            category_name: Name of the category to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        self.logger.info(f"Navigating to category: {category_name}")
        categories = self.get_categories()
        
        if category_name in categories:
            categories[category_name].click()
            # Reset seen product IDs when navigating to a new page
            self.seen_product_ids = set()
            self.logger.info(f"Navigated to category: {category_name}")
            return True
        
        self.logger.warning(f"Category not found: {category_name}")
        return False
    
    def navigate_to_subcategory(self, parent_category, subcategory_name):
        """Navigate to a specific subcategory.
        
        Args:
            parent_category: Name of the parent category
            subcategory_name: Name of the subcategory to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        self.logger.info(f"Navigating to subcategory: {subcategory_name} under {parent_category}")
        
        # Get subcategories for the parent
        subcategories = self.get_subcategories(parent_category)
        
        if subcategory_name in subcategories:
            subcategories[subcategory_name].click()
            # Reset seen product IDs when navigating to a new page
            self.seen_product_ids = set()
            self.logger.info(f"Navigated to subcategory: {subcategory_name}")
            return True
        
        self.logger.warning(f"Subcategory {subcategory_name} not found under {parent_category}")
        return False
