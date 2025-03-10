import boto3
import json
import time
import botocore.exceptions

def query_claude_for_sql(user_query):
    """Generate SQL query using Claude (Bedrock) with retry logic to handle throttling."""
    
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")  # Set AWS region

    fuel_types = ['', 'Plug-in Hybrid Electric Vehicle', 'Battery Electric Vehicle', 'Butane', 'CNG', 'LNG', 'LPG', 'Natural gas', 'Petrol', 'Diesel']
    units = ['kWh', 'km', 'miles', 'tonnes', 'litres', 'cubic metres', 'GJ', 'kg']

    fuel_types_str = ", ".join(f"'{fuel}'" for fuel in fuel_types)  
    units_str = ", ".join(f"'{unit}'" for unit in units)  

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

    max_retries = 5  # Maximum number of retries
    backoff_factor = 2  # Exponential backoff factor
    wait_time = 1  # Initial wait time in seconds

    for attempt in range(max_retries):
        try:
            response = bedrock.invoke_model(
                body=payload["body"],
                modelId=payload["modelId"],
                contentType=payload["contentType"],
                accept=payload["accept"]
            )

            response_body = json.loads(response["body"].read().decode("utf-8"))
            messages = response_body.get("content", [])

            if messages and isinstance(messages, list):
                sql_query = messages[0].get("text", "").strip()
            else:
                sql_query = None

            return sql_query

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ThrottlingException":
                print(f"ThrottlingException: Too many requests. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= backoff_factor  # Increase wait time exponentially
            else:
                print("AWS Bedrock Client Error:", e)
                break  # If it's not a throttling error, break the loop
        except Exception as e:
            print("Error calling Claude API:", e)
            break  # Other errors should not be retried

    return None  # Return None if all retries fail
