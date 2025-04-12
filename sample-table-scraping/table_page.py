"""Table page object for interacting with webscraper.io tables."""

from selenium.webdriver.common.by import By
from base_page import BasePage
from config import WEBSCRAPER_URL
from logger import logger
import time


class TablePage(BasePage):
    """Page object for the webscraper.io/test-sites/tables website."""

    def __init__(self, driver=None, headless=False):
        """Initialize the Table page."""
        super().__init__(driver, headless)

    def load(self):
        """Load the webscraper.io tables page."""
        self.navigate_to(WEBSCRAPER_URL)
        logger.info(f"Navigated to table test page: {WEBSCRAPER_URL}")
        # Wait for page to load
        time.sleep(1)
        return self

    def get_navigation_links(self):
        """Get all the navigation links on the page.
        
        Returns:
            List of WebElements representing navigation links
        """
        # Use a more specific selector to get only navigation links
        nav_selector = (By.CSS_SELECTOR, ".col-md-3 a")
        nav_links = self.driver.find_elements(*nav_selector)

        # Filter out invalid elements
        valid_links = [link for link in nav_links
                       if link is not None and not isinstance(link, bool) and hasattr(link, 'text')]

        logger.info(f"Found {len(valid_links)} navigation links")
        return valid_links

    def get_all_tables_data(self):
        """Extract data from all tables across all navigation links.
        
        Returns:
            Dictionary with navigation link text as keys and lists of table data as values
        """
        all_pages_data = {}

        # Get navigation links
        nav_links = self.get_navigation_links()
        if not nav_links:
            logger.warning("No navigation links found")
            # Just scrape current page if no navigation links
            current_page_data = self.extract_all_tables_from_current_page()
            all_pages_data["Main Page"] = current_page_data
            return all_pages_data

        # Store original URL to navigate back after each scrape
        original_url = self.driver.current_url

        # Process each navigation link
        for link in nav_links:
            # Skip invalid links
            if not hasattr(link, 'text') or not hasattr(link, 'click'):
                continue

            link_text = link.text.strip()
            logger.info(f"Clicking on navigation link: {link_text}")

            # Click the link
            link.click()
            time.sleep(1)  # Allow page to load

            # Extract all tables from the current page after navigation
            tables_data = self.extract_all_tables_from_current_page()

            # Store the data with the link text as key
            all_pages_data[link_text] = tables_data

            # Return to original page for next navigation
            self.navigate_to(original_url)
            time.sleep(1)  # Allow page to load

        return all_pages_data

    def extract_all_tables_from_current_page(self):
        """Extract data from all tables on the current page.
        
        Returns:
            List of dictionaries with table data
        """
        all_tables_data = []

        # Find all tables on the page
        tables = self.driver.find_elements(By.CSS_SELECTOR, "table.table")

        logger.info(f"Found {len(tables)} tables on current page")

        # Process each table
        for i, table in enumerate(tables):
            logger.info(f"Processing table {i + 1} on current page")

            # Get headers from this table
            headers = []
            header_elements = table.find_elements(By.CSS_SELECTOR, "thead > tr > th")

            for header in header_elements:
                if header is None or isinstance(header, bool) or not hasattr(header, 'text'):
                    continue

                header_text = header.text.strip()
                headers.append(header_text)

            logger.info(f"Found {len(headers)} headers in table {i + 1}")

            if not headers:
                # Try alternate header finding for tables without thead
                header_elements = table.find_elements(By.CSS_SELECTOR, "tr:first-child > th, tr:first-child > td")
                for header in header_elements:
                    if header is None or isinstance(header, bool) or not hasattr(header, 'text'):
                        continue

                    header_text = header.text.strip()
                    headers.append(header_text)

                logger.info(f"Found {len(headers)} headers in table {i + 1} (alternate method)")

            # If still no headers, create default column names
            if not headers and i == 0:
                # For first table, create default headers if none found
                num_columns = len(table.find_elements(By.CSS_SELECTOR, "tr:first-child > td, tr:first-child > th"))
                headers = [f"Column {j + 1}" for j in range(num_columns)]
                logger.info(f"Created {len(headers)} default headers for table {i + 1}")

            # Skip if no headers and not first table
            if not headers:
                logger.warning(f"No headers found for table {i + 1}, skipping")
                continue

            # Get rows
            rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
            if not rows:
                # Try alternate row finding for tables without tbody
                rows = table.find_elements(By.CSS_SELECTOR, "tr:not(:first-child)")

            logger.info(f"Found {len(rows)} rows in table {i + 1}")

            # Process each row
            table_data = []
            for row in rows:
                if row is None or isinstance(row, bool) or not hasattr(row, 'find_elements'):
                    continue

                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue

                row_data = {}
                for j, cell in enumerate(cells):
                    if j < len(headers) and cell is not None and not isinstance(cell, bool) and hasattr(cell, 'text'):
                        header_name = headers[j]
                        cell_value = cell.text.strip() if cell.text else ""
                        row_data[header_name] = cell_value

                if row_data:
                    table_data.append(row_data)

            # Add this table's data to all tables data
            all_tables_data.extend(table_data)
            logger.info(f"Extracted {len(table_data)} rows from table {i + 1}")

        return all_tables_data
