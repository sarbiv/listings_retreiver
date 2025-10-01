"""
Deduplication pipeline for luxury development scraper
"""
import structlog
from typing import Any, Dict
from scrapy import Item
from scrapy.exceptions import DropItem
from slugify import slugify
from ..db.io import DatabaseManager

logger = structlog.get_logger()

class DedupePipeline:
    """Pipeline for deduplicating items based on canonical keys"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.processed_keys = set()
    
    def process_item(self, item: Item, spider) -> Item:
        """Process item through deduplication pipeline"""
        try:
            # Generate canonical key for project
            project_key = self._generate_project_key(item.get('project', {}))
            
            if project_key in self.processed_keys:
                logger.info("Duplicate project found, skipping", key=project_key)
                raise DropItem(f"Duplicate project: {project_key}")
            
            # Check if project exists in database
            existing_project = self._check_existing_project(item.get('project', {}))
            
            if existing_project:
                logger.info("Project exists in database, will update", 
                           project_id=existing_project.id, key=project_key)
                item['_existing_project_id'] = existing_project.id
                item['_is_update'] = True
            else:
                item['_is_update'] = False
            
            self.processed_keys.add(project_key)
            return item
            
        except Exception as e:
            logger.error("Error in deduplication pipeline", error=str(e), item=dict(item))
            raise DropItem(f"Deduplication failed: {e}")
    
    def _generate_project_key(self, project_data: Dict[str, Any]) -> str:
        """Generate canonical key for project"""
        name = project_data.get('name', '') or ''
        developer = project_data.get('developer_name', '') or ''
        city = project_data.get('city', '') or ''
        country = project_data.get('country', '') or ''
        
        # Ensure all values are strings and strip them
        name = str(name).strip() if name else ''
        developer = str(developer).strip() if developer else ''
        city = str(city).strip() if city else ''
        country = str(country).strip() if country else ''
        
        # Create slug from key components
        key_components = [name, developer, city, country]
        key_string = ' '.join(filter(None, key_components))
        
        return slugify(key_string)
    
    def _check_existing_project(self, project_data: Dict[str, Any]) -> Any:
        """Check if project exists in database"""
        try:
            return self.db.get_project_by_key(
                name=project_data.get('name', ''),
                developer_name=project_data.get('developer_name', ''),
                city=project_data.get('city', ''),
                country=project_data.get('country', ''),
                website_url=project_data.get('website_url')
            )
        except Exception as e:
            logger.warning("Error checking existing project", error=str(e))
            return None
