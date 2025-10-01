#!/usr/bin/env python3
"""
Test script to verify the luxury development scraper setup
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import scrapy
        print("✓ Scrapy imported successfully")
    except ImportError as e:
        print(f"✗ Scrapy import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✓ Pydantic imported successfully")
    except ImportError as e:
        print(f"✗ Pydantic import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ Pandas imported successfully")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import structlog
        print("✓ Structlog imported successfully")
    except ImportError as e:
        print(f"✗ Structlog import failed: {e}")
        return False
    
    try:
        import yaml
        print("✓ PyYAML imported successfully")
    except ImportError as e:
        print(f"✗ PyYAML import failed: {e}")
        return False
    
    return True

def test_scraper_modules():
    """Test that scraper modules can be imported"""
    print("\nTesting scraper modules...")
    
    try:
        from scraper.db.models import Project, Unit, Amenity, MediaLink, Source
        print("✓ Database models imported successfully")
    except ImportError as e:
        print(f"✗ Database models import failed: {e}")
        return False
    
    try:
        from scraper.schemas import ProjectIn, UnitIn, AmenityIn
        print("✓ Pydantic schemas imported successfully")
    except ImportError as e:
        print(f"✗ Pydantic schemas import failed: {e}")
        return False
    
    try:
        from scraper.pipelines.clean_normalize import CleanNormalizePipeline
        print("✓ Cleaning pipeline imported successfully")
    except ImportError as e:
        print(f"✗ Cleaning pipeline import failed: {e}")
        return False
    
    try:
        from scraper.pipelines.dedupe import DedupePipeline
        print("✓ Deduplication pipeline imported successfully")
    except ImportError as e:
        print(f"✗ Deduplication pipeline import failed: {e}")
        return False
    
    try:
        from scraper.pipelines.database import DatabasePipeline
        print("✓ Database pipeline imported successfully")
    except ImportError as e:
        print(f"✗ Database pipeline import failed: {e}")
        return False
    
    try:
        from scraper.spiders.tier_a.selene_fort_lauderdale import SeleneFortLauderdaleSpider
        print("✓ Tier A spider imported successfully")
    except ImportError as e:
        print(f"✗ Tier A spider import failed: {e}")
        return False
    
    try:
        from scraper.spiders.tier_b.propertyguru_sg import PropertyGuruSgSpider
        print("✓ Tier B spider imported successfully")
    except ImportError as e:
        print(f"✗ Tier B spider import failed: {e}")
        return False
    
    return True

def test_database_creation():
    """Test database creation"""
    print("\nTesting database creation...")
    
    try:
        from scraper.db.io import DatabaseManager
        
        # Create temporary database
        db = DatabaseManager("sqlite:///:memory:")
        db.init_database()
        print("✓ Database created successfully")
        
        # Test basic operations
        stats = db.get_stats()
        print(f"✓ Database stats retrieved: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        import yaml
        config_path = Path(__file__).parent / 'scraper' / 'config.yaml'
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print("✓ Configuration loaded successfully")
            print(f"  - Default download delay: {config['defaults']['download_delay_sec']}s")
            print(f"  - Sites configured: {len(config['sites'])}")
            return True
        else:
            print("✗ Configuration file not found")
            return False
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏢 Luxury Development Scraper - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_scraper_modules,
        test_database_creation,
        test_config_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scraper is ready to use.")
        print("\nNext steps:")
        print("1. Initialize database: python -m scraper.cli init-db")
        print("2. Run a spider: python -m scraper.cli crawl --spider selene_fort_lauderdale")
        print("3. Export data: python -m scraper.cli export --table projects --output data/exports/projects.csv")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
