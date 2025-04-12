"""Centralized locators for the web scraper."""

from selenium.webdriver.common.by import By

class TableScraperLocators:
    """Locators for the webscraper.io/test-sites/tables website."""
    
    # Table elements
    TABLE = (By.CLASS_NAME, "table")
    TABLE_HEADERS = (By.CSS_SELECTOR, "table.table > thead > tr > th")
    TABLE_ROWS = (By.CSS_SELECTOR, "table.table > tbody > tr")
    TABLE_CELLS = (By.CSS_SELECTOR, "table.table > tbody > tr > td")
    
    # Specific column data - using indexed positions
    TABLE_ID_COLUMN = (By.CSS_SELECTOR, "table.table > tbody > tr > td:nth-child(1)")
    TABLE_NAME_COLUMN = (By.CSS_SELECTOR, "table.table > tbody > tr > td:nth-child(2)")
    TABLE_PRICE_COLUMN = (By.CSS_SELECTOR, "table.table > tbody > tr > td:nth-child(3)")
    
    # Pagination elements (if needed)
    PAGINATION = (By.CLASS_NAME, "pagination")
    PAGINATION_LINKS = (By.CSS_SELECTOR, ".pagination > li > a")
    NEXT_PAGE = (By.CSS_SELECTOR, ".pagination > li.next > a")
    PREVIOUS_PAGE = (By.CSS_SELECTOR, ".pagination > li.prev > a")
