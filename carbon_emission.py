import re

def extract_quantity(user_query):
    """Extract fuel quantity and unit from user query."""
    pattern = r"(\d+\.?\d*)\s*(litres?|kg|gallons?|tons?|barrels?|cubic meters?|m3|ml)?"
    matches = re.findall(pattern, user_query, re.IGNORECASE)

    if matches:
        # Filter out empty units and convert values to floats
        valid_matches = [(float(q), u.lower() if u else "units") for q, u in matches if q]

        # Select the highest quantity (to avoid false '2' match)
        best_match = max(valid_matches, key=lambda x: x[0])

        quantity, unit = best_match
        return quantity, unit

    print("No Quantity Found")  # Debugging
    return None, None



  # Explicitly return None if no match is found

def calculate_carbon_emission(user_query, kgco2e):
    """Calculate total carbon emission."""
    fuel_quantity, unit = extract_quantity(user_query)
    
    if fuel_quantity is None:
        print(" Error: Could not extract fuel quantity.")
        return None

    total_emission = fuel_quantity * kgco2e
    print(f" Carbon Emission for {fuel_quantity} {unit}: {total_emission} kg CO₂e")
    return total_emission
