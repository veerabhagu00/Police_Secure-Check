import streamlit as st
import pandas as pd
import pymysql
import plotly.express as plt

#Database connection
def start_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Veerabhagu@00',
            database='securecheck',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except error as x:
        st.error(f"DB Connection Error: {x}")
        return None

# get data from database
def get_data(query):
    connection = start_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                
                if result:  # Check if result is not empty
                    df = pd.DataFrame(result)
                    return df
                else:
                    print("Query executed successfully, but no data was returned.")
                    return pd.DataFrame()
        except Exception as e:  # Catch query execution errors
            print(f"Query Execution Error: {e}")
            return pd.DataFrame()
        finally:
            connection.close()
    else:
        print("Failed to establish database connection.")
        return pd.DataFrame()

        
# Streamlit UI
st.set_page_config(page_title="SecureCheck: A Python-SQL Digital Ledger for Police Post Logs", layout="wide")

st.title("🚨 SecureCheck: Police Check Post Digital Ledger")
st.markdown("Real-time monitoring and insights for law enforcement :oncoming_police_car:")

# Show full table
st.header("📋 Police Logs Overview")
table = "SELECT * FROM police_log"
data = get_data(table)
st.dataframe(data, use_container_width=True)

# Quick Metrics
st.header("📊 Deep Dive Visualizations")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚗 Vehicle-Based",
    "🧍 Demographic-Based",
    "🕒 Time & Duration",
    "⚖️ Violation-Based",
    "🌍 Location-Based",
    "🧠 Complex Analysis"
])
with tab1:
    st.subheader("Top 10 Vehicles in Drug-Related Stops")
    df = get_data("""
        SELECT vehicle_number, COUNT(*) AS drug_related_count
        FROM police_log
        WHERE drugs_related_stop = 1
        GROUP BY vehicle_number
        ORDER BY drug_related_count DESC
        LIMIT 10
    """)
    fig = plt.bar(df, x='vehicle_number', y='drug_related_count')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Most Frequently Searched Vehicles")
    df = get_data("""
        SELECT vehicle_number, COUNT(*) AS search_count
        FROM police_log
        WHERE search_conducted = 1
        GROUP BY vehicle_number
        ORDER BY search_count DESC
        LIMIT 10
    """)
    fig = plt.bar(df, x='vehicle_number', y='search_count')
    st.plotly_chart(fig, use_container_width=True)
    
with tab2:
    st.subheader("Arrests by Driver Age Group")
    df = get_data("""
        SELECT 
          CASE 
            WHEN driver_age < 18 THEN 'Under 18'
            WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
            WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
            WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
            ELSE '60+' 
          END AS age_group,
          COUNT(*) AS arrest_count
        FROM police_log
        WHERE stop_outcome LIKE '%arrest%'
        GROUP BY age_group
        ORDER BY arrest_count DESC
    """)
    fig = plt.bar(df, x='age_group', y='arrest_count')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Gender Distribution by Country")
    df = get_data("""
        SELECT country_name, driver_gender, COUNT(*) AS stop_count
        FROM police_log
        GROUP BY country_name, driver_gender
        ORDER BY country_name
    """)
    fig = plt.bar(df, x='country_name', y='stop_count', color='driver_gender', barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Highest Search Rate by Race & Gender")
    df = get_data("""
        SELECT driver_race, driver_gender, COUNT(*) AS search_count
        FROM police_log
        WHERE search_conducted = 1
        GROUP BY driver_race, driver_gender
        ORDER BY search_count DESC
        LIMIT 1
    """)
    st.dataframe(df)

with tab3:
    st.subheader("Traffic Stops by Hour")
    df = get_data("""
        SELECT HOUR(stop_time) AS hour_of_day, COUNT(*) AS stop_count
        FROM police_log
        GROUP BY hour_of_day
        ORDER BY stop_count DESC
    """)
    fig = plt.line(df, x='hour_of_day', y='stop_count')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Average Stop Duration by Violation")
    df = get_data("""
        SELECT violation, AVG(CAST(stop_duration AS UNSIGNED)) AS avg_duration
        FROM police_log
        GROUP BY violation
    """)
    fig = plt.bar(df, x='violation', y='avg_duration')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Arrest Rate: Day vs Night")
    df = get_data("""
        SELECT 
          CASE 
            WHEN HOUR(stop_time) BETWEEN 20 AND 6 THEN 'Night'
            ELSE 'Day'
          END AS time_period,
          COUNT(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate
        FROM police_log
        GROUP BY time_period
    """)
    fig = plt.bar(df, x='time_period', y='arrest_rate')
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Violations Linked to Searches or Arrests")
    df = get_data("""
        SELECT violation, COUNT(*) AS count
        FROM police_log
        WHERE search_conducted = 1 OR stop_outcome LIKE '%arrest%'
        GROUP BY violation
        ORDER BY count DESC
    """)
    fig = plt.bar(df, x='violation', y='count')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Violations Among Young Drivers (<25)")
    df = get_data("""
        SELECT violation, COUNT(*) AS count
        FROM police_log
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY count DESC
    """)
    fig = plt.bar(df, x='violation', y='count')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Violations Rarely Leading to Search/Arrest")
    df = get_data("""
        SELECT violation
        FROM police_log
        GROUP BY violation
        HAVING SUM(CASE WHEN search_conducted = 1 OR stop_outcome LIKE '%arrest%' THEN 1 ELSE 0 END) < 5
    """)
    st.dataframe(df)

with tab5:
    st.subheader("Drug-Related Stops by Country")
    df = get_data("""
        SELECT country_name, COUNT(*) AS drug_related_count
        FROM police_log
        WHERE drugs_related_stop = 1
        GROUP BY country_name
        ORDER BY drug_related_count DESC
    """)
    fig = plt.bar(df, x='country_name', y='drug_related_count')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Arrest Rate by Country & Violation")
    df = get_data("""
        SELECT country_name, violation,
          COUNT(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate
        FROM police_log
        GROUP BY country_name, violation
    """)
    st.dataframe(df)

    st.subheader("Country with Most Searches")
    df = get_data("""
        SELECT country_name, COUNT(*) AS search_count
        FROM police_log
        WHERE search_conducted = 1
        GROUP BY country_name
        ORDER BY search_count DESC
        LIMIT 1
    """)
    st.dataframe(df)

with tab6:
    st.subheader("Yearly Breakdown of Stops and Arrests by Country")
    df = get_data("""
        SELECT country_name, YEAR(stop_date) AS year,
          COUNT(*) AS total_stops,
          COUNT(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 END) AS total_arrests,
          RANK() OVER (PARTITION BY country_name ORDER BY COUNT(*) DESC) AS stop_rank
        FROM police_log
        GROUP BY country_name, YEAR(stop_date)
    """)
    st.dataframe(df)

    st.subheader("Driver Violation Trends by Age & Race")
    df = get_data("""
        SELECT age_group, driver_race, violation, COUNT(*) AS count
        FROM (
          SELECT *,
            CASE 
              WHEN driver_age < 18 THEN 'Under 18'
              WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
              WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
              WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
              ELSE '60+' 
            END AS age_group
          FROM police_log
        ) AS sub
        GROUP BY age_group, driver_race, violation
    """)
    st.dataframe(df)

    st.subheader("Stops by Year, Month, Hour")
    df = get_data("""
        SELECT 
          YEAR(stop_date) AS year,
          MONTH(stop_date) AS month,
          HOUR(stop_time) AS hour,
          COUNT(*) AS stop_count
        FROM police_log
        GROUP BY year, month, hour
        ORDER BY year, month, hour
    """)
    fig = plt.line(df, x='hour', y='stop_count', color='year', title="Stops by Hour Across Years")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Violations with High Search & Arrest Rates")
    df = get_data("""
        SELECT violation,
          COUNT(*) AS total_stops,
          COUNT(CASE WHEN search_conducted = 1 THEN 1 END) AS search_count,
          COUNT(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 END) AS arrest_count,
          RANK() OVER (ORDER BY COUNT(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 END) DESC) AS arrest_rank
        FROM police_log
        GROUP BY violation
    """)
    st.dataframe(df)

    st.subheader("Driver Demographics by Country")
    df = get_data("""
        SELECT country_name, driver_gender, driver_race,
          AVG(driver_age) AS avg_age,
          COUNT(*) AS total_stops
        FROM police_log
        GROUP BY country_name, driver_gender, driver_race
    """)
    st.dataframe(df)

    st.subheader("Top 5 Violations with Highest Arrest Rates")
    df = get_data("""
        SELECT violation,
          COUNT(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate
        FROM police_log
        GROUP BY violation
        ORDER BY arrest_rate DESC
        LIMIT 5
    """)
    fig = plt.bar(df, x='violation', y='arrest_rate', title="Top 5 Arrest-Prone Violations")
    st.plotly_chart(fig, use_container_width=True)


st.header("🧩 Advanced Insights")

select_query = st.selectbox("Select a Query", [" ",
    "Top 10 drug-related stops",
    "Gender distribution of drivers country wise",
    "Total Number of Police Stops",
    "Count of Stops by Violation Type",
    "Number of Arrests vs. Warnings",
    "Average Age of Drivers Stopped",
    "Top 5 Most Frequent Search Types",
    "Count of Stops by Gender",
    "Most Common Violation for Arrests",
    "Race-Gender combinations having highest search rates"
])

query_map = {
    "Gender distribution of drivers country wise": "SELECT country_name, driver_gender, COUNT(*) AS stop_count FROM police_log GROUP BY country_name, driver_gender ORDER BY country_name, driver_gender",
   "Top 10 drug-related stops": "SELECT vehicle_Number FROM police_log WHERE drugs_related_stop = 1 LIMIT 10",
    "Total Number of Police Stops": "SELECT COUNT(*) AS total_stops FROM police_log",
    "Count of Stops by Violation Type": "SELECT violation, COUNT(*) AS count FROM police_log GROUP BY violation ORDER BY count DESC",
    "Number of Arrests vs. Warnings": "SELECT stop_outcome, COUNT(*) AS count FROM police_log GROUP BY stop_outcome",
    "Average Age of Drivers Stopped": "SELECT AVG(driver_age) AS average_age FROM police_log",
    "Top 5 Most Frequent Search Types": "SELECT search_type, COUNT(*) AS count FROM police_log WHERE search_type != '' GROUP BY search_type ORDER BY count DESC LIMIT 5",
    "Count of Stops by Gender": "SELECT driver_gender, COUNT(*) AS count FROM police_log GROUP BY driver_gender",
    "Most Common Violation for Arrests": "SELECT violation, COUNT(*) AS count FROM police_log WHERE stop_outcome LIKE '%arrest%' GROUP BY violation ORDER BY count DESC LIMIT 1",
    "Race-Gender combinations having highest search rates": "SELECT driver_race, driver_gender, COUNT(*) AS total_stops, COUNT(CASE WHEN search_conducted = 1 THEN 1 END) AS total_searches, ROUND(COUNT(CASE WHEN search_conducted = 1 THEN 1 END) * 100.0 / COUNT(*), 2) AS search_rate FROM police_log GROUP BY driver_race, driver_gender ORDER BY search_rate DESC"

}

if st.button("Find"):
    result = get_data(query_map[select_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the selected query.")

st.markdown("---")
st.header("📝 Add New Police Log & Predict Outcome and Violation")

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    county_name = st.text_input("County Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=18, max_value=85, value=35)
    driver_race = st.text_input("Driver Race")
    violation = st.selectbox("Violation", ["Speeding", "Other", "DUI", "Seatbelt", "Signal"])
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("Predict Outcome & Violation")

    if submitted:
        # Filter data for prediction
        filtered_data = data[
            (data['driver_gender'] == driver_gender) &
            (data['driver_age'] == driver_age) &
            (data['search_conducted'] == int(search_conducted)) &
            (data['stop_duration'] == stop_duration) &
            (data['violation'] == violation) &
            (data['drugs_related_stop'] == int(drugs_related_stop))
        ]

        # Predict stop_outcome
        if not filtered_data.empty:
            predicted_outcome = filtered_data['stop_outcome'].mode()[0]
            predicted_violation = filtered_data['violation'].mode()[0]
        else:
            predicted_outcome = "warning"  # Default fallback
            predicted_violation = "speeding"  # Default fallback


        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

        st.markdown(f"""
🚔 **Prediction Summary**

- **Violation:** {violation}  
- **Predicted Violation (based on historical data):** {predicted_violation}  
- **Predicted Stop Outcome:** {predicted_outcome}

🗒️ A {driver_age}-year-old {driver_gender} driver in {county_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}.  
{search_text}, and the stop {drug_text}.  
Stop duration: **{stop_duration}**.  
Vehicle Number: **{vehicle_number}**.
""")

