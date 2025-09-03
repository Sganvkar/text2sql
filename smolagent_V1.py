import os
import json
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from smolagents import LiteLLMModel

# -------------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------------------------------------------------
# Load DB connection string
# -------------------------------------------------------------------
load_dotenv()
MSSQL_URI = os.getenv("MSSQL_URI")
assert MSSQL_URI, "Set MSSQL_URI in .env"

engine = create_engine(MSSQL_URI, pool_pre_ping=True)

# -------------------------------------------------------------------
# Model setup
# -------------------------------------------------------------------
model = LiteLLMModel(
    model_id="ollama_chat/llama3:instruct",  # local Ollama model
    api_base="http://127.0.0.1:11434",
    num_ctx=8192,
)

# -------------------------------------------------------------------
# SQL generator prompt
# -------------------------------------------------------------------
GENERATOR_PROMPT = """
You are a helpful assistant that converts natural language questions into
valid Microsoft SQL Server queries. Only return the SQL query, nothing else.

Rules:
- Use exact column names.
- For text filters (like Gender, Diagnosis, RiskFlag), use LIKE with wildcards
  unless the value is guaranteed exact.
- Always output valid SQL Server syntax.

Database schema:
Patients(
  PatientID INT PRIMARY KEY,
  FirstName VARCHAR,
  LastName VARCHAR,
  Gender VARCHAR,
  DOB DATE,
  Diagnosis VARCHAR,
  RiskFlag VARCHAR, -- 'High', 'Medium', 'Low'
  LastVisitDate DATE
)

User question:
{question}
"""

# -------------------------------------------------------------------
# Generate SQL
# -------------------------------------------------------------------
def generate_sql(question: str) -> str:
    prompt = GENERATOR_PROMPT.format(question=question)
    sql_query = model.run(prompt)  # direct call to Ollama
    logging.info(f"Generated SQL:\n{sql_query}")
    return sql_query.strip()

# -------------------------------------------------------------------
# Execute SQL
# -------------------------------------------------------------------
def run_query(question: str):
    sql = generate_sql(question)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = [dict(row._mapping) for row in result]
        return json.dumps(rows, indent=2, default=str)
    except Exception as e:
        logging.error(f"SQL execution failed: {e}")
        return None

# -------------------------------------------------------------------
# Example usage
# -------------------------------------------------------------------
if __name__ == "__main__":
    questions = [
        "Show me the first name and diagnosis of patients with high risk flags.",
        "Show me the names and ages of all patients older than 60.",
        "List female patients admitted after January 2024.",
        "How many male patients are currently in the database?"
    ]

    for q in questions:
        logging.info(f"Processing: {q}")
        answer = run_query(q)
        print(f"\n=== Q: {q} ===\n{answer}")
