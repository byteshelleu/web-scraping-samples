"""Centralized locators for the scrolling e-commerce scraper."""

from selenium.webdriver.common.by import By

class ScrollingEcommerceLocators:
    """Locators for the scrolling e-commerce website elements."""
    
    # Main container elements
    PRODUCT_CONTAINER = (By.CSS_SELECTOR, ".thumbnail")
    PRODUCTS_WRAPPER = (By.CSS_SELECTOR, ".wrapper")
    
    # Product elements
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".title")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".price")
    PRODUCT_DESCRIPTION = (By.CSS_SELECTOR, ".description")
    PRODUCT_RATING = (By.CSS_SELECTOR, ".ratings")
    PRODUCT_REVIEW_COUNT = (By.CSS_SELECTOR, ".ratings .pull-right")
    PRODUCT_STARS = (By.CSS_SELECTOR, ".ratings .glyphicon-star")
    
    # Loading indicators
    LOADING_INDICATOR = (By.CSS_SELECTOR, ".loading-indicator")
    LOADING_TEXT = (By.CSS_SELECTOR, ".loading-text")
    
    # Navigation elements
    NAVIGATION_MENU = (By.CSS_SELECTOR, ".navbar")
    
    # Product details page elements
    PRODUCT_DETAILS_CONTAINER = (By.CSS_SELECTOR, ".product-details")
    PRODUCT_IMAGE = (By.CSS_SELECTOR, ".img-responsive")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, ".btn-success")
    
    # End of content indicators (may vary based on site implementation)
    END_OF_CONTENT_MESSAGE = (By.CSS_SELECTOR, ".end-of-results")
    NO_MORE_PRODUCTS_INDICATOR = (By.CSS_SELECTOR, ".no-more-products")
