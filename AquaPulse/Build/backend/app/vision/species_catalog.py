"""
AquaPulse Palghar Marine Fish Species Catalog.
Contains verified biological taxonomy, habitat, seasonal patterns, and landing distributions
sourced from ICAR-CMFRI and the Maharashtra Department of Fisheries.
"""

from typing import Dict, Any, List

VISION_SPECIES_CLASSES: List[str] = [
    "Silver Pomfret",
    "Bombay Duck",
    "Indian Mackerel",
    "Kingfish",
    "Black Pomfret",
    "Tiger Prawns",
    "Catfish",
    "Ribbonfish"
]

SPECIES_BIOLOGY_DATA: Dict[str, Dict[str, Any]] = {
    "Silver Pomfret": {
        "scientific_name": "Pampus argenteus",
        "local_name": "Paplet / Saranga (पापलेट)",
        "habitat": "Coastal pelagic and sub-surface continental shelf waters (15-55m depth) with sandy-muddy substrate.",
        "seasonal_information": {
            "peak_season": "September to February",
            "lean_season": "May to July",
            "spawning_period": "October to December",
            "monsoon_ban_compliance": "Fishing prohibited during annual Maharashtra Marine Fishing Regulation ban (June 1 - July 31)."
        },
        "local_distribution": ["Satpati", "Dahanu", "Arnala", "Kelve", "Vasai"],
        "minimum_legal_size": "15 cm (150 grams)",
        "gear": "Surface drift gillnet (Vavdi/Phanda)",
        "commercial_tier": "Prime Export Grade"
    },
    "Bombay Duck": {
        "scientific_name": "Harpadon nehereus",
        "local_name": "Bombil (बोंबील)",
        "habitat": "Inshore shallow coastal waters, estuaries, and muddy tidal flats (10-30m depth) influenced by strong tidal currents.",
        "seasonal_information": {
            "peak_season": "October to May",
            "lean_season": "June to August",
            "spawning_period": "December to March",
            "monsoon_ban_compliance": "Traditional non-motorized craft exempt near shore; mechanized dol-net ban enforced June 1 - July 31."
        },
        "local_distribution": ["Satpati", "Dahanu", "Arnala", "Kelve"],
        "minimum_legal_size": "18 cm total length",
        "gear": "Fixed coastal Bag Net (Dol Net)",
        "commercial_tier": "Staple Domestic Catch"
    },
    "Indian Mackerel": {
        "scientific_name": "Rastrelliger kanagurta",
        "local_name": "Bangda (बांगडा)",
        "habitat": "Coastal surface pelagic waters (10-40m depth) schooling near phytoplankton blooms.",
        "seasonal_information": {
            "peak_season": "October to March",
            "lean_season": "May to July",
            "spawning_period": "June to August",
            "monsoon_ban_compliance": "Offshore pelagic operations suspended during monsoon ban."
        },
        "local_distribution": ["Satpati", "Dahanu", "Arnala", "Vasai"],
        "minimum_legal_size": "14 cm total length",
        "gear": "Gillnet, Dol net, and traditional ring-seine",
        "commercial_tier": "High Volume Table Fish"
    },
    "Kingfish": {
        "scientific_name": "Scomberomorus commerson",
        "local_name": "Surmai (सुरमई)",
        "habitat": "Offshore clear pelagic waters, reefs, and outer continental shelf (20-70m depth).",
        "seasonal_information": {
            "peak_season": "September to December",
            "lean_season": "April to July",
            "spawning_period": "May to July",
            "monsoon_ban_compliance": "Strict offshore ban observed June 1 to July 31."
        },
        "local_distribution": ["Satpati", "Dahanu", "Arnala"],
        "minimum_legal_size": "37 cm total length",
        "gear": "Large-mesh surface drift gillnet and trolling lines",
        "commercial_tier": "Premium Table Fish & Export"
    },
    "Black Pomfret": {
        "scientific_name": "Parastromateus niger",
        "local_name": "Halwa (हलवा)",
        "habitat": "Coastal pelagic waters (15-60m depth) above soft muddy bottom.",
        "seasonal_information": {
            "peak_season": "September to March",
            "lean_season": "May to July",
            "spawning_period": "July to October",
            "monsoon_ban_compliance": "Mechanized operations banned June 1 - July 31."
        },
        "local_distribution": ["Satpati", "Dahanu", "Arnala", "Kelve"],
        "minimum_legal_size": "17 cm total length",
        "gear": "Drift gillnet and trawl net",
        "commercial_tier": "High Value Catch"
    },
    "Tiger Prawns": {
        "scientific_name": "Penaeus monodon",
        "local_name": "Kolambi / Jhinga (कोळंबी)",
        "habitat": "Benthic coastal muddy bottoms, mangrove creeks, and shallow brackish estuaries.",
        "seasonal_information": {
            "peak_season": "August to November, March to May",
            "lean_season": "June to July",
            "spawning_period": "Year-round with peak in post-monsoon",
            "monsoon_ban_compliance": "Trawler ban enforced June 1 - July 31 to protect broodstock."
        },
        "local_distribution": ["Satpati", "Dahanu", "Vasai", "Kelve"],
        "minimum_legal_size": "10 cm carapace length",
        "gear": "Bottom trawl and coastal stake net",
        "commercial_tier": "Premium Export Crustacean"
    },
    "Catfish": {
        "scientific_name": "Arius dussumieri",
        "local_name": "Shingala (शिंगाळा)",
        "habitat": "Demersal muddy and sandy sea beds in inshore coastal waters (10-45m depth).",
        "seasonal_information": {
            "peak_season": "November to April",
            "lean_season": "June to August",
            "spawning_period": "August to October",
            "monsoon_ban_compliance": "Marine fishing ban applies to all mechanized bottom trawls."
        },
        "local_distribution": ["Satpati", "Dahanu", "Kelve"],
        "minimum_legal_size": "20 cm total length",
        "gear": "Bottom longlines and trawl nets",
        "commercial_tier": "Domestic Table Fish"
    },
    "Ribbonfish": {
        "scientific_name": "Trichiurus lepturus",
        "local_name": "Bala / Phati (बाळा)",
        "habitat": "Benthopelagic waters (20-80m depth) schooling over muddy bottoms.",
        "seasonal_information": {
            "peak_season": "October to February",
            "lean_season": "June to July",
            "spawning_period": "March to June",
            "monsoon_ban_compliance": "Trawling prohibited during monsoon ban."
        },
        "local_distribution": ["Satpati", "Dahanu", "Arnala"],
        "minimum_legal_size": "40 cm total length",
        "gear": "Trawl nets and dol nets",
        "commercial_tier": "Commercial Catch & Export"
    }
}

