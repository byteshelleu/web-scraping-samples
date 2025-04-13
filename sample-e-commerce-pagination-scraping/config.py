"""Configuration settings for the pagination e-commerce scraper."""

# URL configuration
BASE_URL = "https://webscraper.io/test-sites/e-commerce/static"

# WebDriver configuration
HEADLESS_MODE = True
WAIT_TIMEOUT = 10  # seconds

# Pagination configuration
MAX_PAGES = 50  # Maximum number of pages to scrape

# Output configuration
OUTPUT_FILE = "scraped_products.csv"
