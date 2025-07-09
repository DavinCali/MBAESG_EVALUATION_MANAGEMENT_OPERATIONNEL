import duckdb

db = duckdb.connect(database=':memory:')


db.execute("CREATE TABLE netflix AS SELECT * FROM read_csv_auto('data/Netflix_Datasets.csv')")


total_titles = db.execute("SELECT COUNT() FROM netflix").fetchone()[0]
print(f"Nombre total de titres : {total_titles}")


query_type = """
SELECT type, COUNT() AS total
FROM netflix
GROUP BY type
"""
result_type = db.execute(query_type).fetchdf()
print("Répartition Films / Séries")
print(result_type)


query_country = """
SELECT country, COUNT() AS nb
FROM netflix
WHERE country IS NOT NULL
GROUP BY country
ORDER BY nb DESC
LIMIT 5
"""
result_country = db.execute(query_country).fetchdf()
print("Top 5 pays producteurs")
print(result_country)


query_duree = """
SELECT AVG(CAST(SUBSTR(duration, 1, INSTR(duration, ' ') - 1) AS INTEGER)) AS avg_duration
FROM netflix
WHERE type = 'Movie' AND duration LIKE '%min%'
"""
avg_duration = db.execute(query_duree).fetchone()[0]
print(f"Durée moyenne des films : {round(avg_duration, 1)} min")


query_years = """
SELECT strftime(date_added, '%Y') AS year, COUNT() AS nb
FROM netflix
WHERE date_added IS NOT NULL
GROUP BY year
ORDER BY year
"""
result_years = db.execute(query_years).fetchdf()
print("Titres ajoutés par année")
print(result_years)