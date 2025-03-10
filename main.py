from fastapi import FastAPI
from pydantic import BaseModel
from llm import query_claude_for_sql
from database import fetch_value_from_supabase
from carbon_emission import extract_quantity, calculate_carbon_emission
from mangum import Mangum


app = FastAPI()

# Request body model
class UserQuery(BaseModel):
    query: str  #  Ensure FastAPI expects a JSON with a "query" field

@app.get("/")
def home():
    return {"message": "Welcome to the Carbon Emission API!"}

@app.post("/calculate_emission/")
async def calculate_emission(user_input: UserQuery):
    user_query = user_input.query  # Extract the query from JSON
    print(f" User Query Received: {user_query}")

    # Extract fuel quantity and unit
    fuel_quantity, unit = extract_quantity(user_query)
    print(f" Extracted Quantity: {fuel_quantity}, Unit: {unit}")

    if fuel_quantity is None:
        return {"error": "No valid quantity found in query."}

    # Generate SQL from Claude
    sql_query = query_claude_for_sql(user_query)
    print(f" Generated SQL Query: {sql_query}")

    if not sql_query:
        return {"error": "Failed to generate SQL query."}

    # Fetch kgco2e value from Supabase
    kgco2e_value = fetch_value_from_supabase(sql_query)
    print(f" Retrieved kgco2e Value: {kgco2e_value}")

    if kgco2e_value is None:
        return {"error": "No emission data found in database.", "sql_query": sql_query}

    # Ensure kgco2e is a float
    kgco2e = float(kgco2e_value)
    

    # Calculate carbon emissions
    total_emission = calculate_carbon_emission(user_query, kgco2e)
    print(f" Carbon Emission Calculated: {total_emission} kg CO₂e")

    return {
        "sql_query": sql_query,
        "kgco2e_retrieved": kgco2e,
        "carbon_emission_kg": total_emission
    }
handler = Mangum(app)
