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
            List of tuples containing (link_text, href) for each navigation link
        """
        # The links in the left sidebar from the screenshot are identified by these selectors
        # Use a comprehensive list of selectors to ensure we capture all navigation links
        nav_selectors = [
            ".list-group-item",  # General list group items 
            ".col-md-3 a.list-group-item",  # List group items in the sidebar
            "a.semantically-correct-tables",  # Specific link classes from screenshot
            "a.tables-without-the-thead-tag", 
            "a.tables-with-multiple-header-rows"
        ]
        
        # Try each selector until we find some links
        all_links = []
        for selector in nav_selectors:
            links = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if links:
                all_links.extend(links)
        
        # If we still didn't find any links, try a more generic approach
        if not all_links:
            # Look for any link in the page with relevant text content
            relevant_text = ["semantically", "thead", "multiple header", "tables"]
            all_page_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in all_page_links:
                if link is None or isinstance(link, bool):
                    continue
                    
                if not hasattr(link, 'text') or not hasattr(link, 'is_displayed'):
                    continue
                    
                link_text = link.text.lower() if link.text else ""
                if link.is_displayed() and any(text in link_text for text in relevant_text):
                    all_links.append(link)
        
        # Store link information as tuples of (link_text, href) to avoid stale element issues
        valid_links = []
        for link in all_links:
            if link is None or isinstance(link, bool):
                continue
                
            if not hasattr(link, 'text') or not hasattr(link, 'get_attribute'):
                continue
                
            link_text = link.text.strip()
            link_href = link.get_attribute('href')
            
            if link_text and link_href:
                valid_links.append((link_text, link_href))

        logger.info(f"Found {len(valid_links)} navigation links")
        return valid_links

    def get_all_tables_data(self):
        """Extract data from all tables across all navigation links.
        
        Returns:
            Dictionary with navigation link text as keys and lists of table data as values
        """
        all_pages_data = {}

        # Get navigation links as (text, href) tuples to avoid stale element issues
        nav_links = self.get_navigation_links()
        if not nav_links:
            logger.warning("No navigation links found")
            # Just scrape current page if no navigation links
            current_page_data = self.extract_all_tables_from_current_page()
            all_pages_data["Main Page"] = current_page_data
            return all_pages_data

        # Process each navigation link
        for link_text, link_href in nav_links:
            logger.info(f"Navigating to link: {link_text}")

            # Navigate directly to the href instead of clicking (avoids stale elements)
            self.navigate_to(link_href)
            time.sleep(1)  # Allow page to load

            # Extract all tables from the current page after navigation
            tables_data = self.extract_all_tables_from_current_page()

            # Store the data with the link text as key
            all_pages_data[link_text] = tables_data

            # Return to original page for next navigation
            self.navigate_to(WEBSCRAPER_URL)
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
