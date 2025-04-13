"""Pagination page class for handling e-commerce sites with pagination."""

from base_page import BasePage
from locators import PaginationEcommerceLocators
import logging
import time
from selenium.webdriver.common.by import By


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
    
    def find_element_without_wait(self, locator):
        """Find a single element without waiting.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            WebElement if found, None otherwise
        """
        # Directly access elements without waiting
        elements = self.driver.find_elements(*locator)
        
        # Make sure we have elements and the first one isn't a boolean
        if elements and not isinstance(elements[0], bool):
            # Verify the element has is_displayed attribute before returning
            if hasattr(elements[0], 'is_displayed'):
                return elements[0]
        return None
    
    def find_elements_without_wait(self, locator):
        """Find multiple elements without waiting.
        
        Args:
            locator: Tuple of (By.XX, "selector")
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        elements = self.driver.find_elements(*locator)
        return elements

    @staticmethod
    def find_nested_elements(parent, selector):
        """Find elements within a parent element using a CSS selector.
        
        Args:
            parent: Parent WebElement to search within
            selector: CSS selector string
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        if parent is None or isinstance(parent, bool):
            return []
            
        if hasattr(parent, 'find_elements'):
            elements = parent.find_elements(By.CSS_SELECTOR, selector)
            return [element for element in elements if not isinstance(element, bool)
                    and hasattr(element, 'is_displayed')]
        
        return []
    
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
        description_text = self.get_text(description_element)
        description = description_text[:50] if description_text else ""  # First 50 chars for efficiency
        
        return f"{title}|{price}|{description}"
    
    def get_attribute(self, element, attribute):
        """Get attribute value from an element, overriding the BasePage method.

        Args:
            element: WebElement to extract attribute from
            attribute: Name of the attribute

        Returns:
            Attribute value as string if found, empty string otherwise
        """
        if element is None or isinstance(element, bool):
            return ""
            
        if not hasattr(element, 'get_attribute'):
            return ""
            
        attribute_value = element.get_attribute(attribute)
        return attribute_value if attribute_value else ""

    @staticmethod
    def get_text(element):
        """Get text from an element.
        
        Args:
            element: WebElement to extract text from
            
        Returns:
            Text as string if found, empty string otherwise
        """
        if element is None or isinstance(element, bool):
            return ""
        if not hasattr(element, 'text'):
            return ""
        return element.text if element.text else ""
        
    def is_loading_indicator_visible(self):
        """Check if loading indicator is visible.
        
        Returns:
            True if loading indicator is visible, False otherwise
        """
        indicators = self.find_elements_without_wait(PaginationEcommerceLocators.LOADING_INDICATOR)
        if not indicators:
            return False
            
        return any(indicator.is_displayed() for indicator in indicators if not isinstance(indicator, bool)
                   and hasattr(indicator, 'is_displayed'))
    
    def get_visible_products(self):
        """Get all visible product elements on the current page.
        
        Returns:
            List of WebElements representing products
        """
        products = self.find_elements(PaginationEcommerceLocators.PRODUCT_CONTAINER)
        return [product for product in products if not isinstance(product, bool) and hasattr(product, 'is_displayed')
                and product.is_displayed()]
    
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
        review_count_element = self._get_element_safely(product_element, PaginationEcommerceLocators.
                                                        PRODUCT_REVIEW_COUNT)
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
        # First try the standard pagination container
        pagination = self.find_element_without_wait(PaginationEcommerceLocators.PAGINATION_CONTAINER)
        if pagination is not None and not isinstance(pagination, bool) and hasattr(pagination, 'is_displayed'):
            if pagination.is_displayed():
                self.logger.info("Pagination container found and is displayed")
                return True

        # If container not found, check for direct pagination links
        page_links = self.find_elements_without_wait(PaginationEcommerceLocators.PAGINATION_PAGE_LINKS)
        if page_links and any(link.is_displayed() for link in page_links if
                              not isinstance(link, bool) and hasattr(link, 'is_displayed')):
            self.logger.info("Pagination links found")
            return True

        # Look for next/previous buttons directly
        next_button = self.find_element_without_wait(PaginationEcommerceLocators.PAGINATION_NEXT_BUTTON)
        if next_button is not None and not isinstance(next_button, bool) and hasattr(next_button, 'is_displayed'):
            if next_button.is_displayed():
                self.logger.info("Next pagination button found")
                return True

        self.logger.info("No pagination elements found on page")
        return False
    
    def has_next_page(self):
        """Check if there is a next page available.
        
        Returns:
            True if next page is available, False otherwise
        """
        # First check if pagination exists at all
        pagination = self.find_element_without_wait(PaginationEcommerceLocators.PAGINATION_CONTAINER)
        if pagination is None or isinstance(pagination, bool) or not hasattr(pagination, 'is_displayed'):
            self.logger.info("No pagination container found or invalid element")
            return False
            
        if not pagination.is_displayed():
            self.logger.info("Pagination container exists but is not displayed")
            return False
            
        # Check if the next button is disabled - on the test site, disabled next buttons are span elements
        disabled_next = self.find_element_without_wait(PaginationEcommerceLocators.NEXT_PAGE_DISABLED)
        if disabled_next is not None and not isinstance(disabled_next, bool) and hasattr(disabled_next, 'is_displayed'):
            if disabled_next.is_displayed():
                self.logger.info("Next button is disabled")
                return False
            
        # Check if there's an active next button with href
        next_button = self.find_element_without_wait(PaginationEcommerceLocators.PAGINATION_NEXT_BUTTON)
        
        if next_button is None or isinstance(next_button, bool):
            self.logger.info("Next button not found or is boolean value")
            return False
            
        if not hasattr(next_button, 'is_displayed') or not hasattr(next_button, 'get_attribute'):
            self.logger.info("Next button missing required attributes")
            return False
            
        is_displayed = next_button.is_displayed()
        has_href = next_button.get_attribute('href') is not None
        
        result = is_displayed and has_href
        self.logger.info(f"Next page available: {result} (displayed: {is_displayed}, has href: {has_href})")
        return result
    
    def get_current_page_number(self):
        """Get the current page number.
        
        Returns:
            Current page number as integer, or 1 if not found
        """
        active_page = self.find_element_without_wait(PaginationEcommerceLocators.ACTIVE_PAGE)
        if active_page is None or isinstance(active_page, bool):
            return 1
            
        page_text = self.get_text(active_page)
        # Ensure the text is a valid integer before converting
        return int(page_text) if page_text.isdigit() else 1
    
    def go_to_next_page(self):
        """Navigate to the next page.
        
        Returns:
            True if successfully navigated to next page, False otherwise
        """
        if not self.has_next_page():
            self.logger.info("No next page available")
            return False
            
        current_page = self.get_current_page_number()
        self.logger.info(f"Current page before navigation: {current_page}")
        
        # Find next button using the correct locator
        next_button = self.find_element(PaginationEcommerceLocators.PAGINATION_NEXT_BUTTON)
        
        if next_button is None or isinstance(next_button, bool):
            self.logger.warning("Next button not found or is boolean value")
            return False
            
        if not hasattr(next_button, 'click'):
            self.logger.warning("Next button does not have click attribute")
            return False
            
        # Log the URL before clicking
        current_url = self.driver.current_url
        self.logger.info(f"Current URL before navigation: {current_url}")
        
        # Get the href attribute to verify it points to a new page
        next_page_url = next_button.get_attribute("href") if hasattr(next_button, 'get_attribute') else None
        if not next_page_url:
            self.logger.warning("Could not get href from next button")
            return False
            
        self.logger.info(f"Next page URL will be: {next_page_url}")
        
        # Click on the next button
        next_button.click()
        
        # Wait to ensure navigation starts
        self.short_wait(1)
        
        # Check if URL changed
        new_url = self.driver.current_url
        url_changed = new_url != current_url
        self.logger.info(f"URL changed: {url_changed}, new URL: {new_url}")
        
        # Wait for page content to be loaded
        self.short_wait(2)
        
        # Verify we're on the next page (either by URL or page number)
        new_page = self.get_current_page_number()
        page_number_changed = new_page > current_page
        
        if page_number_changed or url_changed:
            self.logger.info(f"Successfully navigated to page {new_page}")
            return True
        else:
            self.logger.warning(f"Navigation may have failed. URL change: {url_changed}, "
                                f"Page number change: {page_number_changed}")
            return False
    
    def extract_products_from_all_pages(self, max_pages=50):
        """Extract products from all pages up to max_pages.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of dictionaries containing product data
        """
        all_products = []
        current_page = 1
        
        # Check if pagination exists at all
        pagination_exists = self.is_pagination_present()
        self.logger.info(f"Pagination detected: {pagination_exists}")
        
        while current_page <= max_pages:
            self.logger.info(f"Processing page {current_page}/{max_pages}")
            
            # Scroll to bottom of current page to ensure all products are loaded
            self.scroll_to_bottom()
            self.short_wait(1)  # Wait for any dynamic content to load
            
            # Extract products from current page
            visible_products = self.get_visible_products()
            self.logger.info(f"Found {len(visible_products)} products on page {current_page}")
            
            for product in visible_products:
                product_data = self.extract_product_data(product)
                if product_data:
                    all_products.append(product_data)
            
            self.logger.info(f"Total products collected so far: {len(all_products)}")
            
            # Log the current URL for debugging
            self.logger.info(f"Current URL: {self.driver.current_url}")
            
            # If no pagination or we've reached the last page, break
            if not pagination_exists or not self.has_next_page():
                self.logger.info("Reached the last page or no pagination available")
                break
                
            # Go to next page
            navigation_successful = self.go_to_next_page()
            if not navigation_successful:
                self.logger.warning("Failed to navigate to next page")
                break
                
            current_page += 1
            self.short_wait(3)  # Increased wait time for the new page to load fully
        
        self.logger.info(f"Extracted a total of {len(all_products)} products from {current_page} pages")
        return all_products
        
    def get_categories(self):
        """Get all categories available in the sidebar navigation.
        
        Returns:
            Dictionary mapping category names to their WebElements
        """
        self.logger.info("Getting all categories")
        categories = {}
        
        category_links = self.find_elements(PaginationEcommerceLocators.CATEGORY_LINK)
        
        for element in category_links:
            if element is None or isinstance(element, bool):
                continue
                
            if not hasattr(element, 'is_displayed') or not hasattr(element, 'text'):
                continue
                
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
        
    def get_subcategories(self, parent_category):
        """Get all subcategories for a given parent category.
        
        Args:
            parent_category: Name of the parent category
            
        Returns:
            Dictionary mapping subcategory names to their WebElements
        """
        self.logger.info(f"Getting subcategories for: {parent_category}")
        subcategories = {}
        
        # First make sure the parent category is expanded
        categories = self.get_categories()
        if parent_category not in categories:
            self.logger.warning(f"Parent category not found: {parent_category}")
            return subcategories
            
        # Check if we need to expand this category
        parent_element = categories[parent_category]
        if not parent_element or isinstance(parent_element, bool):
            return subcategories
            
        # Get all expanded menu items
        expanded_menus = self.find_elements(PaginationEcommerceLocators.EXPANDED_MENU)
        
        # If the parent category isn't already expanded, click it to expand
        parent_expanded = False
        for menu in expanded_menus:
            if menu is None or isinstance(menu, bool) or not hasattr(menu, 'text'):
                continue
                
            menu_text = menu.text or ""
            if parent_category in menu_text:
                parent_expanded = True
                break
                
        # If not expanded, click to expand
        if not parent_expanded and hasattr(parent_element, 'click'):
            self.logger.info(f"Expanding category: {parent_category}")
            parent_element.click()
            self.short_wait(1)  # Wait for animation
            
        # Now find subcategory links
        subcategory_links = self.find_elements(PaginationEcommerceLocators.SUB_CATEGORY_LINKS)
        
        for element in subcategory_links:
            if element is None or isinstance(element, bool):
                continue
                
            if not hasattr(element, 'is_displayed') or not hasattr(element, 'text'):
                continue
                
            if element.is_displayed() and element.text.strip():
                name = element.text.strip()
                subcategories[name] = element
                self.logger.info(f"Found subcategory: {name}")
                
        return subcategories
        
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
            category_element = categories[category_name]
            if category_element is None or isinstance(category_element, bool):
                self.logger.warning(f"Invalid category element for: {category_name}")
                return False
                
            if not hasattr(category_element, 'click'):
                self.logger.warning(f"Category element missing click attribute: {category_name}")
                return False
                
            category_element.click()
            # Reset seen product IDs when navigating to a new page
            self.seen_product_ids = set()
            self.short_wait(2)  # Wait for page to load
            self.logger.info(f"Navigated to category: {category_name}")
            return True
        
        self.logger.warning(f"Category not found: {category_name}")
        return False
        
    def navigate_to_subcategory(self, parent_category, subcategory_name):
        """Navigate to a specific subcategory under a parent category.
        
        Args:
            parent_category: Name of the parent category
            subcategory_name: Name of the subcategory to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        self.logger.info(f"Navigating to subcategory: {subcategory_name} under {parent_category}")
        
        subcategories = self.get_subcategories(parent_category)
        
        if subcategory_name in subcategories:
            subcategory_element = subcategories[subcategory_name]
            if subcategory_element is None or isinstance(subcategory_element, bool):
                self.logger.warning(f"Invalid subcategory element for: {subcategory_name}")
                return False
                
            # Use JavaScript to click to avoid ElementClickInterceptedException
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", subcategory_element)
                self.short_wait(1)  # Wait for scroll
                self.driver.execute_script("arguments[0].click();", subcategory_element)
                self.short_wait(2)  # Wait for page to load
                self.logger.info(f"Navigated to subcategory: {subcategory_name}")
                return True
            except Exception as e:
                self.logger.error(f"Error clicking subcategory element: {e}")
                return False
        
        self.logger.warning(f"Subcategory {subcategory_name} not found under {parent_category}")
        return False

    @staticmethod
    def short_wait(seconds=0.5):
        """Wait for a short period of time.
        
        Args:
            seconds: Number of seconds to wait
        """
        time.sleep(seconds)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
