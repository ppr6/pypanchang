import requests
from flask import current_app
from datetime import datetime

def get_panchang_data(location_id, date=None):
    """
    Fetch panchang data for a given location and date
    
    Args:
        location_id (str): Location ID for the city
        date (datetime, optional): Date for which to fetch panchang. Defaults to current date.
    
    Returns:
        dict: Parsed panchang data
    """
    if date is None:
        date = datetime.now()
    
    params = {
        'locid': location_id,
        'dt': date.day,
        'mn': date.month,
        'yr': date.year
    }
    
    try:
        response = requests.get(
            current_app.config['PANCHANG_API_BASE_URL'],
            params=params
        )
        response.raise_for_status()
        
        # Parse the response text and extract relevant information
        # This is a basic implementation - you might want to add more sophisticated parsing
        data = response.text
        
        # TODO: Add proper parsing of the response data
        # For now, returning the raw text
        return {
            'raw_data': data,
            'location_id': location_id,
            'date': date.strftime('%Y-%m-%d')
        }
        
    except requests.RequestException as e:
        current_app.logger.error(f"Error fetching panchang data: {str(e)}")
        return None 