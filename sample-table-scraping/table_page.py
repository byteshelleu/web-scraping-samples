"""Table page object for interacting with webscraper.io tables."""

from selenium.webdriver.common.by import By
from base_page import BasePage
from locators import TableScraperLocators
from behavior_selenium import SeleniumBehavior
from config import WEBSCRAPER_URL
from logger import logger

class TablePage(BasePage):
    """Page object for the webscraper.io/test-sites/tables website."""
    
    def __init__(self, driver=None, headless=False):
        """Initialize the Table page."""
        super().__init__(driver, headless)
        self.behavior = SeleniumBehavior(self.driver)
    
    def load(self):
        """Load the webscraper.io tables page."""
        self.navigate_to(WEBSCRAPER_URL)
        logger.info(f"Navigated to table test page: {WEBSCRAPER_URL}")
        return self
    
    def get_table_headers(self):
        """Get the headers of the table."""
        headers = []
        header_elements = self.driver.find_elements(*TableScraperLocators.TABLE_HEADERS)
        
        for header in header_elements:
            header_text = header.text.strip()
            headers.append(header_text)
            logger.info(f"Found table header: {header_text}")
            
        return headers
    
    def get_table_data(self):
        """Extract all data from the table."""
        # Wait for elements to load
        self.behavior.wait_for_page_load()
        
        # Get headers
        headers = self.get_table_headers()
        if not headers:
            logger.warning("No table headers found")
            return []
            
        # Get rows
        rows = self.driver.find_elements(*TableScraperLocators.TABLE_ROWS)
        logger.info(f"Found {len(rows)} data rows in table")
        
        # Extract data
        table_data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = {}
            
            for i, cell in enumerate(cells):
                if i < len(headers):  # Only process cells that have corresponding headers
                    header_name = headers[i]
                    cell_value = cell.text.strip()
                    row_data[header_name] = cell_value
            
            table_data.append(row_data)
            logger.info(f"Extracted row data: {row_data}")
            
        return table_data
    
    def check_pagination(self):
        """Check if pagination exists and return the number of pages."""
        pagination_elements = self.driver.find_elements(*TableScraperLocators.PAGINATION)
        
        if not pagination_elements:
            logger.info("No pagination found")
            return 1
            
        # Get all page links
        page_links = self.driver.find_elements(*TableScraperLocators.PAGINATION_LINKS)
        pages = len(page_links)
        logger.info(f"Found pagination with {pages} pages")
        return pages
    
    def navigate_to_page(self, page_number):
        """Navigate to a specific page if pagination exists."""
        pagination_elements = self.driver.find_elements(*TableScraperLocators.PAGINATION)
        
        if not pagination_elements:
            logger.warning("No pagination found, cannot navigate to page")
            return False
            
        # Get all page links
        page_links = self.driver.find_elements(*TableScraperLocators.PAGINATION_LINKS)
        
        for link in page_links:
            if link.text.strip() == str(page_number):
                logger.info(f"Clicking on page {page_number}")
                link.click()
                self.behavior.wait_for_page_load()
                return True
                
        logger.warning(f"Page {page_number} not found in pagination")
        return False
