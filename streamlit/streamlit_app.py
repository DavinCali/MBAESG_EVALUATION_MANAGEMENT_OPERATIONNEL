<<<<<<< HEAD
import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

def generate_where_clause(filters: list):
    if not filters:
        return ""
    return "WHERE " + " AND ".join(filters)

st.title("Analyse Netflix – KPI interactifs")

uploaded = st.file_uploader("Chargez le fichier CSV Netflix", type="csv")
if not uploaded:
    st.stop()

df = pd.read_csv(uploaded)
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

con = duckdb.connect()
con.execute("CREATE OR REPLACE TABLE netflix AS SELECT * FROM df")

# 🔽 Filtres dynamiques : année, type, listed_in
year_options = sorted(df['date_added'].dropna().dt.year.unique())
type_options = sorted(df['type'].dropna().unique())
listed_in_unique = sorted(
    set(cat.strip() for sublist in df['listed_in'].dropna().str.split(',') for cat in sublist)
)

col1, col2, col3 = st.columns(3)
selected_year = col1.selectbox("Filtrer par année", ["Tous"] + [int(y) for y in year_options])
selected_type = col2.selectbox("Filtrer par type", ["Tous"] + type_options)
selected_genre = col3.selectbox("Filtrer par genre", ["Tous"] + listed_in_unique)

filters = []
if selected_year != "Tous":
    filters.append(f"EXTRACT(YEAR FROM date_added) = {selected_year}")
if selected_type != "Tous":
    filters.append(f"type = '{selected_type}'")
if selected_genre != "Tous":
    filters.append(f"STRPOS(listed_in, '{selected_genre}') > 0")

where_clause = generate_where_clause(filters)

# KPI 1 – Répartition des types
df_type = con.execute(f"""
    SELECT type, COUNT(*) AS count
    FROM netflix
    {where_clause}
    GROUP BY type
""").df()

if not df_type.empty:
    fig1, ax1 = plt.subplots()
    ax1.pie(df_type['count'], labels=df_type['type'], autopct='%1.1f%%')
    ax1.set_title("Répartition des types de contenu")
    st.pyplot(fig1)
else:
    st.info("Aucune donnée disponible pour ces filtres.")

# KPI 2 – Nombre de titres ajoutés par année
filters_year = [f for f in filters if not f.startswith("EXTRACT(YEAR")]
where_clause_year = generate_where_clause(["date_added IS NOT NULL"] + filters_year)

df_year = con.execute(f"""
    SELECT EXTRACT(YEAR FROM date_added) AS year, COUNT(*) AS count
    FROM netflix
    {where_clause_year}
    GROUP BY year
    ORDER BY year
""").df()

if not df_year.empty:
    fig2, ax2 = plt.subplots()
    ax2.bar(df_year['year'], df_year['count'])
    ax2.set_title("Titres ajoutés par année")
    ax2.set_xlabel("Année")
    ax2.set_ylabel("Nombre de titres")
    st.pyplot(fig2)
else:
    st.info("Pas de données pour l’évolution annuelle avec ces filtres.")

# KPI 3 – Top 5 catégories genre
df_listed = df.copy()
if selected_year != "Tous":
    df_listed = df_listed[df_listed['date_added'].dt.year == selected_year]
if selected_type != "Tous":
    df_listed = df_listed[df_listed['type'] == selected_type]
if selected_genre != "Tous":
    df_listed = df_listed[df_listed['listed_in'].str.contains(selected_genre, na=False)]


listed_exploded = df_listed['listed_in'].dropna().str.split(',').explode().str.strip()
top_listed = listed_exploded.value_counts().head(5)

if not top_listed.empty:
    fig3, ax3 = plt.subplots()
    top_listed.plot(kind='bar', ax=ax3)
    ax3.set_title("Top 5 genres les plus vu")
    ax3.set_xlabel("Genre")
    ax3.set_ylabel("Nombre de titres")
    st.pyplot(fig3)
else:
    st.info("Aucun genre à afficher avec ces filtres.")

# KPI 4 – Durée moyenne des films
filters_duration = filters + ["type = 'Movie'", "duration LIKE '%min%'"]
where_clause_duration = generate_where_clause(filters_duration)

df_duree = con.execute(f"""
    SELECT AVG(CAST(SUBSTR(duration, 1, INSTR(duration, ' ') - 1) AS INTEGER)) AS avg_duration
    FROM netflix
    {where_clause_duration}
""").df()

if not df_duree.empty and not pd.isna(df_duree['avg_duration'][0]):
    avg = round(df_duree['avg_duration'][0], 1)
    st.metric("Durée moyenne des films", f"{avg} min")
else:
    st.info("Aucune donnée de durée disponible avec ces filtres.")
