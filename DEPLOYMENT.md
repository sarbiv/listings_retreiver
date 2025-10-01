# 🚀 Deployment Guide

## Quick Start

### 1. Environment Setup
```bash
# Clone the repository
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

### 2. Verify Installation
```bash
python test_setup.py
```

### 3. Initialize Database
```bash
python -m scraper.cli init-db
```

### 4. Run Spiders
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

### 5. Export Data
```bash
# Export to CSV
python -m scraper.cli export --table projects --output data/exports/projects.csv
python -m scraper.cli export --table units --output data/exports/units.csv
python -m scraper.cli export --table amenities --output data/exports/amenities.csv

# View statistics
python -m scraper.cli stats
```

## Production Deployment

### 1. System Requirements
- Python 3.11+
- 4GB RAM minimum
- 10GB disk space
- Internet connection

### 2. Configuration
Edit `scraper/config.yaml` for production settings:
```yaml
defaults:
  download_delay_sec: 5.0  # Increase for production
  concurrent_requests: 1   # Reduce for production
  max_pages_per_domain: 200  # Reduce for production
  obey_robots: true
  autothrottle: true
```

### 3. Monitoring
- Check logs in `data/scraper.log`
- Monitor database size: `python -m scraper.cli stats`
- Set up automated exports

### 4. Scheduling
Use cron or systemd to schedule regular runs:
```bash
# Daily run at 2 AM
0 2 * * * cd /path/to/scraper && python -m scraper.cli crawl --spider propertyguru_sg --max-projects 100
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**
   ```bash
   python -m scraper.cli init-db
   ```

3. **Spider Errors**
   - Check robots.txt compliance
   - Reduce concurrent requests
   - Increase download delays

4. **Memory Issues**
   - Reduce max_projects limit
   - Process data in batches
   - Monitor system resources

### Logs
- Application logs: `data/scraper.log`
- Scrapy logs: Console output
- Database logs: SQLite logs

## Performance Tuning

### For High Volume
```yaml
defaults:
  download_delay_sec: 1.0
  concurrent_requests: 3
  max_pages_per_domain: 1000
```

### For Respectful Crawling
```yaml
defaults:
  download_delay_sec: 10.0
  concurrent_requests: 1
  max_pages_per_domain: 100
```

## Data Management

### Backup
```bash
# Backup database
cp data/luxury_developments.db backups/luxury_developments_$(date +%Y%m%d).db

# Backup exports
tar -czf exports_$(date +%Y%m%d).tar.gz data/exports/
```

### Cleanup
```bash
# Remove old exports
find data/exports/ -name "*.csv" -mtime +30 -delete

# Vacuum database
sqlite3 data/luxury_developments.db "VACUUM;"
```

## Security Considerations

1. **Rate Limiting**: Always respect robots.txt
2. **User Agents**: Rotating user agents included
3. **Data Privacy**: No personal data collection
4. **Network Security**: Use HTTPS only

## Support

For issues or questions:
1. Check the logs
2. Run test_setup.py
3. Review configuration
4. Check network connectivity
