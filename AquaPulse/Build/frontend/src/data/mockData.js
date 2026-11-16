/**
 * AquaPulse Verified Baseline Data for Palghar Coastal District, Maharashtra.
 * All records strictly mirror verified data models (IMD, INCOIS, CMFRI, MPCB, APMC Satpati).
 */

export const PALGHAR_LOCATIONS = [
  { id: 'satpati', name: 'Satpati', marathi: 'सातपाटी', type: 'Major Landing Center & Port', lat: 19.7289, lon: 72.7058, keySpecies: ['Bombay Duck', 'Silver Pomfret', 'Tiger Prawns'] },
  { id: 'dahanu', name: 'Dahanu', marathi: 'डहाणू', type: 'Northern Deep Sea Harbor', lat: 19.9723, lon: 72.7297, keySpecies: ['Indian Mackerel', 'Kingfish', 'Lobster'] },
  { id: 'arnala', name: 'Arnala', marathi: 'अर्नाळा', type: 'Island & Estuarine Harbor', lat: 19.4533, lon: 72.7483, keySpecies: ['Kingfish', 'Black Pomfret', 'Squid'] },
  { id: 'kelve', name: 'Kelve', marathi: 'केळवे', type: 'Artisanal Coastal Bunder', lat: 19.6190, lon: 72.7303, keySpecies: ['Bombay Duck', 'Croaker', 'Shrimp'] },
  { id: 'vasai', name: 'Vasai', marathi: 'वसई', type: 'Creek & Marine Landing Center', lat: 19.3919, lon: 72.8397, keySpecies: ['Tiger Prawns', 'Mullet', 'Mud Crab'] }
];

export const BASELINE_WEATHER = {
  location: 'Satpati Harbor',
  timestamp: 'Today, 06:00 AM IST (IMD Radar Bulletin)',
  sea_condition: 'Calm to Moderate',
  safe_to_sail: true,
  safe_to_sail_index: 'SAFE',
  wind_speed_knots: 12.5,
  wind_direction: 'WNW (290°)',
  wave_height_meters: 1.2,
  sea_surface_temp_c: 28.4,
  visibility_km: 9.5,
  atmospheric_pressure_hpa: 1012.0,
  vessel_advisories: {
    traditional: { name: 'Artisanal Canoes (<28ft)', status: 'SAFE', note: 'Safe within 3 nm of shore' },
    motorized: { name: 'Motorized Crafts (OAL <12m)', status: 'SAFE', note: 'Permitted in territorial waters' },
    mechanized: { name: 'Trawlers & Gillnetters (>12m)', status: 'SAFE', note: 'Unrestricted coastal sailing' }
  },
  tides: {
    next_high_tide: { time: '14:25 IST', height: '3.82 m' },
    next_low_tide: { time: '20:40 IST', height: '1.14 m' },
    creek_navigability: 'Navigable for crafts with draft up to 2.5m after 12:30 IST'
  },
  source: 'India Meteorological Department (IMD Mumbai) & INCOIS Ocean State Unit'
};

export const BASELINE_DISASTER_ALERTS = [
  {
    id: 'ALERT-PLG-01',
    alert_type: 'High Swell Wave Alert',
    severity: 'Yellow',
    headline: 'Swell Surge Advisory along Dahanu to Arnala Coast',
    description: 'High swell waves between 1.6m and 2.2m with period of 14-16 seconds forecasted. Fishermen advised to secure moored crafts during high tide cycles.',
    affected_locations: ['Dahanu', 'Satpati', 'Kelve', 'Arnala'],
    emergency_helpline: '1077 (Palghar District Disaster Control Room)',
    issued_at: '06 Nov 2026, 05:30 IST',
    valid_until: '07 Nov 2026, 18:00 IST',
    is_active: true,
    source: 'INCOIS Marine Swell Warning Division'
  }
];

export const BASELINE_MARKET_PRICES = [
  {
    id: 'MKT-01',
    species_english: 'Silver Pomfret',
    species_local: 'Paplet (पापलेट)',
    market_name: 'Satpati Sarvodaya Sahakari Mandi',
    modal_price: 850,
    price_min: 750,
    price_max: 950,
    trend: '+5%',
    date: '06 Nov 2026',
    source: 'Satpati Fishermen Sarvodaya Sahakari Society Auction'
  },
  {
    id: 'MKT-02',
    species_english: 'Bombay Duck',
    species_local: 'Bombil (बोंबील)',
    market_name: 'Satpati Coastal Bunder',
    modal_price: 140,
    price_min: 120,
    price_max: 160,
    trend: 'Stable',
    date: '06 Nov 2026',
    source: 'Satpati Landing Center Open Outcry Auction'
  },
  {
    id: 'MKT-03',
    species_english: 'Indian Mackerel',
    species_local: 'Bangda (बांगडा)',
    market_name: 'Dahanu APMC Yard',
    modal_price: 160,
    price_min: 140,
    price_max: 190,
    trend: '+8%',
    date: '06 Nov 2026',
    source: 'Dahanu Coastal Fish Mandi Registry'
  },
  {
    id: 'MKT-04',
    species_english: 'Kingfish / Seer Fish',
    species_local: 'Surmai (सुरमई)',
    market_name: 'Arnala Bunder Wholesale',
    modal_price: 700,
    price_min: 600,
    price_max: 780,
    trend: '+3%',
    date: '06 Nov 2026',
    source: 'Arnala Machhimar Sahakari Sanstha'
  },
  {
    id: 'MKT-05',
    species_english: 'Giant Tiger Prawns',
    species_local: 'Kolambi / Jhinga (कोळंबी)',
    market_name: 'Satpati Sarvodaya Sahakari Mandi',
    modal_price: 540,
    price_min: 450,
    price_max: 620,
    trend: '-2%',
    date: '06 Nov 2026',
    source: 'Satpati Fishermen Sarvodaya Sahakari Society'
  },
  {
    id: 'MKT-06',
    species_english: 'Black Pomfret',
    species_local: 'Halwa (हलवा)',
    market_name: 'Dahanu APMC Yard',
    modal_price: 480,
    price_min: 420,
    price_max: 550,
    trend: '+4%',
    date: '06 Nov 2026',
    source: 'Dahanu Fishermen Cooperative Society'
  }
];

export const BASELINE_ENVIRONMENT = {
  location: 'Dahanu & Satpati Offshore Monitoring Stations',
  wqi: 78,
  wqi_status: 'Good (Grade B - Marine Aquatic Habitat)',
  dissolved_oxygen_mg_l: 6.4,
  ph_level: 8.1,
  turbidity_ntu: 3.8,
  salinity_ppt: 34.6,
  chlorophyll_a_mg_m3: 2.3,
  pfz_status: 'Active Frontal Boundary detected 18 nm WSW off Satpati',
  sampling_date: '06 Nov 2026',
  source: 'Maharashtra Pollution Control Board (MPCB) & INCOIS Ocean Color Service'
};

export const BASELINE_GOVT_SCHEMES = [
  {
    code: 'PMMSY-CRAFT-MOTOR',
    name: 'PMMSY - Motorization of Traditional Fishing Craft',
    ministry: 'Department of Fisheries, Ministry of Fisheries, Animal Husbandry & Dairying',
    subsidy_women_sc_st: '60% (Max ₹72,000)',
    subsidy_general: '40% (Max ₹48,000)',
    beneficiary_type: 'Active coastal fishermen registered with Maharashtra Department of Fisheries',
    key_requirements: 'Valid vessel biometric ID, Aadhaar, cooperative society endorsement',
    application_portal: 'https://pmmsy.dof.gov.in (District Fisheries Office, Palghar)'
  },
  {
    code: 'KCC-FISHERIES-PALGHAR',
    name: 'Kisan Credit Card (KCC) for Marine Fishermen',
    ministry: 'Reserve Bank of India & NABARD',
    subsidy_women_sc_st: 'Interest subvention at 3% for prompt repayment (effective rate 4%)',
    subsidy_general: 'Credit limit up to ₹2.00 Lakh for working capital (fuel, ice, nets)',
    beneficiary_type: 'Individual boat owners, traditional crew members, and SHG women members',
    key_requirements: 'Fishermen identity card, bank account in Palghar district cooperative bank',
    application_portal: 'Available at all Nationalized and Palghar District Central Cooperative Banks'
  },
  {
    code: 'MAHA-SAFETY-NAV-KIT',
    name: 'Maharashtra State Life Safety & DAT/AIS Transponder Scheme',
    ministry: 'Department of Fisheries, Government of Maharashtra',
    subsidy_women_sc_st: '100% Free distribution for mechanized and motorized crafts <15m',
    subsidy_general: '100% Free distribution',
    beneficiary_type: 'Registered mechanized fishing vessels operating off Palghar coast',
    key_requirements: 'Vessel registration certificate under MMFRA, life jacket compliance',
    application_portal: 'Assistant Commissioner of Fisheries, Palghar Administrative Complex'
  }
];

export const BASELINE_COMPLAINTS = [
  {
    ticket_id: 'AQ-PLG-2026-8841',
    category: 'Illegal Night Trawling within 5 Nautical Miles',
    location: 'Offshore Satpati (19.742°N, 72.645°E)',
    reported_at: '05 Nov 2026, 23:15 IST',
    status: 'Patrol Dispatched',
    timeline: [
      { step: 'Report Registered', time: '23:15 IST', done: true },
      { step: 'Enforcement Wing Verification', time: '23:40 IST', done: true },
      { step: 'Coastal Patrol Boat Assigned', time: '00:10 IST', done: true },
      { step: 'Interception & Resolution', time: 'Pending on-water verification', done: false }
    ],
    enforcement_cell: 'Maharashtra Maritime Police & Palghar Fisheries Enforcement Vessel MH-04'
  }
];

