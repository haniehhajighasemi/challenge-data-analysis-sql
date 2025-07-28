import streamlit as st
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

dataBase = '/Users/haniehhajighasemi/Documents/BeCode/Bouman9/GitRep/Projects/challenge-data-analysis-sql/kbo_database.db'
# Connect to your database
conn = sqlite3.connect(dataBase)

# Query: juridical form by sector and year
query = """
SELECT 
 STRFTIME('%Y', 
  SUBSTR(e.StartDate, 7, 4) || '-' || SUBSTR(e.StartDate, 4, 2) || '-' || SUBSTR(e.StartDate, 1, 2)
) AS Year,
  a.NaceCode,
  nc.Description AS NaceDescription,
  e.JuridicalForm,
  jc.Description AS JuridicalFormDescription,
  COUNT(*) AS CompanyCount,
  ROUND(
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (
      PARTITION BY STRFTIME('%Y', e.StartDate), a.NaceCode
    ), 
    2
  ) AS SectorYearPercentage
FROM enterprise e
JOIN activity a ON e.EnterpriseNumber = a.EntityNumber
LEFT JOIN code nc 
  ON CAST(a.NaceCode AS TEXT) = nc.Code 
     AND nc.Category = 'NACE' 
     AND nc.Language = 'EN'
LEFT JOIN code jc 
  ON CAST(e.JuridicalForm AS TEXT) = jc.Code 
     AND jc.Category = 'JURIDICAL_FORM' 
     AND jc.Language = 'EN'
WHERE e.StartDate IS NOT NULL
GROUP BY 
  Year, a.NaceCode, nc.Description, e.JuridicalForm, jc.Description
ORDER BY 
  Year DESC, a.NaceCode, CompanyCount DESC;
"""

df = pd.read_sql_query(query, conn)
st.write(df.head()) 
# Sidebar filters
years = df['Year'].unique()
selected_year = st.sidebar.selectbox("Select Year", sorted(years, reverse=True))

sectors = df['NaceDescription'].dropna().unique()
selected_sector = st.sidebar.selectbox("Select Sector", sorted(sectors))

filtered_df = df[(df['Year'] == selected_year) & (df['NaceDescription'] == selected_sector)]

# Plot
st.title("Juridical Form Distribution by Sector and Year")
st.subheader(f"{selected_sector} - {selected_year}")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=filtered_df.sort_values('SectorYearPercentage', ascending=False),
    x="SectorYearPercentage", y="JuridicalFormDescription", ax=ax
)
ax.set_xlabel("Percentage (%)")
ax.set_ylabel("Juridical Form")
ax.set_title("Company Distribution by Juridical Form")
st.pyplot(fig)
