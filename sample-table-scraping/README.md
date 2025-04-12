# Sample Table Scraper

A Python web scraper using Selenium to collect data from HTML tables on [webscraper.io](https://webscraper.io/test-sites/tables).

## Description

This project demonstrates web scraping techniques using Python and Selenium. It navigates to the webscraper.io test site with sample tables, extracts tabular data, and saves it to a CSV file. The project follows best practices for web scraping, including proper page object patterns and avoiding try/except blocks for flow control.

## Key Features

- Extracts data from multiple tables across different pages
- Navigates through links to find all tables on the site
- Handles tables with different structures (with/without thead, multiple header rows)
- Processes numeric data (e.g., extracting price values for analysis)
- Generates structured CSV files for each page's tables
- Creates a consolidated JSON with all scraped data
- Provides comprehensive logging throughout the scraping process

## Learning Objectives

- Using Selenium to automate browser interactions
- Locating table elements using CSS and XPath selectors
- Extracting structured data from HTML tables
- Handling navigation between pages in web scraping
- Processing and saving scraped data to CSV and JSON formats

## Prerequisites

- Python 3.7+
- Chrome browser installed
- Internet connection

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```
   python table_scraper.py
   ```
2. The script will:
   - Open a Chrome browser (visible or headless)
   - Navigate to webscraper.io/test-sites/tables
   - Extract table headers and data from all navigation links
   - Process the data (e.g., extract numeric values from price)
   - Save the data to separate CSV files for each page
   - Create a consolidated JSON file with all scraped data

## Project Structure

- **table_scraper.py**: Main script that orchestrates the scraping process
- **table_page.py**: Page object for interacting with the table website
- **base_page.py**: Base class for page objects with common methods
- **data_handler.py**: Data processing and export functionality
- **config.py**: Configuration settings for the scraper
- **logger.py**: Logging configuration

## Key Coding Rules Followed

- No try/except blocks for flow control
- Low cognitive complexity (under 15)
- Explicit waits for reliable element interaction
- Clean, modular code structure
- Page Object Model pattern
- Instance methods instead of static methods

## Sample Output

The scraper produces:
1. CSV files with table data from each navigation section
2. A consolidated JSON file containing all scraped data
3. Price statistics including min, max, average, and total values

## License

This project is open source and available for educational purposes.
