-- SQLite schema for luxury development scraper
-- This file is for reference; actual tables are created via SQLAlchemy models

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    developer_name TEXT,
    brand_flag TEXT,
    property_type TEXT,
    status TEXT,
    country TEXT,
    city TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    est_completion TEXT,
    website_url TEXT,
    inquiry_url TEXT,
    contact_email TEXT,
    description TEXT,
    completeness_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    unit_name TEXT,
    bedrooms REAL,
    bathrooms REAL,
    size_sqft REAL,
    size_sqm REAL,
    price_local_value REAL,
    price_local_currency TEXT,
    price_note TEXT,
    floor TEXT,
    exposure TEXT,
    maintenance_fees TEXT,
    tax_note TEXT,
    availability_status TEXT,
    floorplan_url TEXT,
    vr_url TEXT,
    brochure_url TEXT,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

CREATE TABLE IF NOT EXISTS amenities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    amenity TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

CREATE TABLE IF NOT EXISTS media_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    url TEXT NOT NULL,
    caption TEXT,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    robots_ok INTEGER DEFAULT 1,
    tos_ok INTEGER DEFAULT 1,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects (name);
CREATE INDEX IF NOT EXISTS idx_projects_city_country ON projects (city, country);
CREATE INDEX IF NOT EXISTS idx_projects_website_url ON projects (website_url);
CREATE INDEX IF NOT EXISTS idx_units_project_id ON units (project_id);
CREATE INDEX IF NOT EXISTS idx_amenities_project_id ON amenities (project_id);
CREATE INDEX IF NOT EXISTS idx_media_links_project_id ON media_links (project_id);
CREATE INDEX IF NOT EXISTS idx_sources_project_id ON sources (project_id);
