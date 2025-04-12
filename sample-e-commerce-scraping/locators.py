"""Centralized locators for the e-commerce scraper."""

from selenium.webdriver.common.by import By


class EcommerceLocators:
    """Locators for the e-commerce website elements."""

    # Navigation and category locators
    CATEGORY_ITEMS = (By.CSS_SELECTOR, "#side-menu .nav-item")
    CATEGORY_LINK = (By.CSS_SELECTOR, ".sidebar-nav a")
    EXPANDED_MENU = (By.CSS_SELECTOR, ".sidebar-nav .nav-item.active")

    # Product list locators
    PRODUCT_CONTAINERS = (By.CSS_SELECTOR, ".thumbnail")
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".title")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".price")
    PRODUCT_DESCRIPTION = (By.CSS_SELECTOR, ".description")
    PRODUCT_RATING = (By.CSS_SELECTOR, ".ratings")
    PRODUCT_REVIEW_COUNT = (By.CSS_SELECTOR, ".ratings .pull-right")
    PRODUCT_STARS = (By.CSS_SELECTOR, ".ratings .glyphicon-star")

    # Pagination
    NEXT_PAGE = (By.CSS_SELECTOR, ".pagination .next a")
