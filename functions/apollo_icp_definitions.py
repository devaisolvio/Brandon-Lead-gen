

INDUSTRY_ICPS = {
    "Amusement Parks": """Target: Theme parks, water parks, amusement parks, and family entertainment centers
Decision makers: VPs and Directors of Food & Beverage, Park Operations, Sustainability, Procurement, Chief Sustainability Officers, and C-suite executives (COO, General Manager)
Company size: Preferably 11-5000 employees with established multi-attraction operations
Geography: United States and United Kingdom
Use case: Entertainment venues seeking to optimize food & beverage operations, implement sustainability initiatives, improve procurement efficiency, and enhance guest experience at large-scale attractions""",

    "Higher Ed & University Arenas": """Target: Healthcare facilities, hospitals, medical centers, clinics, health systems, and patient care facilities (excluding insurance, pharmaceutical, medical device, and biotech companies)
Decision makers: Directors of Food Services, Nutrition Services, Dining Services, Environmental Services, Sustainability Managers, Facilities Directors, Procurement Directors, and C-suite operations executives
Company size: Preferably 11-5000 employees with significant patient/visitor volume
Use case: Healthcare and institutional facilities seeking to improve food service operations, nutrition programs, dining experiences, sustainability initiatives, and auxiliary services for patients, staff, and visitors""",

    "sports_arenas": """Target: Sports management companies, venue management firms, stadium operators, and sports venue facilities (excluding gyms, fitness centers, sports apparel, and equipment retailers)
Decision makers: VPs and Directors of Stadium Operations, Food & Beverage, Concessions, Venue Operations, Sustainability Directors, Procurement Directors, General Managers, and senior operations executives
Company size: Preferably 11-5000 employees managing professional sports venues
Industry focus: Sports, entertainment, events services, and recreational facilities (NAICS: 71311, 23713)
Use case: Sports venues and arenas seeking to optimize concessions operations, food & beverage services, sustainability programs, and overall venue operations for large-scale spectator events""",

    "Concert Venus": """Target: Concert venues, concert halls, indoor arenas, stadiums hosting live entertainment, sports events, and spectator sports (excluding single-location operations, food trucks, catering-only services, and ghost kitchens)
Decision makers: VPs and Directors of Food & Beverage, Heads of Concessions, Directors of Hospitality and Sustainability, Executive Chefs, and VP of Venue Operations
Company size: Preferably 21-10,000 employees operating medium to large entertainment venues
Geography: United States and United Kingdom
Use case: Entertainment and sports venues seeking to enhance food & beverage programs, concessions operations, hospitality services, and sustainability initiatives for concerts, sporting events, and live entertainment experiences""",

    "Beverages Chains": """Target: Bubble tea shops, coffee chains, tea brands, café chains, artisanal bakery brands, and food & beverage retail franchises (excluding single-location shops, food trucks, catering-only operations, and ghost kitchens)
Decision makers: VPs and Directors of Food & Beverage, Heads of Concessions, Directors of Hospitality and Sustainability, Executive Chefs, and operations executives
Company size: Preferably 21-10,000 employees with multi-location operations or franchise models
Geography: United States and United Kingdom
Industry focus: Food & beverages, consumer goods, retail
Use case: Multi-location beverage and food retail chains seeking to optimize operations, sustainability programs, supply chain management, and franchise/multi-unit coordination"""
}

DEFAULT_ICP = """Target: B2B service-oriented companies across various industries
Decision makers: C-suite executives, VPs, and Directors with operational or strategic responsibilities
Company size: Preferably 11-5000 employees
Geography: Primarily United States and United Kingdom
Use case: Companies seeking operational improvements, technology solutions, strategic partnerships, or business optimization services"""


def get_icp_for_industry(industry: str) -> str:
    """
    Get ICP text for a given industry.

    Args:
        industry: Industry identifier from apollo_input_data.py

    Returns:
        ICP text string for the industry, or default ICP if not found

    Examples:
        >>> get_icp_for_industry("Amusement Parks")
        "Target: Theme parks, water parks..."

        >>> get_icp_for_industry("Unknown Industry")
        "Target: B2B service-oriented companies..."
    """
    return INDUSTRY_ICPS.get(industry.strip(), DEFAULT_ICP)
