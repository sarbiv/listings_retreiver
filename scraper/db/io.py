"""
Database I/O operations for luxury development scraper
"""
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
from typing import Optional, List, Dict, Any
from .models import Base, Project, Unit, Amenity, MediaLink, Source

class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        if database_url is None:
            # Default to project data directory
            data_dir = Path(__file__).parent.parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            database_url = f"sqlite:///{data_dir / 'luxury_developments.db'}"
        
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def init_database(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)
        print(f"Database initialized at: {self.database_url}")
    
    def get_session(self):
        """Get a database session"""
        return self.Session()
    
    def export_to_csv(self, table_name: str, output_path: str, run_id: Optional[str] = None):
        """Export table to CSV with proper formatting"""
        query = f"SELECT * FROM {table_name}"
        if run_id:
            # Add run_id filter if applicable
            if table_name == 'sources':
                query += f" WHERE crawled_at >= '{run_id}'"
        
        df = pd.read_sql_query(query, self.engine)
        
        # Add run_id column if provided
        if run_id and 'run_id' not in df.columns:
            df['run_id'] = run_id
        
        # Clean data before export
        df = self.clean_dataframe_for_export(df)
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export with proper formatting
        df.to_csv(output_path, index=False, encoding='utf-8', lineterminator='\n')
        
        # Ensure file ends with newline
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            with open(output_path, 'r+b') as f:
                f.seek(-1, 2)  # Go to last character
                if f.read(1) != b'\n':  # If last character is not newline
                    f.write(b'\n')
        
        print(f"Exported {len(df)} rows from {table_name} to {output_path}")
        return df
    
    def clean_dataframe_for_export(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean dataframe for CSV export"""
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Replace NaN values with empty strings for better CSV readability
        df_clean = df_clean.fillna('')
        
        # Clean HTML tags from string columns
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).apply(self.strip_html_tags)
        
        return df_clean
    
    def strip_html_tags(self, text: str) -> str:
        """Remove HTML tags from text"""
        if not text or text == 'nan':
            return ''
        
        import re
        # Remove HTML tags
        clean = re.compile('<.*?>')
        cleaned_text = re.sub(clean, '', str(text))
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def get_project_by_key(self, name: str, developer_name: str, city: str, country: str, website_url: str = None):
        """Find project by canonical key"""
        session = self.get_session()
        try:
            query = session.query(Project).filter(
                Project.name == name,
                Project.developer_name == developer_name,
                Project.city == city,
                Project.country == country
            )
            
            if website_url:
                query = query.filter(Project.website_url == website_url)
            
            return query.first()
        finally:
            session.close()
    
    def upsert_project(self, project_data: Dict[str, Any]) -> Project:
        """Insert or update project"""
        session = self.get_session()
        try:
            # Try to find existing project
            existing = self.get_project_by_key(
                project_data['name'],
                project_data.get('developer_name', ''),
                project_data.get('city', ''),
                project_data.get('country', ''),
                project_data.get('website_url')
            )
            
            if existing:
                # Update existing project
                for key, value in project_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                project = existing
            else:
                # Create new project
                project = Project(**project_data)
                session.add(project)
            
            session.commit()
            session.refresh(project)
            return project
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_units(self, project_id: int, units_data: List[Dict[str, Any]]):
        """Add units to project"""
        session = self.get_session()
        try:
            for unit_data in units_data:
                unit_data['project_id'] = project_id
                unit = Unit(**unit_data)
                session.add(unit)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_amenities(self, project_id: int, amenities: List[str]):
        """Add amenities to project"""
        session = self.get_session()
        try:
            for amenity_name in amenities:
                amenity = Amenity(project_id=project_id, amenity=amenity_name)
                session.add(amenity)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_media_links(self, project_id: int, media_data: List[Dict[str, Any]]):
        """Add media links to project"""
        session = self.get_session()
        try:
            for media in media_data:
                media['project_id'] = project_id
                media_link = MediaLink(**media)
                session.add(media_link)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_source(self, project_id: int, source_data: Dict[str, Any]):
        """Add source to project"""
        session = self.get_session()
        try:
            source_data['project_id'] = project_id
            source = Source(**source_data)
            session.add(source)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        session = self.get_session()
        try:
            stats = {}
            stats['projects'] = session.query(Project).count()
            stats['units'] = session.query(Unit).count()
            stats['amenities'] = session.query(Amenity).count()
            stats['media_links'] = session.query(MediaLink).count()
            stats['sources'] = session.query(Source).count()
            return stats
        finally:
            session.close()

def main():
    """CLI interface for database operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database operations')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--export', type=str, help='Export table to CSV')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    
    args = parser.parse_args()
    
    db = DatabaseManager()
    
    if args.init_db:
        db.init_database()
    
    if args.export and args.output:
        db.export_to_csv(args.export, args.output)
    
    if args.stats:
        stats = db.get_stats()
        print("Database Statistics:")
        for table, count in stats.items():
            print(f"  {table}: {count}")

if __name__ == '__main__':
    main()
