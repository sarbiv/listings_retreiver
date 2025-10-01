"""
CLI interface for luxury development scraper
"""
import argparse
import sys
import os
from pathlib import Path
import structlog
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraper.db.io import DatabaseManager
from scraper.pipelines.database import DatabasePipeline

logger = structlog.get_logger()

def init_database():
    """Initialize database"""
    db = DatabaseManager()
    db.init_database()
    print("Database initialized successfully!")

def run_spider(spider_name: str, max_pages: int = None, max_projects: int = None):
    """Run a specific spider"""
    settings = get_project_settings()
    
    # Override settings if limits provided
    if max_pages:
        settings.set('CLOSESPIDER_PAGECOUNT', max_pages)
    if max_projects:
        settings.set('CLOSESPIDER_ITEMCOUNT', max_projects)
    
    process = CrawlerProcess(settings)
    process.crawl(spider_name, max_pages=max_pages, max_projects=max_projects)
    process.start()

def export_data(table_name: str, output_path: str):
    """Export data to CSV"""
    db = DatabaseManager()
    db.export_to_csv(table_name, output_path)
    print(f"Exported {table_name} to {output_path}")

def show_stats():
    """Show database statistics"""
    db = DatabaseManager()
    stats = db.get_stats()
    
    print("Database Statistics:")
    print("=" * 50)
    for table, count in stats.items():
        print(f"{table.capitalize():<15}: {count:>10,}")
    
    total_items = sum(stats.values())
    print("-" * 50)
    print(f"{'Total':<15}: {total_items:>10,}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Luxury Development Scraper CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init database command
    init_parser = subparsers.add_parser('init-db', help='Initialize database')
    
    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Run spider')
    crawl_parser.add_argument('--spider', required=True, help='Spider name to run')
    crawl_parser.add_argument('--max-pages', type=int, help='Maximum pages to crawl')
    crawl_parser.add_argument('--max-projects', type=int, help='Maximum projects to crawl')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to CSV')
    export_parser.add_argument('--table', required=True, help='Table name to export')
    export_parser.add_argument('--output', required=True, help='Output file path')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'init-db':
            init_database()
        
        elif args.command == 'crawl':
            run_spider(args.spider, args.max_pages, args.max_projects)
        
        elif args.command == 'export':
            export_data(args.table, args.output)
        
        elif args.command == 'stats':
            show_stats()
    
    except Exception as e:
        logger.error("CLI error", error=str(e))
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
