"""
ICP definitions for HubSpot leads evaluation.

Since HubSpot leads typically have limited information (name and email),
we use a general ICP that can be applied broadly.
"""

DEFAULT_HUBSPOT_ICP = """Target: B2B companies and organizations across various industries
Decision makers: Business professionals, managers, and executives with decision-making authority
Company characteristics: Established businesses with professional email domains (not personal email providers like gmail.com, yahoo.com, etc.)
Geography: Primarily United States, Canada, United Kingdom, and other English-speaking countries
Use case: Companies seeking business solutions, partnerships, or services that can help improve operations, growth, or efficiency

Ideal lead characteristics:
- Professional email domain (corporate domains preferred over personal email providers)
- Appropriate job titles indicating decision-making authority or business relevance
- Companies in growth phase or established businesses
- B2B focused organizations

Exclusions:
- Personal email addresses (gmail.com, yahoo.com, hotmail.com, outlook.com, etc.)
- Clearly non-business entities
- Spam or invalid email addresses"""


def get_hubspot_icp() -> str:
    """
    Get ICP text for HubSpot leads evaluation.
    
    Returns:
        ICP text string for HubSpot leads
    
    Note: HubSpot leads have limited information, so we use a general ICP
    that evaluates based on email domain, name, and available metadata.
    """
    return DEFAULT_HUBSPOT_ICP

