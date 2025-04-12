"""Configuration settings for the e-commerce scraper."""

# URL configuration
BASE_URL = "https://webscraper.io/test-sites/e-commerce/allinone"

# WebDriver configuration
HEADLESS_MODE = True
WAIT_TIMEOUT = 10  # seconds

# Output configuration
OUTPUT_FILE = "scraped_products.csv"
