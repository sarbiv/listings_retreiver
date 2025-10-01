"""
Database pipeline for luxury development scraper
"""
import structlog
from typing import Any, Dict
from scrapy import Item
from scrapy.exceptions import DropItem
from ..db.io import DatabaseManager
from ..schemas import CleanedProject, CleanedUnit

logger = structlog.get_logger()

class DatabasePipeline:
    """Pipeline for storing items in database"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.stats = {
            'projects_processed': 0,
            'projects_created': 0,
            'projects_updated': 0,
            'units_created': 0,
            'amenities_created': 0,
            'media_links_created': 0,
            'sources_created': 0
        }
    
    def process_item(self, item: Item, spider) -> Item:
        """Process item through database pipeline"""
        try:
            # Extract data from item
            project_data = item.get('project', {})
            units_data = item.get('units', [])
            amenities_data = item.get('amenities', [])
            media_links_data = item.get('media_links', [])
            source_data = item.get('source', {})
            
            # Validate project data
            if not project_data.get('name'):
                raise DropItem("Project name is required")
            
            # Check if this is an update
            is_update = item.get('_is_update', False)
            existing_project_id = item.get('_existing_project_id')
            
            if is_update and existing_project_id:
                # Update existing project
                project = self.update_project(existing_project_id, project_data)
                self.stats['projects_updated'] += 1
            else:
                # Create new project
                project = self.create_project(project_data)
                self.stats['projects_created'] += 1
            
            project_id = project.id
            self.stats['projects_processed'] += 1
            
            # Add units
            if units_data:
                self.db.add_units(project_id, units_data)
                self.stats['units_created'] += len(units_data)
            
            # Add amenities
            if amenities_data:
                self.db.add_amenities(project_id, amenities_data)
                self.stats['amenities_created'] += len(amenities_data)
            
            # Add media links
            if media_links_data:
                self.db.add_media_links(project_id, media_links_data)
                self.stats['media_links_created'] += len(media_links_data)
            
            # Add source
            if source_data:
                self.db.add_source(project_id, source_data)
                self.stats['sources_created'] += 1
            
            logger.info("Project processed successfully", 
                       project_id=project_id, 
                       project_name=project_data.get('name'),
                       is_update=is_update)
            
            return item
            
        except Exception as e:
            logger.error("Error in database pipeline", error=str(e), item=dict(item))
            raise DropItem(f"Database storage failed: {e}")
    
    def create_project(self, project_data: Dict[str, Any]):
        """Create new project in database"""
        # Compute completeness score
        project_data['completeness_score'] = self.compute_completeness_score(project_data)
        
        # Clean project data to match database schema
        cleaned_data = self.clean_project_data_for_db(project_data)
        
        return self.db.upsert_project(cleaned_data)
    
    def update_project(self, project_id: int, project_data: Dict[str, Any]):
        """Update existing project in database"""
        # Compute completeness score
        project_data['completeness_score'] = self.compute_completeness_score(project_data)
        
        # Get existing project and update
        session = self.db.get_session()
        try:
            from ..db.models import Project
            project = session.query(Project).filter(Project.id == project_id).first()
            
            if project:
                for key, value in project_data.items():
                    if hasattr(project, key) and value is not None:
                        setattr(project, key, value)
                
                session.commit()
                session.refresh(project)
                return project
            else:
                raise ValueError(f"Project with ID {project_id} not found")
        finally:
            session.close()
    
    def compute_completeness_score(self, project_data: Dict[str, Any]) -> float:
        """Compute completeness score for project"""
        score = 0.0
        max_score = 10.0
        
        # Essential fields (higher weight)
        if project_data.get('name'):
            score += 2.0
        if project_data.get('city'):
            score += 1.0
        if project_data.get('country'):
            score += 1.0
        if project_data.get('website_url'):
            score += 1.0
        
        # Important fields
        if project_data.get('developer_name'):
            score += 0.5
        if project_data.get('address'):
            score += 0.5
        if project_data.get('description'):
            score += 0.5
        if project_data.get('contact_email') or project_data.get('inquiry_url'):
            score += 0.5
        if project_data.get('est_completion'):
            score += 0.5
        if project_data.get('status'):
            score += 0.5
        
        # Bonus for having media/units (indicates rich data)
        # This would be computed at the project level with units/media
        return min(score / max_score, 1.0)
    
    def clean_project_data_for_db(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean project data to match database schema"""
        # Map email to contact_email
        if 'email' in project_data:
            project_data['contact_email'] = project_data.pop('email')
        
        # Remove phone field if it exists (not in schema)
        project_data.pop('phone', None)
        
        # Only keep fields that exist in the Project model
        valid_fields = {
            'name', 'developer_name', 'brand_flag', 'property_type', 'status',
            'country', 'city', 'address', 'latitude', 'longitude', 'est_completion',
            'website_url', 'inquiry_url', 'contact_email', 'description', 'completeness_score'
        }
        
        cleaned_data = {k: v for k, v in project_data.items() if k in valid_fields}
        
        return cleaned_data
    
    def close_spider(self, spider):
        """Called when spider closes"""
        logger.info("Database pipeline statistics", stats=self.stats)
        
        # Print summary
        print("\n" + "="*50)
        print("DATABASE PIPELINE SUMMARY")
        print("="*50)
        print(f"Projects processed: {self.stats['projects_processed']}")
        print(f"Projects created:   {self.stats['projects_created']}")
        print(f"Projects updated:   {self.stats['projects_updated']}")
        print(f"Units created:      {self.stats['units_created']}")
        print(f"Amenities created:  {self.stats['amenities_created']}")
        print(f"Media links created: {self.stats['media_links_created']}")
        print(f"Sources created:    {self.stats['sources_created']}")
        print("="*50)
