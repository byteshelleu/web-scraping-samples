"""Centralized locators for the scrolling e-commerce scraper."""

from selenium.webdriver.common.by import By


class PaginationEcommerceLocators:
    """Locators for the pagination e-commerce website elements."""

    # Main container elements
    PRODUCT_CONTAINER = (By.CSS_SELECTOR, ".thumbnail")

    # Product elements
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".title")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".price")
    PRODUCT_DESCRIPTION = (By.CSS_SELECTOR, ".description")
    PRODUCT_RATING = (By.CSS_SELECTOR, ".ratings")
    PRODUCT_REVIEW_COUNT = (By.CSS_SELECTOR, ".ratings .pull-right")
    PRODUCT_STARS = (By.CSS_SELECTOR, ".ratings .glyphicon-star")

    # Loading indicators
    LOADING_INDICATOR = (By.CSS_SELECTOR, ".loading-indicator")

    # Navigation and category locators
    CATEGORY_LINK = (By.CSS_SELECTOR, ".sidebar-nav a")
    
    # Main category links (Computers, Phones) 
    MAIN_CATEGORY_LINKS = (By.CSS_SELECTOR, ".sidebar-nav > li > a")
    
    # Subcategory links (Laptops, Tablets under Computers)
    SUB_CATEGORY_LINKS = (By.CSS_SELECTOR, ".sidebar-nav li.active ul li a")
    
    EXPANDED_MENU = (By.CSS_SELECTOR, ".sidebar-nav li.open, .sidebar-nav li.active")

    # Pagination elements based on actual website structure
    PAGINATION_CONTAINER = (By.CSS_SELECTOR, "ul.pagination")
    PAGINATION_NEXT_BUTTON = (By.XPATH, "//a[contains(text(), '›')]")
    PAGINATION_PREVIOUS_BUTTON = (By.XPATH, "//a[contains(text(), '‹')]")
    PAGINATION_PAGE_LINKS = (By.CSS_SELECTOR, "ul.pagination > li > a")
    ACTIVE_PAGE = (By.CSS_SELECTOR, "ul.pagination > li.active")
    NEXT_PAGE_DISABLED = (By.XPATH, "//li[contains(@class, 'disabled')]/span[contains(text(), '›')]")
    PAGE_NUMBER_LINKS = (By.XPATH, "//ul[contains(@class, 'pagination')]/li/a[not(contains(text(), '‹')) and not(contains(text(), '›'))]")