"""
Database models for luxury development scraper
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    developer_name = Column(String(255))
    brand_flag = Column(String(255))  # e.g., "Waldorf Astoria", "Six Senses"
    property_type = Column(String(100))  # "Residential", "Mixed-Use"
    status = Column(String(50))  # "planned", "under_construction", "completed", "unknown"
    country = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    est_completion = Column(String(100))  # "Q4 2025", "2027"
    website_url = Column(String(500))
    inquiry_url = Column(String(500))
    contact_email = Column(String(255))
    description = Column(Text)
    completeness_score = Column(Float)  # 0-1 score
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    units = relationship("Unit", back_populates="project", cascade="all, delete-orphan")
    amenities = relationship("Amenity", back_populates="project", cascade="all, delete-orphan")
    media_links = relationship("MediaLink", back_populates="project", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")

class Unit(Base):
    __tablename__ = 'units'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    unit_name = Column(String(255))  # "Residence 03B"
    bedrooms = Column(Float)  # allow "studio" as 0
    bathrooms = Column(Float)
    size_sqft = Column(Float)
    size_sqm = Column(Float)
    price_local_value = Column(Float)
    price_local_currency = Column(String(10))  # "AED", "GBP", "USD", "₪", "SGD"
    price_note = Column(String(255))  # "From", "Price on request"
    floor = Column(String(50))
    exposure = Column(String(100))
    maintenance_fees = Column(String(255))
    tax_note = Column(String(255))
    availability_status = Column(String(50))  # "available", "reserved", "sold", "unknown"
    floorplan_url = Column(String(500))
    vr_url = Column(String(500))
    brochure_url = Column(String(500))
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="units")

class Amenity(Base):
    __tablename__ = 'amenities'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    amenity = Column(String(255), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="amenities")

class MediaLink(Base):
    __tablename__ = 'media_links'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    type = Column(String(50), nullable=False)  # "image", "render", "video", "vr"
    url = Column(String(500), nullable=False)
    caption = Column(String(500))
    
    # Relationships
    project = relationship("Project", back_populates="media_links")

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    source_name = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=False)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    robots_ok = Column(Boolean, default=True)
    tos_ok = Column(Boolean, default=True)
    
    # Relationships
    project = relationship("Project", back_populates="sources")

def get_engine(database_url=None):
    """Get SQLAlchemy engine"""
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///data/luxury_developments.db')
    return create_engine(database_url)

def get_session(database_url=None):
    """Get SQLAlchemy session"""
    engine = get_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()

def init_db(database_url=None):
    """Initialize database tables"""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return engine
