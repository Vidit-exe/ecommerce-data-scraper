# Resilient E-Commerce Web Scraper & Data Pipeline

An automated, fault-tolerant Python data collection pipeline that navigates paginated catalog structures, extracts product attributes, sanitizes messy currency and rating strings, and exports clean CSV and JSON feeds.

## Features
- **Dynamic Pagination Crawling:** Traverses multi-page catalog structures with automated stop conditions.
- **Data Sanitization:** Strips currency symbols, casts price fields to clean floats, and converts CSS star-rating classes into standard numerical values (1–5).
- **Polite Crawling Architecture:** Implements custom User-Agent headers, session reuse, and throttled request intervals to prevent server rate limiting.
- **Multi-Format Export:** Generates ready-to-use CSV and JSON deliverables alongside real-time pipeline metric summaries (average price, in-stock ratio).

## Project Structure