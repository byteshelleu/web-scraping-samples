# E-Commerce Pagination Scraper

This project demonstrates a Selenium-based scraper for e-commerce websites that use pagination to display products across multiple pages. The scraper is built with clean code principles and best practices in mind.

## Overview

The E-Commerce Pagination Scraper handles websites that organize products across multiple pages with numbered navigation, specifically targeting:
- https://webscraper.io/test-sites/e-commerce/static

The main challenges addressed by this project include:
1. Navigating through paginated content
2. Detecting when the last page is reached
3. Avoiding duplicate extraction of products
4. Handling attribute references safely without try/except blocks
5. Ensuring all products from all categories and subcategories are extracted

## Features

- **Pagination Handling**: Automatically navigates through all product pages by detecting and clicking on pagination controls
- **Duplicate Detection**: Uses a unique product identifier system to prevent duplicate records
- **End of Content Detection**: Detects when the last page has been reached by checking for disabled "next" buttons
- **Robust Data Extraction**: Extracts comprehensive product data including titles, prices, descriptions, and ratings
- **Data Processing**: Processes raw extracted data into a consistent format
- **Category Navigation**: Supports navigation between different product categories and subcategories
- **Null-Safety Patterns**: Implements explicit checks for null values, booleans, and attribute existence
- **Price Analysis**: Calculates price statistics including min, max, average, and total
- **Clean Code Design**: Follows best practices with clear separation of concerns and low cognitive complexity
- **Complete Product Coverage**: Successfully extracts all 147 unique products from the target website

## Project Structure

- `config.py` - Configuration settings for URLs, pagination behavior, and output options
- `locators.py` - Centralized Selenium locators for web elements including pagination controls
- `base_page.py` - Base page object with common web interaction methods
- `pagination_page.py` - Page object specifically for handling pagination functionality
- `data_handler.py` - Processes and saves scraped product data
- `pagination_scraper.py` - Main script for running the scraper
- `requirements.txt` - Project dependencies

## How It Works

1. **Initialization**: Set up WebDriver, page objects, and data handler
2. **Page Navigation**: Load the target e-commerce website
3. **Category Selection**: Navigate through each main category
4. **Subcategory Navigation**: For each category, navigate through all subcategories
5. **Pagination and Data Extraction**:
   - Extract all visible products on the current page
   - Detect duplicates using unique product identifiers
   - Check if there is a next page
   - Click on the next page button and wait for page to load
   - Repeat until all pages are processed or max pages reached
6. **Data Processing**: Process and validate the extracted product data
7. **Price Analysis**: Calculate statistics on product prices
8. **Data Storage**: Save the processed data to a CSV file

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
   python pagination_scraper.py
   ```

3. View the extracted data in the generated CSV file (default: `scraped_products.csv`)

## Data Extracted

For each product, the scraper extracts:
- Product title
- Price (with numeric value extraction)
- Description
- Rating information (including review count and stars)
- Category and subcategory information
- URL (when applicable)

## Customization

The behavior of the scraper can be customized through the `config.py` file:
- `HEADLESS_MODE`: Run in headless mode (no visible browser)
- `WAIT_TIMEOUT`: Maximum time to wait for elements
- `MAX_PAGES`: Maximum number of pages to process
- `OUTPUT_FILE`: Name of the output CSV file
- `BASE_URL`: Target website URL

## Design Principles

This scraper follows these key design principles:
- No try/except blocks for flow control
- Cognitive complexity under 15 for all methods
- Proper instance methods (no static methods)
- Explicit null checking
- Polling-based waits
