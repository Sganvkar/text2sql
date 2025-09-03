# langchain_V3.py
# A minimal example of using LangChain to convert natural language to SQL
# Contains query fixer

from langchain_ollama import OllamaLLM
from langchain_community.utilities import SQLDatabase
import logging

# -------------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------------------------------------------------
# Load models
# -------------------------------------------------------------------
generator = OllamaLLM(model="llama3:instruct")   # reasoning model

# -------------------------------------------------------------------
# Connect to SQL Server
# -------------------------------------------------------------------
connection_uri = (
    "mssql+pyodbc://@localhost\\SQLEXPRESS/DevelopmentShr?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "trusted_connection=yes&"
    "Encrypt=yes&"
    "TrustServerCertificate=yes"
)

db = SQLDatabase.from_uri(
    connection_uri,
    include_tables=["Patients"],         
    sample_rows_in_table_info=0
)


# -------------------------------------------------------------------
# Prompt templates
# -------------------------------------------------------------------
GENERATOR_PROMPT = """
You are a Microsoft SQL Server expert. Convert the user question into a SQL query 
for Microsoft SQL Server. Only return the SQL query, nothing else.

Rules:
- Use exact column names from schema. Never invent tables or columns.
- Always alias tables when more than one table is used (e.g., Patients AS p, PatientNotes AS pn).
- For text filters (like gender, diagnosis, risk flags), use LIKE with wildcards unless the value is guaranteed exact.
- Always format SQL valid for Microsoft SQL Server.
- Avoid backticks at the start and end of the query.
- Always format DATE or DATETIME fields in the result as DD-MM-YYYY hh:mm:ss AM/PM (12-hour clock) 
  using SQL Server FORMAT() function, e.g. FORMAT([LastVisitDate], 'dd-MM-yyyy hh:mm:ss tt').
- When grouping by dates, ensure the SELECT and GROUP BY use the same date granularity (e.g. both use FORMAT(..., 'MM-yyyy') for monthly counts).
- For filtering with WHERE clauses, always use ISO format 'YYYY-MM-DD' for dates.
- When calculating age, always use DATEDIFF(YEAR, DOB, GETDATE()) so the result is an integer in years.
- Use JOINs when accessing related data across tables.
- Use EXISTS only when you need to check for the existence of related rows without counting or selecting their fields.

Database schema:
1. Patients
   - PatientID (INT, PK)
   - FirstName (NVARCHAR)
   - LastName (NVARCHAR)
   - Gender (NVARCHAR)
   - DOB (DATE)
   - Diagnosis (NVARCHAR)
   - RiskFactor (NVARCHAR)
   - LastVisitDate (DATE)

2. PatientNotes
   - NoteID (INT, PK)
   - PatientID (INT, FK → Patients.PatientID)
   - NoteDate (DATE)
   - NoteText (NVARCHAR)
   - Provider (NVARCHAR)

User question:
{question}
"""

# -------------------------------------------------------------------
# Helper function to generate
# -------------------------------------------------------------------
def generate_sql(question: str) -> str:
    schema_str = db.get_table_info()
    # Step 1: Generate candidate SQL
    raw_sql = generator.invoke(
        GENERATOR_PROMPT.format(schema=schema_str, question=question)
    )
    logging.info(f"Raw SQL from generator:\n{raw_sql}\n")
    
    return raw_sql

# -------------------------------------------------------------------
# Run query
# -------------------------------------------------------------------
def run_query(question: str):
    sql_query = generate_sql(question)
    try:
        result = db.run(sql_query)
        return result
    except Exception as e:
        logging.error(f"Execution failed: {e}")

# -------------------------------------------------------------------
# Main execution
# -------------------------------------------------------------------
if __name__ == "__main__":
    questions = [
        # "Show me the first name and diagnosis of patients with high risk flags.",
        # "Show me the names and ages of all patients older than 60.",
        # "List female patients admitted after January 2024.",
        # "How many male patients are currently in the database?",

        # "Show me patients with a diagnosis of diabetes.",
        # "List patients with both hypertension and a high risk flag.",
        # "How many patients have a “Medium” risk flag?",
        # "Show me patients admitted in the last 30 days.",
        # "Which patients have not yet been discharged?",
        # "List patients discharged before June 2023.",

        # "What is the average age of patients with high risk flags?",
        # "Count the number of patients grouped by diagnosis.",
        # "Show me the number of patients admitted each month in 2024.",
        # "Show me the first and last names of patients under 40 diagnosed with asthma.",
        # "List the top 5 most common diagnoses among patients.",
        # "Find patients who were admitted in 2023 and still have a high risk flag.",

        # Basic
        "Show me all notes for patient Jane Smith.",
        "List the names of patients who have more than one note.",
        "Get all notes written by Dr. Carter.",

        # Intermediate
        "Show the latest note for each patient.",
        "List patients who had notes added in July 2024.",
        "How many notes were recorded per doctor in 2024?",
        "Show patient names with notes mentioning the word 'follow-up'.",

        # Advanced
        "For each patient, show the date of their first and last note.",
        "Show patients who had more than 1 note in the same month.",
        "Count how many emergency visits (notes containing 'emergency') occurred in 2024.",
        "Show patients who have notes mentioning both 'fatigue' and 'improvement'.",

        # Complex Joins + Aggregations
        "Show the number of patients per diagnosis category who had at least one note in 2024.",
        "Find the average time gap (in days) between notes for each patient.",
        "List patients over 60 years old who had notes written by Dr. Adams.",
        "Show all patients with diabetes who had more than 2 notes after March 2024."
    ]

    for question in questions:
        logging.info(f"Processing question: {question}")
        result = run_query(question)
        logging.info(f"Answer::: {result}\n")
