from langchain_ollama import OllamaLLM
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
import logging
logging.basicConfig(level=logging.DEBUG)
# 1. Load model
llm = OllamaLLM(model="llama3:instruct", temperature=0)

# 2. Connect to SQL Server
connection_uri = (
    "mssql+pyodbc://@localhost\\SQLEXPRESS/DevelopmentShr?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "trusted_connection=yes&"
    "Encrypt=yes&"
    "TrustServerCertificate=yes"
)
db = SQLDatabase.from_uri(connection_uri)

# 4. Custom prompt template with schema baked in
custom_prompt = PromptTemplate.from_template("""
You are a senior data analyst writing **T-SQL** for Microsoft SQL Server (2019+).

Rules:
- Use only the tables/columns from the provided schema.
- Prefer schema-qualified names (e.g., dbo.Patients).
- Use SQL Server syntax: use TOP (not LIMIT), GETDATE/DATEADD, TRY_CONVERT/TRY_CAST.
- Do not use ILIKE/REGEXP/backticks; use brackets [ ] only if identifiers contain spaces/special chars.
- Strings use single quotes; NVARCHAR literals use N'...'.
- Return only a single T-SQL query, no explanations, no markdown.

Schema:
{table_info}

User question: {input}
SQLQuery:
""")

# 5. Build the chain
db_chain = SQLDatabaseChain.from_llm(
    llm,
    db,
    prompt=custom_prompt,
    verbose=True,
    return_intermediate_steps=True,
    use_query_checker=True
)


# 6. Run query
query = "List the names and diagnoses of patients flagged as high risk"
result = db_chain.invoke(query)

print("\n=== Intermediate Steps ===")
for i, s in enumerate(result.get("intermediate_steps", [])):
    print(f"[{i}] {s}")

print("\n=== Final Answer ===")
print(result.get("result"))

