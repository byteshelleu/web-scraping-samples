# E-Commerce Infinite Scrolling Scraper

This project demonstrates a Selenium-based scraper for e-commerce websites that use infinite scrolling to load products. The scraper is built with clean code principles and best practices in mind.

## Overview

The E-Commerce Infinite Scrolling Scraper handles websites that dynamically load content as users scroll down the page, specifically targeting:
- https://webscraper.io/test-sites/e-commerce/scroll

The main challenges addressed by this project include:
1. Detecting when new content is loaded during scrolling
2. Avoiding duplicate extraction of products
3. Determining when all content has been loaded
4. Managing memory usage during long scrolling sessions
5. Handling attribute references safely without try/except blocks

## Features

- **Dynamic Scrolling**: Handles infinite scrolling pages by automatically scrolling and waiting for new content
- **Duplicate Detection**: Uses a unique product identifier system to prevent duplicate records
- **End of Content Detection**: Multiple methods to determine when all content has been loaded
- **Robust Data Extraction**: Extracts comprehensive product data including titles, prices, descriptions, and ratings
- **Data Processing**: Processes raw extracted data into a consistent format
- **Category Navigation**: Supports navigation between different product categories
- **Null-Safety Patterns**: Implements explicit checks for null values, booleans, and attribute existence
- **Price Analysis**: Calculates price statistics including min, max, average, and total
- **Clean Code Design**: Follows best practices with clear separation of concerns and low cognitive complexity

## Project Structure

- `config.py` - Configuration settings for URLs, scrolling behavior, and output options
- `locators.py` - Centralized Selenium locators for web elements
- `base_page.py` - Base page object with common web interaction methods
- `scrolling_page.py` - Page object specifically for handling infinite scrolling functionality
- `data_handler.py` - Processes and saves scraped product data
- `logger.py` - Logger configuration for the application
- `scrolling_scraper.py` - Main script for running the scraper
- `requirements.txt` - Project dependencies

## How It Works

1. **Initialization**: Set up WebDriver, page objects, and data handler
2. **Page Navigation**: Load the target e-commerce website
3. **Category Selection**: Navigate to a specific category (if specified)
4. **Scrolling and Data Extraction**:
   - Scroll to the bottom of the currently loaded content
   - Wait for new content to load (checks loading indicators)
   - Extract newly visible products
   - Detect duplicates using unique product identifiers
   - Check for end-of-content indicators
   - Repeat until all products are extracted or max scrolls reached
5. **Data Processing**: Process and validate the extracted product data
6. **Price Analysis**: Calculate statistics on product prices
7. **Data Storage**: Save the processed data to a CSV file

## Error Handling Approach

This project follows a strict no try/except approach to error handling:
- Uses polling-based approaches to wait for elements
- Implements predicate functions to verify conditions
- Performs explicit null checks and type validation
- Uses hasattr() to verify object properties before access
- Handles edge cases with boolean checks rather than exception catching

## Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the scraper:
   ```
   python scrolling_scraper.py
   ```

3. View the extracted data in the generated CSV file (default: `scraped_products.csv`)

## Data Extracted

For each product, the scraper extracts:
- Product title
- Price (with numeric value extraction)
- Description
- Rating information (including review count and stars)
- Category information
- URL (when applicable)

## Customization

The behavior of the scraper can be customized through the `config.py` file:
- `HEADLESS_MODE`: Run in headless mode (no visible browser)
- `WEBDRIVER_TIMEOUT`: Maximum time to wait for elements
- `SCROLL_PAUSE_TIME`: Time to pause between scrolls
- `MAX_SCROLLS`: Maximum number of scrolls to attempt
- `DEFAULT_OUTPUT_FILE`: Name of the output CSV file
- `BASE_URL`: Target website URL

## Design Principles

This scraper follows these key design principles:
- No try/except blocks for flow control
- Cognitive complexity under 15 for all methods
- Centralized locators in separate file
- Explicit waits instead of sleep
- Polling-based approach for element detection
- Page Object Model architecture
- Instance methods instead of static methods
- Null-safe attribute access with explicit type checking
