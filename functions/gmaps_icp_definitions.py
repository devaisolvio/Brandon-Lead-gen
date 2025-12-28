

GMAPS_ICPS = {
    "Search for stadium": """Type: Stadiums, arenas, large sports or entertainment venues, concert halls, and similar large event facilities
Characteristics: Medium to large venues with significant visitor traffic, recurring events, and professional operations
Geography: Primarily United States (with focus on major metropolitan areas)
Size indicators: High review counts (500+), professional venue management, capacity for large crowds
Use case: Venues where improving concessions, food & beverage operations, sustainability programs, and fan/guest experience can have meaningful impact
Ideal examples: Professional sports stadiums, major concert venues, university arenas, multi-purpose event centers""",

    "Search for Coffee Shops": """Type: Coffee shops, cafes, bubble tea shops, specialty beverage retailers, and artisanal bakery cafes
Characteristics: Multi-location chains, franchise operations, or high-volume single locations with strong brand presence
Geography: United States and United Kingdom (major cities and metropolitan areas)
Size indicators: High review counts (200+), professional operations, modern facilities, strong online presence
Use case: Coffee and beverage establishments seeking to optimize operations, expand sustainability programs, improve supply chain management, or enhance customer experience
Ideal examples: Regional coffee chains, successful independent cafes with expansion potential, specialty tea/boba chains, artisanal bakery cafes with beverage programs
Exclusions: Single-location mom-and-pop shops without growth plans, food trucks, temporary pop-ups"""
}

DEFAULT_GMAPS_ICP = """Type: Commercial venues and businesses with significant foot traffic and operational scale
Characteristics: Established businesses with professional management and growth potential
Geography: Primarily United States
Size indicators: Strong review presence (100+ reviews), professional operations, established brand
Use case: Businesses seeking operational improvements, sustainability initiatives, or enhanced customer experience
Focus: Venues where food & beverage, operations, or guest experience improvements can create meaningful business impact"""


def get_icp_for_gmaps_search(search_intent: str) -> str:
    """
    Get ICP text for a given Google Maps search intent.

    Args:
        search_intent: Search category from google_scraper_input_data.py (stored in 'icp' field)

    Returns:
        ICP text string for the search intent, or default ICP if not found

    Examples:
        >>> get_icp_for_gmaps_search("Search for stadium")
        "Type: Stadiums, arenas, large sports..."

        >>> get_icp_for_gmaps_search("Unknown Search")
        "Type: Commercial venues and businesses..."
    """
    return GMAPS_ICPS.get(search_intent.strip(), DEFAULT_GMAPS_ICP)
