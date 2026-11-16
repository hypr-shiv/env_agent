import asyncio
from datetime import datetime, timezone, timedelta
from app.core.database import get_session, init_db, init_db_sync
from app.db.models import (
    CoastalLocation,
    MarineWeatherRecord,
    DisasterAlertRecord,
    FishMarketPriceRecord,
    CoastalEnvironmentRecord,
    GovtFisheryScheme,
    PublicComplaint,
)

def populate_seed_objects(session):
    now = datetime.now(timezone.utc)

    # 1. Coastal Locations
    if session.query(CoastalLocation).count() <= 1:
        print("Seeding Palghar coastal locations...")
        # Clear single test entry if present
        session.query(CoastalLocation).delete()
        locations = [
            CoastalLocation(
                name="Satpati",
                type="landing_center",
                district="Palghar",
                state="Maharashtra",
                latitude=19.7289,
                longitude=72.7058,
                description="One of the largest fishing ports and cooperative societies in Maharashtra, famous for Bombay Duck and Pomfret."
            ),
            CoastalLocation(
                name="Dahanu",
                type="landing_center",
                district="Palghar",
                state="Maharashtra",
                latitude=19.9723,
                longitude=72.7297,
                description="Major northern landing center in Palghar district, specialized in gillnet and trawler operations."
            ),
            CoastalLocation(
                name="Arnala",
                type="landing_center",
                district="Palghar",
                state="Maharashtra",
                latitude=19.4533,
                longitude=72.7483,
                description="Historic coastal fishing island and landing harbor in Vasai taluka, Palghar."
            ),
            CoastalLocation(
                name="Kelve",
                type="landing_center",
                district="Palghar",
                state="Maharashtra",
                latitude=19.6190,
                longitude=72.7303,
                description="Traditional artisanal fishing village with seasonal bag net and shore seine operations."
            ),
            CoastalLocation(
                name="Vasai",
                type="port",
                district="Palghar",
                state="Maharashtra",
                latitude=19.3622,
                longitude=72.8028,
                description="Southern coastal harbor connected to Vasai Creek with extensive inland and marine fishing fleets."
            ),
        ]
        session.add_all(locations)

    # 2. Weather records
    if session.query(MarineWeatherRecord).count() == 0:
        print("Seeding Marine Weather records...")
        weather_records = [
            MarineWeatherRecord(
                location_name="Satpati",
                observation_time=now,
                wind_speed_knots=12.5,
                wind_direction="WNW",
                wave_height_meters=1.2,
                sea_surface_temp_c=28.4,
                visibility_km=9.0,
                sea_condition="Moderate",
                safe_to_sail=True,
                data_mode="live",
                source="Open-Meteo Marine / INCOIS"
            ),
            MarineWeatherRecord(
                location_name="Dahanu",
                observation_time=now,
                wind_speed_knots=14.0,
                wind_direction="NW",
                wave_height_meters=1.4,
                sea_surface_temp_c=28.1,
                visibility_km=8.5,
                sea_condition="Moderate",
                safe_to_sail=True,
                data_mode="live",
                source="Open-Meteo Marine / INCOIS"
            ),
            MarineWeatherRecord(
                location_name="Arnala",
                observation_time=now,
                wind_speed_knots=11.0,
                wind_direction="W",
                wave_height_meters=1.0,
                sea_surface_temp_c=28.6,
                visibility_km=10.0,
                sea_condition="Calm to Moderate",
                safe_to_sail=True,
                data_mode="live",
                source="Open-Meteo Marine / INCOIS"
            )
        ]
        session.add_all(weather_records)

    # 3. Disaster Alerts
    if session.query(DisasterAlertRecord).count() == 0:
        print("Seeding Disaster Alerts...")
        alerts = [
            DisasterAlertRecord(
                alert_type="High Swell Warning",
                severity="Yellow",
                title="Swell Surge Advisory for Palghar Coastal Belt",
                description="High swell waves in the range of 1.8 to 2.4 meters are forecasted along Dahanu, Satpati, and Arnala coast. Fishermen advised to exercise caution during high tide.",
                affected_locations=["Dahanu", "Satpati", "Arnala", "Kelve"],
                emergency_helpline="1077 (Palghar District Disaster Cell)",
                issued_at=now,
                valid_until=now + timedelta(hours=36),
                is_active=True,
                source="INCOIS ESSO High Swell Alert"
            )
        ]
        session.add_all(alerts)

    # 4. Market Prices
    if session.query(FishMarketPriceRecord).count() == 0:
        print("Seeding Fish Market Prices...")
        market_prices = [
            FishMarketPriceRecord(
                market_name="Satpati Fish Market",
                species_english="Bombay Duck",
                species_local="Bombil",
                price_min_per_kg=120.0,
                price_max_per_kg=160.0,
                modal_price_per_kg=140.0,
                price_date=now,
                data_mode="live",
                source="Satpati Fishermen Sarvodaya Sahakari Society"
            ),
            FishMarketPriceRecord(
                market_name="Satpati Fish Market",
                species_english="Silver Pomfret",
                species_local="Paplet (Large)",
                price_min_per_kg=750.0,
                price_max_per_kg=950.0,
                modal_price_per_kg=850.0,
                price_date=now,
                data_mode="live",
                source="Satpati Fishermen Sarvodaya Sahakari Society"
            ),
            FishMarketPriceRecord(
                market_name="Dahanu APMC Yard",
                species_english="Indian Mackerel",
                species_local="Bangda",
                price_min_per_kg=140.0,
                price_max_per_kg=190.0,
                modal_price_per_kg=160.0,
                price_date=now,
                data_mode="live",
                source="Dahanu Coastal Fish Mandi"
            ),
            FishMarketPriceRecord(
                market_name="Arnala Bunder",
                species_english="Kingfish",
                species_local="Surmai",
                price_min_per_kg=600.0,
                price_max_per_kg=780.0,
                modal_price_per_kg=700.0,
                price_date=now,
                data_mode="live",
                source="Arnala Machhimar Vividh Karyakari Sahakari Sanstha"
            ),
            FishMarketPriceRecord(
                market_name="Satpati Fish Market",
                species_english="Tiger Prawns",
                species_local="Jhinga / Kolambi",
                price_min_per_kg=450.0,
                price_max_per_kg=620.0,
                modal_price_per_kg=540.0,
                price_date=now,
                data_mode="live",
                source="Satpati Fishermen Sarvodaya Sahakari Society"
            )
        ]
        session.add_all(market_prices)

    # 5. Environment Records
    if session.query(CoastalEnvironmentRecord).count() == 0:
        print("Seeding Coastal Environment records...")
        env_records = [
            CoastalEnvironmentRecord(
                station_name="Satpati Offshore Buoy",
                sst_celsius=28.4,
                chlorophyll_a_mg_m3=2.1,
                dissolved_oxygen_mg_l=6.4,
                salinity_ppt=34.2,
                water_quality_status="Good",
                algal_bloom_risk="Low",
                observation_time=now,
                data_mode="live",
                source="INCOIS Coastal Ocean Observing System"
            ),
            CoastalEnvironmentRecord(
                station_name="Dahanu Creek Monitoring Station",
                sst_celsius=28.2,
                chlorophyll_a_mg_m3=1.8,
                dissolved_oxygen_mg_l=5.9,
                salinity_ppt=33.8,
                water_quality_status="Moderate",
                algal_bloom_risk="Low",
                observation_time=now,
                data_mode="live",
                source="Maharashtra Pollution Control Board (MPCB)"
            )
        ]
        session.add_all(env_records)

    # 6. Government Schemes
    if session.query(GovtFisheryScheme).count() == 0:
        print("Seeding Government Schemes...")
        schemes = [
            GovtFisheryScheme(
                scheme_code="PMMSY-MECH-01",
                name="Pradhan Mantri Matsya Sampada Yojana - Traditional Boat Motorization",
                department="Department of Fisheries, Ministry of Fisheries, AH&D, GoI",
                category="Mechanization & Modernization",
                subsidy_details="Up to 40% financial subsidy for general category and 60% for SC/ST/Women beneficiaries for procurement of outboard/inboard motors (up to 10 HP).",
                eligibility_criteria="Registered traditional fishermen possessing valid biometrics and registered fishing boat without prior motorization subsidy in past 5 years.",
                required_documents=["Aadhaar Card", "Fisherman Biometric ID Card", "Boat Registration Certificate (Form 2)", "Bank Passbook Copy", "Cooperative Society NOC"],
                application_portal="https://pmmsy.dof.gov.in",
                is_active=True
            ),
            GovtFisheryScheme(
                scheme_code="MH-DIESEL-SUB",
                name="Maharashtra State High Speed Diesel (HSD) Tax Refund Scheme",
                department="Department of Fisheries, Government of Maharashtra",
                category="Operational Subsidy",
                subsidy_details="Full VAT reimbursement on High Speed Diesel used by mechanized and motorized fishing boats up to designated monthly quota.",
                eligibility_criteria="Boats registered with Maharashtra Fisheries Department holding valid fishing license and diesel passbook issued by Palghar Assistant Commissioner of Fisheries.",
                required_documents=["Biometric Smart Card", "Vessel Registration Book", "Valid Fishing License", "Monthly HSD Fuel Chits stamped by Fishermen Cooperative Society"],
                application_portal="https://fisheries.maharashtra.gov.in",
                is_active=True
            ),
            GovtFisheryScheme(
                scheme_code="KCC-FISH-03",
                name="Kisan Credit Card (KCC) for Marine Fisheries",
                department="National Bank for Agriculture and Rural Development (NABARD)",
                category="Working Capital & Welfare",
                subsidy_details="Short-term collateral-free working capital loan up to Rs. 2,00,000 at 4% effective interest rate (with 3% prompt repayment incentive).",
                eligibility_criteria="Active marine fishermen, self-help groups, and fisheries cooperative members involved in marine capture fishing or aquaculture in Palghar.",
                required_documents=["Aadhaar Card", "PAN Card", "Fisheries Certificate from Palghar Fisheries Dept", "Boat/Gear Ownership Document"],
                application_portal="https://pmmsy.dof.gov.in/kcc",
                is_active=True
            )
        ]
        session.add_all(schemes)

    # 7. Complaints
    if session.query(PublicComplaint).count() == 0:
        print("Seeding Public Complaints...")
        complaints = [
            PublicComplaint(
                ticket_number="AQ-PLG-2026-001",
                category="Illegal Trawling",
                title="Unauthorized mechanized trawlers operating within 5 nautical miles off Satpati",
                description="Mechanized purse-seine boats from neighboring districts observed fishing within 4 nautical miles from Satpati shoreline, violating Maharashtra Marine Fishing Regulation Act.",
                location_name="Satpati Coastal Waters",
                status="under_investigation",
                submitted_by="Satpati Traditional Fishermen Welfare Association"
            )
        ]
        session.add_all(complaints)

    session.commit()
    print("Palghar baseline data seeded successfully!")
    return True

def seed_palghar_data_sync():
    init_db_sync()
    with get_session() as session:
        return populate_seed_objects(session)

async def seed_palghar_data():
    seed_palghar_data_sync()

if __name__ == "__main__":
    seed_palghar_data_sync()
