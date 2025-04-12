"""Configuration settings for the scrolling e-commerce scraper."""

# URL configuration
BASE_URL = "https://webscraper.io/test-sites/e-commerce/scroll"

# WebDriver configuration
HEADLESS_MODE = True
WAIT_TIMEOUT = 10  # seconds

# Scrolling configuration
SCROLL_PAUSE_TIME = 1.5  # seconds between scrolls
MAX_SCROLLS = 20  # maximum number of scrolls to attempt (safety limit)
ITEMS_PER_SCROLL = 12  # estimated number of items loaded per scroll
SCROLL_OVERLAP_BUFFER = 5  # items to check for duplicate detection

# Output configuration
OUTPUT_FILE = "scraped_products.csv"
