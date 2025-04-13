"""Configuration settings for the scrolling e-commerce scraper."""

# URL configuration
BASE_URL = "https://webscraper.io/test-sites/e-commerce/scroll"

# WebDriver configuration
HEADLESS_MODE = True
WAIT_TIMEOUT = 10  # seconds

# Scrolling configuration
# Scroll Settings
SCROLL_PAUSE_TIME = 2.5  # Increased from 1.5 to give more time for content to load
MAX_SCROLLS = 50
ITEMS_PER_SCROLL = 12
SCROLL_OVERLAP_BUFFER = 5

# Output configuration
OUTPUT_FILE = "scraped_products.csv"
