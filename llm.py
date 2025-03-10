import boto3 
import json

def query_claude_for_sql(user_query):
    """Generate SQL query using Claude (Bedrock)."""
    bedrock = boto3.client(service_name="bedrock-runtime")
    region_name="us-east-1"

    fuel_types = ['', 'Plug-in Hybrid Electric Vehicle', 'Battery Electric Vehicle', 'Butane', 'CNG', 'LNG', 'LPG', 'Natural gas', 'Natural gas (100% mineral blend)', 'Other petroleum gas', 'Propane', 'Aviation spirit', 'Aviation turbine fuel', 'Burning oil', 'Diesel (average biofuel blend)', 'Diesel (100% mineral diesel)', 'Fuel oil', 'Gas oil', 'Lubricants', 'Naphtha', 'Petrol (average biofuel blend)', 'Petrol (100% mineral petrol)', 'Processed fuel oils - residual oil', 'Processed fuel oils - distillate oil', 'Refinery miscellaneous', 'Waste oils', 'Marine gas oil', 'Marine fuel oil', 'Coal (industrial)', 'Coal (electricity generation)', 'Coal (domestic)', 'Coking coal', 'Petroleum coke', 'Coal (electricity generation - home produced coal only)', 'Bioethanol', 'Biodiesel ME', 'Biomethane (compressed)', 'Biodiesel ME (from used cooking oil)', 'Biodiesel ME (from tallow)', 'Biodiesel HVO', 'Biopropane', 'Development diesel', 'Development petrol', 'Off road biodiesel', 'Biomethane (liquified)', 'Methanol (bio)', 'Avtur (renewable)', 'Wood logs', 'Wood chips', 'Wood pellets', 'Grass/straw', 'Biogas', 'Landfill gas', 'Carbon dioxide', 'Methane', 'Nitrous oxide', 'HFC-23', 'HFC-32', 'HFC-41', 'HFC-125', 'HFC-134', 'HFC-134a', 'HFC-143', 'HFC-143a', 'HFC-152a', 'HFC-227ea', 'HFC-236fa', 'HFC-245fa', 'HFC-43-I0mee', 'Perfluoromethane (PFC-14)', 'Perfluoroethane (PFC-116)', 'Perfluoropropane (PFC-218)', 'Perfluorocyclobutane (PFC-318)', 'Perfluorobutane (PFC-3-1-10)', 'Perfluoropentane (PFC-4-1-12)', 'Perfluorohexane (PFC-5-1-14)', 'PFC-9-1-18', 'Perfluorocyclopropane', 'Sulphur hexafluoride (SF6)', 'HFC-152', 'HFC-161', 'HFC-236cb', 'HFC-236ea', 'HFC-245ca', 'HFC-365mfc', 'Nitrogen trifluoride', 'Diesel', 'Hybrid', 'Unknown']

    units = ['kWh', 'km', 'miles', 'tonnes', 'litres', 'kWh (Net CV)', 'kWh (Gross CV)', 'cubic metres', 'GJ', 'kg', 'tonne.km', 'million litres', 'passenger.km', 'Room per night', 'per FTE Working Hour']


    fuel_types_str = ", ".join(f"'{fuel}'" for fuel in fuel_types)  # Format for SQL query
    units_str = ", ".join(f"'{unit}'" for unit in units)  # Format units

    prompt = f"""
    Given the following request: "{user_query}", generate an SQL query.
    The database schema is `uk_no_carbon_ai` and the table is `emission_data`.
    The relevant columns are:
      - `fuel_or_emission_type`
      - `unit`
      - `kgco2e` (carbon emission factor)
    Ensure the SQL query retrieves `kgco2e` based on the specified fuel type and unit.
    The fuel types to consider are: {fuel_types_str}.
    The units to consider are: {units_str}.
    Output only the SQL query, without explanations.
    """

    payload = {
        "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        })
    }

    response = bedrock.invoke_model(
        body=payload["body"],
        modelId=payload["modelId"],
        contentType=payload["contentType"],
        accept=payload["accept"]
    )

    try:
        response_body = json.loads(response["body"].read().decode("utf-8"))
        
        # Extract text properly, even if it's a list
        messages = response_body.get("content", [])  # Ensure it's a list
        if messages and isinstance(messages, list):
            sql_query = messages[0].get("text", "").strip()  # Extract first text response
        else:
            sql_query = None

        return sql_query
    except Exception as e:
        print("Error extracting SQL query:", e)
        return None
