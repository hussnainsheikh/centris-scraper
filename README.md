# Centris Scraper

Centris Scraper is a web scraping tool designed to extract real estate listings from [Centris](https://www.centris.ca). The scraper uses Python and Scrapy, along with Splash for JavaScript rendering, to collect data about properties available for rent or sale in Montreal and other areas.

## Features

- Scrapes property listings including details like price, location, number of bedrooms, bathrooms, and other amenities.
- Uses Splash to render JavaScript-heavy pages.
- Saves the scraped data in a structured format (e.g., CSV, JSON, or database). Currently saving in JSON
- Configurable to target specific property types, locations, and other criteria.

## Requirements

To run this project, you'll need the following installed:

- Python 3.6+
- Scrapy
- Splash
- Docker (optional, for running Splash as a container)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/hussnainsheikh/centris-scraper.git
   cd centris-scraper

2. **Set Up a Virtual Environment (Optional but Recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate

3. **Install the Required Packages**
   ```bash
   pip install scrapy autopep8 pylint scrapy-splash

4. **Download Splash Docker Image**
   ```bash
   docker pull scrapinghub/splash

5. **Run Splash**
   ```bash
   docker run -p 8050:8050 scrapinghub/splash
   ```
This command will start Splash on port 8050 and you can access it by *localhost:8050*

6. **Execute the Spider**
   ```bash
   scrapy crawl listings -o dataset.json


Contributions are welcome! Please open an issue or submit a pull request if you would like to contribute to this project.