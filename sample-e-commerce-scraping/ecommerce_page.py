"""E-commerce page class for interacting with the e-commerce website."""

from base_page import BasePage
from locators import EcommerceLocators
import logging
from selenium.webdriver.common.by import By
import time


class EcommercePage(BasePage):
    """Page object for the e-commerce website."""

    def __init__(self, driver, timeout=10):
        """Initialize the e-commerce page.
        
        Args:
            driver: Selenium WebDriver instance
            timeout: Maximum wait time for elements
        """
        super().__init__(driver, timeout)
        self.logger = logging.getLogger(__name__)

    def load(self, url):
        """Load the e-commerce website.
        
        Args:
            url: URL of the e-commerce website
            
        Returns:
            True if the page loaded successfully
        """
        self.logger.info(f"Loading e-commerce page: {url}")
        success = self.open_url(url)
        if success:
            self.logger.info("E-commerce page loaded successfully")
            return True
        return False

    def get_categories(self):
        """Get all available main categories from the navigation menu.
        
        Returns:
            Dictionary mapping category names to their elements
        """
        self.logger.info("Getting available main categories")
        category_elements = self.find_elements(EcommerceLocators.CATEGORY_ITEMS)
        categories = {}

        for element in category_elements:
            name = element.text.strip() if element else ""
            if name:
                categories[name] = element
                self.logger.info(f"Found category: {name}")

        return categories

    def get_all_navigation_links(self):
        """Get all navigation links including categories and subcategories.
        
        Returns:
            Dictionary with category/subcategory names and their elements
        """
        self.logger.info("Getting all navigation links")
        all_links = {}

        # Get all category links
        category_links = self.find_elements(EcommerceLocators.CATEGORY_LINK)
        for link in category_links:
            text = link.text.strip()
            if text:
                all_links[text] = link
                self.logger.info(f"Found navigation link: {text}")

        return all_links

    def expand_category_if_needed(self, category_name):
        """Expand a category menu if it's not already expanded.
        
        Args:
            category_name: Name of the category to expand
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Checking if category needs expanding: {category_name}")

        # First check if the category is already expanded
        expanded_menus = self.find_elements(EcommerceLocators.EXPANDED_MENU)
        for menu in expanded_menus:
            link = self._get_element_safely(menu, (By.TAG_NAME, "a"))
            if link and link.text.strip() == category_name:
                self.logger.info(f"Category {category_name} is already expanded")
                return True

        # If not expanded, find and click the category
        categories = self.get_categories()
        if category_name in categories:
            categories[category_name].click()
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
        expanded_containers = self.find_elements(EcommerceLocators.EXPANDED_MENU)
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

    def navigate_to_link(self, link_element):
        """Navigate to a specific link.
        
        Args:
            link_element: WebElement of the link to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        if not link_element:
            return False

        link_text = link_element.text.strip()
        self.logger.info(f"Navigating to: {link_text}")

        link_element.click()
        self.logger.info(f"Navigated to: {link_text}")
        return True

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
            self.logger.info(f"Navigated to subcategory: {subcategory_name}")
            return True

        self.logger.warning(f"Subcategory {subcategory_name} not found under {parent_category}")
        return False

    def get_navigation_structure(self):
        """Get the complete navigation structure of the site.
        
        Returns:
            Dictionary representing the site's navigation structure
        """
        self.logger.info("Analyzing site navigation structure")
        structure = {}

        # Get main categories
        main_categories = self.get_categories()

        for category_name in main_categories:
            # Skip home as it's not a product category
            if category_name.lower() == 'home':
                continue

            structure[category_name] = {"link": main_categories[category_name], "subcategories": {}}

            # Check for subcategories
            self.expand_category_if_needed(category_name)
            subcategories = self.get_subcategories(category_name)

            for subcategory_name, subcategory_link in subcategories.items():
                structure[category_name]["subcategories"][subcategory_name] = subcategory_link

        return structure

    def extract_product_data(self, product_element):
        """Extract data from a product element.

        Args:
            product_element: WebElement representing a product

        Returns:
            Dictionary containing product data
        """
        # Check if product element is valid
        if product_element is None or isinstance(product_element, bool) or not hasattr(product_element, 'is_displayed'):
            return {}

        product_data = {}

        # Extract title
        title_element = self._get_element_safely(product_element, EcommerceLocators.PRODUCT_TITLE)
        product_data['title'] = title_element.text.strip() if title_element and hasattr(title_element, 'text') else ""

        # Extract price
        price_element = self._get_element_safely(product_element, EcommerceLocators.PRODUCT_PRICE)
        product_data['price'] = price_element.text.strip() if price_element and hasattr(price_element, 'text') else ""

        # Extract description
        description_element = self._get_element_safely(product_element, EcommerceLocators.PRODUCT_DESCRIPTION)
        product_data['description'] = description_element.text.strip() if description_element and hasattr(
            description_element, 'text') else ""

        # Extract rating information
        rating_elements = self._get_elements_safely(product_element, EcommerceLocators.PRODUCT_RATING)
        if rating_elements:
            rating_element = rating_elements[0]
            if rating_element and not isinstance(rating_element, bool) and hasattr(rating_element, 'text'):
                product_data['rating'] = rating_element.text.strip()

            # Extract number of reviews
            review_count_elements = self._get_elements_safely(product_element, EcommerceLocators.PRODUCT_REVIEW_COUNT)
            if review_count_elements:
                review_element = review_count_elements[0]
                if review_element and not isinstance(review_element, bool) and hasattr(review_element, 'text'):
                    product_data['review_count'] = review_element.text.strip()

            # Extract star rating
            star_elements = self._get_elements_safely(product_element, EcommerceLocators.PRODUCT_STARS)
            product_data['stars'] = len(star_elements)

        # Get product URL
        if title_element and not isinstance(title_element, bool):
            link_element = title_element if hasattr(title_element,
                                                    'tag_name') and title_element.tag_name == 'a' else None

            if not link_element and hasattr(title_element, 'find_element'):
                # Try to find an anchor tag within the title element
                links = self._get_elements_safely(title_element, (By.TAG_NAME, "a"))
                link_element = links[0] if links else None

            if link_element and hasattr(link_element, 'get_attribute'):
                href = link_element.get_attribute('href')
                if href is not None:
                    product_data['url'] = href

        self.logger.info(f"Extracted data for product: {product_data.get('title', 'Unknown')}")
        return product_data

    @staticmethod
    def _get_element_safely(parent, locator):
        """Safely get an element without raising exceptions.

        Args:
            parent: Parent WebElement to search within
            locator: Locator tuple (By.XX, "selector")

        Returns:
            WebElement if found, None otherwise
        """
        # First validate parent before trying to use it
        if parent is None:
            return None

        if isinstance(parent, bool):
            return None

        # Create a separate variable to avoid the IDE warning
        find_elements_attr = getattr(parent, 'find_elements', None)
        if find_elements_attr is None:
            return None

        # Use the attribute as a function
        elements = find_elements_attr(*locator)

        # Check if we have elements and get the first one
        if not elements:
            return None

        element = elements[0]

        # Validate the element isn't a boolean and has expected attributes
        if isinstance(element, bool):
            return None

        if not hasattr(element, 'is_displayed'):
            return None

        return element

    @staticmethod
    def _get_elements_safely(parent, locator):
        """Safely get elements without raising exceptions.

        Args:
            parent: Parent WebElement to search within
            locator: Locator tuple (By.XX, "selector")

        Returns:
            List of WebElements if found, empty list otherwise
        """
        # First validate parent before trying to use it
        if parent is None:
            return []

        if isinstance(parent, bool):
            return []

        # Create a separate variable to avoid the IDE warning
        find_elements_attr = getattr(parent, 'find_elements', None)
        if find_elements_attr is None:
            return []

        # Use the attribute as a function
        all_elements = find_elements_attr(*locator)

        # Filter out any boolean values or invalid elements
        valid_elements = []
        for element in all_elements:
            if element is None:
                continue

            if isinstance(element, bool):
                continue

            if not hasattr(element, 'is_displayed'):
                continue

            valid_elements.append(element)

        return valid_elements

    def get_products_on_page(self):
        """Get all products on the current page.
        
        Returns:
            List of dictionaries containing product data
        """
        self.logger.info("Getting products on current page")
        product_elements = self.find_elements(EcommerceLocators.PRODUCT_CONTAINERS)
        self.logger.info(f"Found {len(product_elements)} products on page")

        products = []
        for product_element in product_elements:
            product_data = self.extract_product_data(product_element)
            if product_data:
                products.append(product_data)

        self.logger.info(f"Extracted data for {len(products)} products")
        return products

    def has_next_page(self):
        """Check if there is a next page of products.

        Returns:
            True if there is a next page, False otherwise
        """
        next_page_element = self.find_element(EcommerceLocators.NEXT_PAGE)
        # Explicitly check for None and boolean values
        return next_page_element is not None and not isinstance(next_page_element, bool)

    def go_to_next_page(self):
        """Navigate to the next page of products.

        Returns:
            True if navigation was successful, False otherwise
        """
        next_page_element = self.find_element(EcommerceLocators.NEXT_PAGE)

        # Check if the element exists, is not a boolean, and has click method
        if next_page_element is None or isinstance(next_page_element, bool) or not hasattr(next_page_element, 'click'):
            self.logger.warning("No next page button found")
            return False

        next_page_element.click()
        self.logger.info("Navigated to next page")

        # Give time for the page to load
        time.sleep(1)
        return True
