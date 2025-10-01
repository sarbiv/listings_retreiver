"""
Pydantic schemas for luxury development scraper
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime
import re

class ProjectIn(BaseModel):
    """Input schema for project data"""
    name: str
    developer_name: Optional[str] = None
    brand_flag: Optional[str] = None
    property_type: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    est_completion: Optional[str] = None
    website_url: Optional[str] = None
    inquiry_url: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()
    
    @validator('contact_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            return None  # Invalid email, return None instead of raising
        return v

class UnitIn(BaseModel):
    """Input schema for unit data"""
    unit_name: Optional[str] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    size_sqft: Optional[float] = None
    size_sqm: Optional[float] = None
    price_local_value: Optional[float] = None
    price_local_currency: Optional[str] = None
    price_note: Optional[str] = None
    floor: Optional[str] = None
    exposure: Optional[str] = None
    maintenance_fees: Optional[str] = None
    tax_note: Optional[str] = None
    availability_status: Optional[str] = None
    floorplan_url: Optional[str] = None
    vr_url: Optional[str] = None
    brochure_url: Optional[str] = None
    
    @validator('bedrooms', 'bathrooms', 'size_sqft', 'size_sqm', 'price_local_value')
    def validate_numeric_fields(cls, v):
        if v is not None and v < 0:
            return None  # Invalid negative value
        return v

class AmenityIn(BaseModel):
    """Input schema for amenity data"""
    amenity: str
    
    @validator('amenity')
    def amenity_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Amenity cannot be empty')
        return v.strip()

class MediaLinkIn(BaseModel):
    """Input schema for media link data"""
    type: str  # "image", "render", "video", "vr"
    url: str
    caption: Optional[str] = None
    
    @validator('type')
    def validate_media_type(cls, v):
        valid_types = ['image', 'render', 'video', 'vr', 'brochure', 'floorplan']
        if v.lower() not in valid_types:
            return 'image'  # Default to image if invalid
        return v.lower()
    
    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        return v.strip()

class SourceIn(BaseModel):
    """Input schema for source data"""
    source_name: str
    source_url: str
    robots_ok: bool = True
    tos_ok: bool = True
    
    @validator('source_name', 'source_url')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Source name and URL cannot be empty')
        return v.strip()

class CleanedProject(BaseModel):
    """Cleaned project data with computed fields"""
    name: str
    developer_name: Optional[str] = None
    brand_flag: Optional[str] = None
    property_type: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    est_completion: Optional[str] = None
    website_url: Optional[str] = None
    inquiry_url: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    completeness_score: Optional[float] = None
    
    def compute_completeness_score(self) -> float:
        """Compute completeness score (0-1)"""
        score = 0.0
        max_score = 10.0
        
        # Essential fields (higher weight)
        if self.name:
            score += 2.0
        if self.city:
            score += 1.0
        if self.country:
            score += 1.0
        if self.website_url:
            score += 1.0
        
        # Important fields
        if self.developer_name:
            score += 0.5
        if self.address:
            score += 0.5
        if self.description:
            score += 0.5
        if self.contact_email or self.inquiry_url:
            score += 0.5
        if self.est_completion:
            score += 0.5
        if self.status:
            score += 0.5
        
        # Bonus for having media/units (indicates rich data)
        # This would be computed at the project level with units/media
        return min(score / max_score, 1.0)

class CleanedUnit(BaseModel):
    """Cleaned unit data"""
    unit_name: Optional[str] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    size_sqft: Optional[float] = None
    size_sqm: Optional[float] = None
    price_local_value: Optional[float] = None
    price_local_currency: Optional[str] = None
    price_note: Optional[str] = None
    floor: Optional[str] = None
    exposure: Optional[str] = None
    maintenance_fees: Optional[str] = None
    tax_note: Optional[str] = None
    availability_status: Optional[str] = None
    floorplan_url: Optional[str] = None
    vr_url: Optional[str] = None
    brochure_url: Optional[str] = None
    size_computed: bool = False  # Flag if size was computed from conversion
    
    def compute_size_conversion(self):
        """Compute missing size field if possible"""
        if self.size_sqft and not self.size_sqm:
            self.size_sqm = self.size_sqft / 10.7639
            self.size_computed = True
        elif self.size_sqm and not self.size_sqft:
            self.size_sqft = self.size_sqm * 10.7639
            self.size_computed = True
