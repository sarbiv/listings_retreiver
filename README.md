# 🏢 Global Luxury New-Development Scraper

A comprehensive, local-first scraper for collecting pre-construction and early-market luxury real estate projects from official project pages and regional portals.

## 🎯 Features

- **Tier A Sources**: Official project pages (Selene Fort Lauderdale, Pier Sixty-Six, Berkeley Oval Village)
- **Tier B Sources**: Regional portals (PropertyGuru Singapore, OPR Dubai, Corcoran Sunshine NYC)
- **Robust Data Model**: Projects, units, amenities, media links, and sources
- **Smart Deduplication**: Canonical key-based deduplication with update support
- **Data Cleaning**: Automatic normalization of prices, sizes, currencies, and text
- **Export Options**: SQLite database + CSV exports for business users
- **Rate Limiting**: Respectful crawling with robots.txt compliance
- **International Support**: Multi-currency and multi-locale support

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and setup
git clone <repository-url>
cd luxury-development-scraper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for JS-heavy sites)
playwright install
```

### 2. Initialize Database

```bash
python -m scraper.cli init-db
```

### 3. Run Spiders

```bash
# Tier A (Official project pages)
python -m scraper.cli crawl --spider selene_fort_lauderdale
python -m scraper.cli crawl --spider pier_sixty_six
python -m scraper.cli crawl --spider berkeley_oval_village

# Tier B (Regional portals)
python -m scraper.cli crawl --spider propertyguru_sg --max-projects 200
python -m scraper.cli crawl --spider opr_dubai --max-projects 300
python -m scraper.cli crawl --spider corcoran_sunshine_nyc --max-projects 150
```

### 4. Export Data

```bash
# Export to CSV
python -m scraper.cli export --table projects --output data/exports/projects.csv
python -m scraper.cli export --table units --output data/exports/units.csv
python -m scraper.cli export --table amenities --output data/exports/amenities.csv

# View statistics
python -m scraper.cli stats
```

## 📊 Data Model

### Projects Table
- **Basic Info**: name, developer_name, brand_flag, property_type, status
- **Location**: country, city, address, latitude, longitude
- **Timeline**: est_completion
- **Contact**: website_url, inquiry_url, contact_email
- **Content**: description, completeness_score
- **Metadata**: created_at, updated_at

### Units Table
- **Layout**: unit_name, bedrooms, bathrooms, floor, exposure
- **Size**: size_sqft, size_sqm
- **Pricing**: price_local_value, price_local_currency, price_note
- **Status**: availability_status, maintenance_fees, tax_note
- **Media**: floorplan_url, vr_url, brochure_url
- **Metadata**: last_seen

### Amenities Table
- **Amenity**: amenity (text)

### Media Links Table
- **Media**: type, url, caption
- **Types**: image, render, video, vr, brochure, floorplan

### Sources Table
- **Source**: source_name, source_url
- **Compliance**: robots_ok, tos_ok
- **Metadata**: crawled_at

## 🛠️ Configuration

Edit `scraper/config.yaml` to customize:

```yaml
defaults:
  download_delay_sec: 3.0
  concurrent_requests: 2
  max_pages_per_domain: 400
  obey_robots: true

sites:
  selene_fortlauderdale:
    start_urls: ["https://selenefortlauderdale.com/"]
    max_projects: 50
```

## 🔧 Architecture

```
scraper/
├── db/                    # Database models and I/O
├── pipelines/            # Data processing pipelines
├── spiders/
│   ├── tier_a/          # Official project pages
│   ├── tier_b/          # Regional portals
│   └── utils/           # Spider utilities
├── config.yaml          # Configuration
├── settings.py          # Scrapy settings
└── cli.py              # Command-line interface
```

## 📈 Data Quality

- **Completeness Score**: 0-1 score based on data richness
- **Smart Parsing**: Handles various price formats, sizes, currencies
- **Deduplication**: Prevents duplicate projects across runs
- **Error Handling**: Graceful handling of missing fields
- **Validation**: Pydantic schemas for data validation

## 🌍 International Support

- **Currencies**: USD, GBP, EUR, AED, SGD, ILS, JPY, INR
- **Locales**: US, UK, UAE, Singapore, Israel, Japan, India
- **Local Fields**: Retains original currency and local formatting
- **Normalization**: Light normalization where appropriate

## 🚦 Rate Limiting & Compliance

- **Robots.txt**: Automatic compliance checking
- **Throttling**: 1-2 requests/second per domain
- **Jitter**: Random delays to avoid detection
- **User Agents**: Rotating user agent strings
- **Respectful**: Designed to avoid overloading servers

## 📝 Usage Examples

### Run with Limits
```bash
python -m scraper.cli crawl --spider propertyguru_sg --max-projects 100
```

### Export Specific Data
```bash
python -m scraper.cli export --table projects --output exports/luxury_projects.csv
```

### View Statistics
```bash
python -m scraper.cli stats
```

## 🔍 Monitoring

The scraper provides comprehensive logging:
- **Structured Logging**: JSON-formatted logs with context
- **Progress Tracking**: Real-time progress updates
- **Error Reporting**: Detailed error information
- **Statistics**: Summary of processed items

## 🛡️ Error Handling

- **Graceful Degradation**: Continues processing even with missing data
- **Partial Data**: Stores incomplete records with nulls
- **Retry Logic**: Automatic retries for transient failures
- **Validation**: Data validation before database storage

## 📋 Requirements

- Python 3.11+
- SQLite3
- Playwright (for JS-heavy sites)
- Scrapy 2.11+
- Pydantic 2.5+
- Pandas 2.1+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This scraper is designed for educational and research purposes. Always respect robots.txt files and terms of service. Use responsibly and consider the impact on target websites.
