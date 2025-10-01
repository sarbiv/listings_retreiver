#!/usr/bin/env python3
"""
Test script to validate data parsing and export flow
"""
import sys
import os
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scraper.db.io import DatabaseManager
from scraper.db.models import Project, Unit, Amenity, MediaLink, Source

def test_data_flow():
    """Test the complete data flow from parsing to export"""
    print("🧪 Testing Data Flow...")
    print("=" * 60)
    
    # Create temporary database for testing
    temp_db_path = tempfile.mktemp(suffix='.db')
    temp_db = DatabaseManager(f"sqlite:///{temp_db_path}")
    
    try:
        # Initialize test database
        temp_db.init_database()
        print("✅ Test database initialized")
        
        # Test 1: Insert test data
        test_data_insertion(temp_db)
        
        # Test 2: Export to CSV
        test_csv_export(temp_db)
        
        # Test 3: Validate exported data
        test_exported_data_validation()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        # Clean up temporary database
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        print("🧹 Cleaned up test database")

def test_data_insertion(db: DatabaseManager):
    """Test inserting test data"""
    print(f"\n📝 Testing Data Insertion...")
    
    # Test project data
    project_data = {
        'name': 'Test Luxury Project',
        'developer_name': 'Test Developer',
        'city': 'Test City',
        'country': 'Test Country',
        'website_url': 'https://test-project.com',
        'contact_email': 'info@test-project.com',
        'description': 'A test luxury development project',
        'completeness_score': 0.8
    }
    
    project = db.upsert_project(project_data)
    print(f"   ✅ Project inserted: {project.name} (ID: {project.id})")
    
    # Test unit data
    unit_data = [{
        'unit_name': 'Test Unit 1',
        'bedrooms': 2.0,
        'bathrooms': 2.0,
        'size_sqft': 1200.0,
        'price_local_value': 500000.0,
        'price_local_currency': 'USD',
        'price_note': 'From price'
    }]
    
    db.add_units(project.id, unit_data)
    print(f"   ✅ Units inserted: {len(unit_data)} units")
    
    # Test amenity data
    amenities = ['Pool', 'Gym', 'Concierge', 'Parking']
    db.add_amenities(project.id, amenities)
    print(f"   ✅ Amenities inserted: {len(amenities)} amenities")
    
    # Test media link data
    media_data = [{
        'type': 'image',
        'url': 'https://test-project.com/image1.jpg',
        'caption': 'Test image'
    }]
    
    db.add_media_links(project.id, media_data)
    print(f"   ✅ Media links inserted: {len(media_data)} links")
    
    # Test source data
    source_data = {
        'source_name': 'Test Spider',
        'source_url': 'https://test-project.com',
        'robots_ok': True,
        'tos_ok': True
    }
    
    db.add_source(project.id, source_data)
    print(f"   ✅ Source inserted: {source_data['source_name']}")

def test_csv_export(db: DatabaseManager):
    """Test CSV export functionality"""
    print(f"\n📤 Testing CSV Export...")
    
    # Create temporary export directory
    temp_export_dir = tempfile.mkdtemp()
    
    try:
        # Export all tables
        tables = ['projects', 'units', 'amenities', 'media_links', 'sources']
        
        for table in tables:
            output_path = os.path.join(temp_export_dir, f"{table}.csv")
            df = db.export_to_csv(table, output_path)
            
            # Verify file was created and has content
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ {table}.csv exported: {len(df)} rows, {file_size} bytes")
                
                # Check if file ends with newline
                with open(output_path, 'rb') as f:
                    f.seek(-1, 2)
                    last_char = f.read(1)
                    if last_char == b'\n':
                        print(f"      ✅ File ends with newline")
                    else:
                        print(f"      ⚠️  File does not end with newline")
            else:
                print(f"   ❌ {table}.csv not created")
        
        # Store export directory for validation
        global test_export_dir
        test_export_dir = temp_export_dir
        
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        raise

def test_exported_data_validation():
    """Test validation of exported data"""
    print(f"\n🔍 Testing Exported Data Validation...")
    
    # Read and validate each CSV file
    csv_files = ['projects.csv', 'units.csv', 'amenities.csv', 'media_links.csv', 'sources.csv']
    
    for csv_file in csv_files:
        file_path = os.path.join(test_export_dir, csv_file)
        
        if not os.path.exists(file_path):
            print(f"   ❌ {csv_file} not found")
            continue
        
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Basic validation
            if len(df) == 0:
                print(f"   ⚠️  {csv_file} is empty")
                continue
            
            # Check for required columns
            required_columns = get_required_columns(csv_file)
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"   ❌ {csv_file} missing columns: {missing_columns}")
            else:
                print(f"   ✅ {csv_file} has all required columns")
            
            # Check for HTML tags in text columns
            html_issues = check_html_tags(df)
            if html_issues:
                print(f"   ⚠️  {csv_file} has HTML tags in: {html_issues}")
            else:
                print(f"   ✅ {csv_file} has clean text data")
            
            # Check for proper data types
            type_issues = check_data_types(df, csv_file)
            if type_issues:
                print(f"   ⚠️  {csv_file} has type issues: {type_issues}")
            else:
                print(f"   ✅ {csv_file} has correct data types")
            
        except Exception as e:
            print(f"   ❌ Error reading {csv_file}: {e}")

def get_required_columns(csv_file: str) -> list:
    """Get required columns for each CSV file"""
    required_columns = {
        'projects.csv': ['id', 'name', 'city', 'country', 'created_at'],
        'units.csv': ['id', 'project_id', 'unit_name'],
        'amenities.csv': ['id', 'project_id', 'amenity'],
        'media_links.csv': ['id', 'project_id', 'type', 'url'],
        'sources.csv': ['id', 'project_id', 'source_name', 'source_url']
    }
    return required_columns.get(csv_file, [])

def check_html_tags(df: pd.DataFrame) -> list:
    """Check for HTML tags in text columns"""
    html_issues = []
    
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].astype(str).str.contains('<.*?>', regex=True, na=False).any():
            html_issues.append(col)
    
    return html_issues

def check_data_types(df: pd.DataFrame, csv_file: str) -> list:
    """Check for data type issues"""
    type_issues = []
    
    if csv_file == 'projects.csv':
        # Check numeric fields
        if 'completeness_score' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['completeness_score']):
                type_issues.append('completeness_score should be numeric')
    
    elif csv_file == 'units.csv':
        # Check numeric fields
        numeric_fields = ['bedrooms', 'bathrooms', 'size_sqft', 'size_sqm', 'price_local_value']
        for field in numeric_fields:
            if field in df.columns and not df[field].isna().all():
                if not pd.api.types.is_numeric_dtype(df[field]):
                    type_issues.append(f'{field} should be numeric')
    
    return type_issues

def main():
    """Run data flow tests"""
    test_data_flow()

if __name__ == '__main__':
    main()
