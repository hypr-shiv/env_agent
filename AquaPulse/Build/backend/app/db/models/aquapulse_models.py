import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Float, Boolean, DateTime, Integer, JSON, ForeignKey, Enum as SQLEnum
)
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class CoastalLocation(Base):
    __tablename__ = "coastal_locations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, index=True) # e.g. Satpati, Dahanu, Arnala
    type = Column(String(50), default="landing_center") # landing_center, port, beach, taluka
    district = Column(String(50), default="Palghar", index=True)
    state = Column(String(50), default="Maharashtra")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

class MarineWeatherRecord(Base):
    __tablename__ = "marine_weather_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    location_name = Column(String(100), nullable=False, index=True)
    observation_time = Column(DateTime, default=get_utc_now, index=True)
    wind_speed_knots = Column(Float, nullable=False)
    wind_direction = Column(String(20), nullable=True)
    wave_height_meters = Column(Float, nullable=False)
    sea_surface_temp_c = Column(Float, nullable=True)
    visibility_km = Column(Float, nullable=True)
    sea_condition = Column(String(50), nullable=False) # Calm, Moderate, Rough, Very Rough
    safe_to_sail = Column(Boolean, default=True)
    data_mode = Column(String(20), default="live") # live, historical, mock, synthetic
    source = Column(String(100), default="Open-Meteo Marine / IMD")
    created_at = Column(DateTime, default=get_utc_now)

class DisasterAlertRecord(Base):
    __tablename__ = "disaster_alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    alert_type = Column(String(50), nullable=False) # Cyclone, High Swell, Tsunami, Storm Surge
    severity = Column(String(20), nullable=False) # Red, Orange, Yellow, Green
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    affected_locations = Column(JSON, default=list) # ["Dahanu", "Satpati", "Vasai"]
    emergency_helpline = Column(String(50), default="1077 (Palghar District Control)")
    issued_at = Column(DateTime, default=get_utc_now)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    source = Column(String(100), default="INCOIS / IMD")

class FishMarketPriceRecord(Base):
    __tablename__ = "fish_market_prices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    market_name = Column(String(100), nullable=False, index=True) # Satpati, Arnala, Dahanu
    species_english = Column(String(100), nullable=False, index=True) # Bombay Duck, Pomfret
    species_local = Column(String(100), nullable=True) # Bombil, Paplet, Surmai
    price_min_per_kg = Column(Float, nullable=False)
    price_max_per_kg = Column(Float, nullable=False)
    modal_price_per_kg = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    price_date = Column(DateTime, default=get_utc_now, index=True)
    data_mode = Column(String(20), default="live")
    source = Column(String(100), default="Palghar Fishermen Cooperative / APMC")

class CoastalEnvironmentRecord(Base):
    __tablename__ = "coastal_environment"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    station_name = Column(String(100), nullable=False, index=True)
    sst_celsius = Column(Float, nullable=False)
    chlorophyll_a_mg_m3 = Column(Float, nullable=True)
    dissolved_oxygen_mg_l = Column(Float, nullable=True)
    salinity_ppt = Column(Float, nullable=True)
    water_quality_status = Column(String(50), default="Good") # Good, Moderate, Degraded
    algal_bloom_risk = Column(String(20), default="Low") # Low, Medium, High
    observation_time = Column(DateTime, default=get_utc_now)
    data_mode = Column(String(20), default="live")
    source = Column(String(100), default="INCOIS / MPCB")

class GovtFisheryScheme(Base):
    __tablename__ = "govt_fishery_schemes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scheme_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    department = Column(String(100), default="Dept of Fisheries, Maharashtra / GoI")
    category = Column(String(100), nullable=False) # Mechanization, Safety, Welfare, Aquaculture
    subsidy_details = Column(Text, nullable=False)
    eligibility_criteria = Column(Text, nullable=False)
    required_documents = Column(JSON, default=list)
    application_portal = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

class PublicComplaint(Base):
    __tablename__ = "public_complaints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False) # Illegal Trawling, Marine Pollution, Port Issue
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location_name = Column(String(100), nullable=False)
    status = Column(String(30), default="submitted") # submitted, under_investigation, resolved, rejected
    evidence_image_url = Column(String(255), nullable=True)
    submitted_by = Column(String(100), default="Anonymous Fisherman")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now)

class AgentAuditLog(Base):
    __tablename__ = "agent_audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(100), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    routed_agents = Column(JSON, default=list) # ["weather", "fisheries"]
    intent = Column(String(100), nullable=True)
    response_summary = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

