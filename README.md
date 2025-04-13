# Web Scraping Samples

This repository contains various web scraping examples using different techniques and targeting different types of websites. Each subdirectory represents a different scraping project, designed to showcase best practices in web automation and data extraction.

## Projects

### Sample Table Scraping

Located in: `./sample-table-scraping/`

A robust example of table data extraction using Selenium. This project demonstrates:
- Page Object Model design pattern
- Clean code practices with low cognitive complexity
- Structured data extraction from HTML tables
- Data validation and processing
- CSV output generation

### Sample E-Commerce Scraping

Located in: `./sample-e-commerce-scraping/`

A comprehensive example of scraping e-commerce websites. This project showcases:
- Category and subcategory navigation
- Product data extraction (title, price, description, ratings)
- Structured data organization
- Error prevention with polling-based approaches

### Sample E-Commerce Pagination Scraping

Located in: `./sample-e-commerce-pagination-scraping/`

A specialized example of scraping e-commerce websites with traditional pagination. Features include:
- Navigation through numbered pages
- "Next" and "Previous" button detection
- Last page detection through disabled controls
- Duplicate product prevention
- Category and subcategory navigation
- Complete product data extraction

### Sample E-Commerce Scrolling Scraping

Located in: `./sample-e-commerce-scrolling-scraping/`

An advanced example of scraping e-commerce sites with infinite scrolling. Features include:
- Infinite scroll detection and handling
- Dynamic content loading
- End-of-content detection
- Duplicate product prevention
- Category navigation
- Efficient scroll-based data extraction

## Common Design Principles

All projects in this repository follow these core principles:
- No try/except blocks for flow control
- Cognitive complexity kept under 15
- Centralized locators
- Explicit waits
- Clean, modular code structure
- Instance methods over static methods

## Getting Started

Each project has its own README with specific instructions for running and configuring the scraper.

## Requirements

See individual project requirements.txt files for specific dependencies.

## Target Websites

The samples in this repository target the following demo websites:
- Table Scraping: https://webscraper.io/test-sites/tables
- E-Commerce Scraping: https://webscraper.io/test-sites/e-commerce/allinone
- E-Commerce Pagination Scraping: https://webscraper.io/test-sites/e-commerce/static
- E-Commerce Scrolling: https://webscraper.io/test-sites/e-commerce/scroll

These are safe, legal test sites specifically designed for practicing web scraping. Always ensure you have permission before scraping any website.
