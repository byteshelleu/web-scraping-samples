# Sample E-commerce Scraper

This project demonstrates a robust implementation of a web scraper designed to extract product data from an e-commerce website. It follows clean code principles and uses the Page Object Model design pattern for maintainable and readable code.

## Target Website

This scraper is designed to work with the following test e-commerce website:
```
https://webscraper.io/test-sites/e-commerce/allinone
```

## Features

- Extracts product information including title, price, description, and ratings
- Navigates through multiple categories and subcategories
- Supports pagination to extract products across multiple pages
- Processes and validates extracted data (e.g., extracting numeric price values)
- Performs price statistics calculations (min, max, average, total)
- Saves data in structured CSV format
- Includes comprehensive logging with timestamps
- Implements polling-based approaches instead of try/except blocks
- Handles edge cases with explicit checks and null safety patterns

## Project Structure

- `ecommerce_scraper.py` - Main script orchestrating the scraping process
- `ecommerce_page.py` - Page Object Model implementation for interacting with the website
- `base_page.py` - Base class providing common functionality for page objects
- `locators.py` - Centralized selectors for the e-commerce website
- `data_handler.py` - Processes and validates scraped data
- `config.py` - Configuration settings
- `logger.py` - Logging configuration
- `requirements.txt` - Dependencies

## Design Principles

This project adheres to the following design principles:
- No try/except blocks for flow control
- Cognitive complexity kept under 15
- Centralized locators for better maintainability
- Explicit waits with polling-based approaches
- Clean, modular code structure
- Page Object Model pattern
- Instance methods over static methods

## Requirements

- Python 3.7+
- Selenium 4.14.0
- pandas 2.1.1
- Chrome browser

## Installation

1. Clone the repository:
```
git clone https://github.com/byteshelleu/web-scraping-samples.git
cd web-scraping-samples/sample-e-commerce-scraping
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

Run the scraper with:
```
python ecommerce_scraper.py
```

The script will:
1. Initialize a Chrome WebDriver
2. Navigate to the e-commerce website
3. Identify categories and subcategories
4. Navigate through each category
5. Handle pagination to extract all products
6. Process and validate the data
7. Calculate price statistics
8. Save the results to a CSV file

## Configuration

You can modify the following settings in `config.py`:
- `BASE_URL` - URL of the e-commerce website
- `HEADLESS_MODE` - Whether to run the browser in headless mode
- `WEBDRIVER_TIMEOUT` - Maximum time to wait for elements
- `DEFAULT_OUTPUT_FILE` - Name of the output CSV file

## Output Structure

The scraper produces a CSV file with the following columns:
- `title` - Product title
- `price` - Original price string (e.g., "$1234.56")
- `price_value` - Extracted numeric price value (e.g., 1234.56)
- `description` - Product description
- `rating` - Rating information
- `review_count` - Number of reviews
- `stars` - Star rating (when available)
- `url` - URL to the product page
- `category` - Product category
- `subcategory` - Product subcategory (when available)

Additionally, the console output and logs will display price statistics for each category, including minimum, maximum, average, and total prices.
