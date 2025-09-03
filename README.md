# LangChain + Ollama + SQL Server: Natural Language to SQL

This project demonstrates how to use **LangChain**, **Ollama**, and a local **Llama 3 model** (`llama3:instruct`) to convert natural language questions into SQL queries for **Microsoft SQL Server**.

It also includes a retry mechanism with an SQL **fixer loop** that attempts to correct invalid queries when errors occur.

---

## 🚀 Setup Instructions

### 1. Install and Run Ollama
1. Download and install Ollama from [https://ollama.ai](https://ollama.ai).
2. Pull the Llama 3 instruct model:
   ```bash
   ollama pull llama3:instruct
   ```
3. Start the Ollama server (it usually runs automatically after install):
   ```bash
   ollama serve
   ```
4. Verify it’s working:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   You should see `llama3:instruct` in the list.

---

### 2. Set up Python Environment
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate    # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Configure SQL Server Connection
Update the connection string in `langchain_V3.py` to match your SQL Server setup:

```python
connection_uri = (
    "mssql+pyodbc://@<server-name>/<db-name>?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "trusted_connection=yes&"
    "Encrypt=yes&"
    "TrustServerCertificate=yes"
)
```

Make sure you have the correct **ODBC Driver 18 for SQL Server** installed.

---

## 🛠 Development Process

The script was built step by step:

1. **Basic SQL generation**
   - Connected LangChain + Ollama (`llama3:instruct`) to SQL Server.
   - Prompted the model to generate SQL queries from natural language.

2. **Schema-Aware Prompting**
   - Added explicit schema details of `Patients` and `PatientNotes` tables.
   - Enforced strict rules (aliases, JOINs, date formatting, etc.).

3. **Error Handling**
   - Captured SQL errors from execution.
   - Implemented a retry loop (`FIXER_MAX_RETRIES`).
   - Sent failing query + error message back to the model for correction.

4. **Final Refinements**
   - Stripped markdown formatting (```sql blocks, backticks).
   - Added logging for debugging each query, error, and retry.
   - Returns `"Answer not found."` after max retries.

---

## ▶️ Running the Script

Run the script with:

```bash
python langchain_V3.py
```

It will:
- Generate SQL queries from predefined natural language questions.
- Execute them on SQL Server.
- Retry fixing invalid queries when errors occur.
- Log results and errors for debugging.

---

## 📌 Example Workflow

**User question:**
```
List the names of patients who have more than one note.
```

**Generated SQL (first attempt):**
```sql
SELECT p.FirstName, p.LastName
FROM Patients AS p
WHERE p.PatientID IN (
  SELECT pn.PatientID
  FROM PatientNotes AS pn
  GROUP BY pn.PatientID
  HAVING COUNT(*) > 1
)
```

If this query fails, the fixer loop attempts corrections up to 3 times.

---

## 📂 Project Files

- `langchain_V3.py` → Main script (LangChain + Ollama + SQL Server)
- `requirements.txt` → Python dependencies
- `README.md` → Documentation (this file)

---

## ✅ Next Steps / Future Improvements

- Add a smaller, faster model just for SQL **fixing** (e.g., `mistral:instruct`).
- Add caching for repeated queries.
- Build a simple **Streamlit UI** for interactive testing.

---

## 📝 Requirements

Contents of `requirements.txt`:

```
langchain
langchain-community
langchain-ollama
pyodbc
sqlalchemy
```

---

## 🔗 References

- [Ollama Docs](https://github.com/ollama/ollama)
- [LangChain Docs](https://python.langchain.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
