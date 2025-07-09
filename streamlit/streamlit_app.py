import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

st.title("Analyse Netflix – KPI interactifs")

uploaded = st.file_uploader("Téléversez le CSV Netflix", type="csv")
if not uploaded:
    st.stop()

df = pd.read_csv(uploaded)
con = duckdb.connect()
con.execute("CREATE OR REPLACE TABLE netflix AS SELECT * FROM df")

df_type = con.execute("SELECT type, COUNT() AS count FROM netflix GROUP BY type").df()

fig1, ax1 = plt.subplots()
ax1.pie(df_type['count'], labels=df_type['type'], autopct='%1.1f%%')
ax1.set_title("Répartition des types de contenu")
st.pyplot(fig1)


df_year = con.execute("""
    SELECT strftime(date_added, '%Y') AS year, COUNT() as count
    FROM netflix
    WHERE date_added IS NOT NULL
    GROUP BY year
    ORDER BY year
""").df()

fig2, ax2 = plt.subplots()
ax2.bar(df_year['year'], df_year['count'])
ax2.set_title("Titres ajoutés par année")
ax2.set_xlabel("Année")
ax2.set_ylabel("Nombre de titres")
st.pyplot(fig2)


df_country = con.execute("""
    SELECT country, COUNT(*) AS count
    FROM netflix
    WHERE country IS NOT NULL
    GROUP BY country
    ORDER BY count DESC
    LIMIT 5
""").df()

fig3, ax3 = plt.subplots()
ax3.bar(df_country['country'], df_country['count'])
ax3.set_title("Top 5 pays producteurs")
ax3.set_ylabel("Nombre de titres")
st.pyplot(fig3)


df_duree = con.execute("""
    SELECT AVG(CAST(SUBSTR(duration, 1, INSTR(duration,' ') -1) AS INTEGER)) AS avg_duration
    FROM netflix
    WHERE type = 'Movie' AND duration LIKE '%min%'
""").df()

avg = round(df_duree['avg_duration'][0], 1)
st.metric("Durée moyenne des films", f"{avg} min")