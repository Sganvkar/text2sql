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

### 4. Database setup & Seeding

```SQL
CREATE TABLE Patients (
    PatientID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Gender NVARCHAR(10) NOT NULL,
    DOB DATE NOT NULL,
    Diagnosis NVARCHAR(100),
    RiskLevel NVARCHAR(20),
    LastVisitDate DATE
);
```

```SQL
INSERT INTO Patients (
    FirstName, LastName, Gender, DOB, Diagnosis, RiskLevel, LastVisitDate
)
VALUES
('John', 'Doe', 'Male', '1955-06-12', 'Hypertension', 'High', '2024-02-01'),
('Jane', 'Smith', 'Female', '1980-09-23', 'Diabetes', 'Medium', '2024-03-15'),
('Michael', 'Johnson', 'Male', '1970-01-10', 'Asthma', 'Low', '2024-01-20'),
('Emily', 'Davis', 'Female', '1995-04-18', 'Healthy', 'Low', '2024-03-05'),
('Robert', 'Brown', 'Male', '1965-11-30', 'Heart Disease', 'High', '2024-02-28'),
('Linda', 'Wilson', 'Female', '2000-07-12', 'Anemia', 'Medium', '2024-03-10'),
('William', 'Taylor', 'Male', '1950-02-17', 'Diabetes', 'High', '2024-01-30'),
('Olivia', 'Anderson', 'Female', '1988-12-05', 'Asthma', 'Low', '2024-02-18'),
('James', 'Thomas', 'Male', '1978-08-22', 'Hypertension', 'Medium', '2024-03-01'),
('Sophia', 'Martinez', 'Female', '1992-03-14', 'Healthy', 'Low', '2024-02-25');

```

```SQL
CREATE TABLE PatientNotes (
    NoteID INT PRIMARY KEY IDENTITY(1,1),
    PatientID INT NOT NULL,
    NoteDate DATETIME NOT NULL DEFAULT GETDATE(),
    NoteText NVARCHAR(MAX) NOT NULL,
    Provider NVARCHAR(100) NOT NULL, 
    CONSTRAINT FK_PatientNotes_Patients FOREIGN KEY (PatientID)
        REFERENCES Patients(PatientID)
        ON DELETE CASCADE
);
```

```SQL
INSERT INTO PatientNotes (PatientID, NoteDate, NoteText, Provider)
VALUES
(2, '2024-03-16 09:15:00', 'Patient shows stable condition. Continue with current medication.', 'Dr. Adams'),
(2, '2024-06-20 11:45:00', 'Follow-up visit. Insulin dosage adjusted.', 'Dr. Carter'),

(4, '2024-03-06 10:30:00', 'Routine check-up. No issues reported.', 'Dr. Smith'),

(6, '2024-03-11 14:00:00', 'Patient reports fatigue. Iron supplements prescribed.', 'Dr. Taylor'),
(6, '2024-08-01 16:20:00', 'Follow-up shows improvement in hemoglobin levels.', 'Dr. Taylor'),

(8, '2024-02-19 08:50:00', 'Asthma symptoms mild. Inhaler prescribed.', 'Dr. Johnson'),
(8, '2024-05-25 09:40:00', 'Emergency visit due to shortness of breath. Condition stabilized.', 'Dr. Adams'),

(10, '2024-02-26 13:10:00', 'Routine annual check-up. Patient healthy.', 'Dr. Smith'),
(10, '2024-07-15 15:00:00', 'Patient reported dizziness. Tests recommended.', 'Dr. Carter');

```

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
