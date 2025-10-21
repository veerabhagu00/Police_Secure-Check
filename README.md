# Police_Secure-CheckData Science Project Summary: SecureCheck: A Python-SQL Digital Ledger for Police Post Logs

**Project Overview**

Police check posts require a centralized system for logging, tracking, and analyzing vehicle movements. Currently, manual logging and inefficient databases slow down security processes. This project aims to build an SQL-based check post database with a Python-powered dashboard for real-time insights and alerts

__Step 1_: Data Ingestion & Preprocessing (Jupyter Notebook)_
- Tool Used: Jupyter Notebook (.ipynb)
- Dataset: A structured CSV file "police.csv" containing police stop records.
- Libraries: pandas, pymysql, datetime
- Key Actions:
- Loaded the dataset using pandas.read_csv().
- Cleaned missing values using df.where(pd.notnull(df), None) to ensure compatibility with SQL NULL.
- Standardized column names and data types (e.g., converting boolean, formatting timestamps).


_Step 2: Database Integration_
- Database Used: MySQL
- Connection: Established using pymysql.connect.
- Table Created: police_log with fields like:
- stop_date, stop_time, driver_gender, driver_age, violation, search_conducted, stop_outcome, etc.
- Insertion Logic:
- Used parameterized SQL queries with %s placeholders to prevent SQL injection.
- Converted NaN to None before insertion to ensure proper handling of nulls.
- Inserted rows using cursor.execute().

_Step 3: Interactive Dashboard with Streamlit_
- Tool Used: Streamlit
- Purpose: To showcase insights and allow users to interact with the data.
- Form Input: Users can enter new stop records via a form (st.form()), including driver details, violation type, and search status.
- Prediction Logic: Based on historical data, the app predicts:
- Most likely stop_outcome using .mode()[0]
- Most frequent violation for similar cases
- Summary: Generates a readable summary of the stop, including actual and predicted values.
- Data Filtering: Filters historical data using multiple conditions to find similar records.
- Fallbacks: If no match is found, defaults like "warning" and "speeding" are used.

**Project Questions Addressed**
-Vehicle-Based
-Demographic-Based
-Time & Duration
-Violation-Based
-Location-Based
-Complex Analysis

**Key Learnings & Takeaways**
- Data Cleaning: Handling NaN vs None is crucial for SQL compatibility.
- Security: Parameterized queries protect against SQL injection.
- User Experience: Streamlit makes it easy to build intuitive forms and summaries.
- Analytics: Mode-based prediction offers a simple yet interpretable baseline
