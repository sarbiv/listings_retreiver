"""
Debug pipeline for spider data flow analysis
"""
import structlog
from typing import Any, Dict
from scrapy import Item
from scrapy.exceptions import DropItem

logger = structlog.get_logger()

class DebugPipeline:
    """Pipeline for debugging spider data flow"""
    
    def __init__(self):
        self.debug_data = {
            'items_processed': 0,
            'raw_items': [],
            'parsed_items': [],
            'errors': []
        }
    
    def process_item(self, item: Item, spider) -> Item:
        """Process item through debug pipeline"""
        try:
            self.debug_data['items_processed'] += 1
            
            # Capture raw item data
            raw_item = dict(item)
            self.debug_data['raw_items'].append({
                'spider': spider.name,
                'item_number': self.debug_data['items_processed'],
                'raw_data': raw_item
            })
            
            # Log detailed item information
            logger.info("DEBUG: Raw item received", 
                       spider=spider.name,
                       item_number=self.debug_data['items_processed'],
                       item_keys=list(raw_item.keys()))
            
            # Analyze project data
            if 'project' in raw_item:
                project_data = raw_item['project']
                logger.info("DEBUG: Project data", 
                           project_name=project_data.get('name', 'No name'),
                           project_keys=list(project_data.keys()),
                           project_data=project_data)
            
            # Analyze units data
            if 'units' in raw_item:
                units_data = raw_item['units']
                logger.info("DEBUG: Units data", 
                           units_count=len(units_data),
                           units_data=units_data)
            
            # Analyze amenities data
            if 'amenities' in raw_item:
                amenities_data = raw_item['amenities']
                logger.info("DEBUG: Amenities data", 
                           amenities_count=len(amenities_data),
                           amenities_data=amenities_data)
            
            # Analyze media links data
            if 'media_links' in raw_item:
                media_data = raw_item['media_links']
                logger.info("DEBUG: Media links data", 
                           media_count=len(media_data),
                           media_data=media_data)
            
            # Analyze source data
            if 'source' in raw_item:
                source_data = raw_item['source']
                logger.info("DEBUG: Source data", 
                           source_name=source_data.get('source_name', 'No source'),
                           source_data=source_data)
            
            return item
            
        except Exception as e:
            error_msg = f"Debug pipeline error: {str(e)}"
            logger.error("DEBUG: Pipeline error", error=error_msg, item=dict(item))
            self.debug_data['errors'].append({
                'spider': spider.name,
                'error': error_msg,
                'item': dict(item)
            })
            raise DropItem(error_msg)
    
    def close_spider(self, spider):
        """Called when spider closes"""
        logger.info("DEBUG: Pipeline closed", 
                   spider=spider.name,
                   items_processed=self.debug_data['items_processed'],
                   errors_count=len(self.debug_data['errors']))
        
        # Print debug summary
        print("\n" + "="*50)
        print("DEBUG PIPELINE SUMMARY")
        print("="*50)
        print(f"Spider: {spider.name}")
        print(f"Items processed: {self.debug_data['items_processed']}")
        print(f"Errors: {len(self.debug_data['errors'])}")
        
        if self.debug_data['errors']:
            print("\nErrors encountered:")
            for error in self.debug_data['errors']:
                print(f"  - {error['error']}")
        
        print("="*50)
