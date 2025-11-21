import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import subprocess, sys
import re

st.caption("Artemisia MAURO")

st.header("Analyse du trafic du réseau de métro parisien (RATP)")

st.write("La Régie autonome des transports parisiens (RATP) assure l'exploitation d'une partie des transports en commun de Paris et de sa banlieue.")
st.write("Afin d'observer l'efficacité de ce réseau, nous allons analyser le trafic de certaines lignes de métro et de RER en 2021.")

st.subheader("Aperçu de la table")
st.caption("🔗 [Source : Trafic annuel entrant par station du réseau ferré 2021 (data.ratp)](https://data.ratp.fr/explore/dataset/trafic-annuel-entrant-par-station-du-reseau-ferre-2021/export/)")
df = pd.read_excel("trafic_2021.xlsx")

st.dataframe(df.head(10))

df_clean = df[df['Arrondissement'].notna()]
df['Correspondance_1'] = df['Correspondance_1'].astype(str)


st.subheader("Chiffres clés de 2021")

# --- Nettoyage et conversion en numérique ---
df['Trafic'] = pd.to_numeric(df['Trafic'], errors='coerce')
nb_usagers = df['Trafic'].sum()

df['Correspondance_1'] = pd.to_numeric(df['Correspondance_1'], errors='coerce')
nb_lignes = df['Correspondance_1'].nunique()

# --- Valeur de l'année précédente ---
nb_usagers_annee_prec = 913_388_062

# --- Calcul de la différence ---
delta_usagers = nb_usagers - nb_usagers_annee_prec
delta_pourcentage = (delta_usagers / nb_usagers_annee_prec) * 100

# --- Affichage des metrics ---
col1, col2 = st.columns(2)

col1.metric(
    label="💼 Usagers",
    value=f"{nb_usagers:,.0f}",
    delta=f"{delta_usagers:+,.0f} ({delta_pourcentage:.1f}%)"
)

col2.metric(
    label="🚇 Lignes",
    value=f"{nb_lignes:,.0f}"
)
st.write("Parmi les 14 lignes analysées, la RATP a vu sa part d'usagers augmenter d'un peu plus de 33%, c'est-à-dire de près de 305 millions d'usagers.")
st.write("Dans cette table, nous retrouvons que 14 de l'ensemble des lignes du réseau.")

st.subheader("Trafic par ligne ou arrondissement")
# --- Sélecteur utilisateur ---
choix = st.selectbox("Afficher le trafic par :", ["Ligne", "Arrondissement"])

if choix == "Ligne":
    # Agréger par la colonne 'Ligne'
    df_group = df.groupby('Ligne', as_index=False)['Trafic'].sum()
    x_col = 'Ligne'
else:
    # Agréger par arrondissement
    df_group = df.groupby('Arrondissement', as_index=False)['Trafic'].sum()
    x_col = 'Arrondissement'

# --- Tri croissant ---
df_group = df_group.sort_values('Trafic', ascending=True)

# --- Affichage du graphique ---
st.bar_chart(data=df_group, x=x_col, y='Trafic')
st.write("Les 3 lignes les plus fréquentées sont le RER A et les métros 4 et 1. Le RER A combine à lui seul environ 15,3%, soit près d'un tiers du trafic total annuel")
st.write("Les arrondissements les plus fréquentés sont quant à eux le 12ème, 10ème, 8ème et 1er : d'importantes gares comme la Gare du Nord ou la Gare saint Lazare se trouve dans certains de ces arrondissements.")


st.subheader("Les villes les plus fréquentées par le réseau d'usagers")

# --- Nettoyage et conversion en numérique ---
df['Trafic'] = pd.to_numeric(df['Trafic'], errors='coerce').fillna(0)

# Top 5 des villes
df_top_villes = df.groupby('Ville', as_index=False)['Trafic'].sum()
df_top_villes = df_top_villes.sort_values('Trafic', ascending=False).head(5)
df_top_villes = df_top_villes.sort_values('Trafic', ascending=True)  # Trier croissant

# Graphique Altair sans légende
chart = alt.Chart(df_top_villes).mark_bar().encode(
    x=alt.X('Trafic:Q', title='Trafic'),
    y=alt.Y('Ville:N', sort=None, title='Ville')  # respect ordre DataFrame
).properties(height=300)

st.altair_chart(chart, use_container_width=True)
st.write("La ville bien en tête du classement est la capitale, avec près de 870 millions d'usagers. Parmi les 4 autres villes du classement, 3 d'entre elles se situent dans le département des Hauts-de-Seine (92) : ces villes sont parmi les principales communes du département.")


st.subheader("Les 10 stations les plus fréquentées")
# --- Nettoyage et conversion en numérique ---
df['Trafic'] = pd.to_numeric(df['Trafic'], errors='coerce').fillna(0)

# Top 10 des stations
df_top_stations = df.groupby(['Station', 'Réseau'], as_index=False)['Trafic'].sum()
df_top_stations = df_top_stations.sort_values('Trafic', ascending=False).head(10)
df_top_stations = df_top_stations.sort_values('Trafic', ascending=True)  # Trier croissant

# Altair bar chart avec couleur par réseau
chart = alt.Chart(df_top_stations).mark_bar().encode(
    x=alt.X('Trafic:Q', title='Trafic'),
    y=alt.Y('Station:N', sort=None, title='Station'),
    color=alt.Color('Réseau:N', title='Réseau'),
    tooltip=['Station', 'Réseau', 'Trafic']
).properties(height=400)

st.altair_chart(chart, use_container_width=True)
st.write("Comme vu précédemment, les quartiers les plus fréquentés étaient parfois ceux comportant une ou plusieurs gares. Ce dernier graphique nous montre qu'effectivement la présence de ces gares doit être l'un des facteurs les plus importants quant au nombre d'usagers répertoriés.")
st.write("Parmi les 10 stations qui comptaient le plus d'usagers en 2021, 7 d'entres elles sont des stations desservant de grandes gares parisiennes. À côté de ces gares nous retrouvons aussi de grandes stations connues pour leur fréquentation comme Châtelet Les Halles ou Naterre Préfecture.")


st.write("En résumé, l'analyse du trafic 2021 met en évidence que la majorité des usagers se concentre sur quelques lignes et stations clés, notamment le RER A et les lignes 1 et 4 du métro, ainsi que dans des arrondissements et villes centrales comme Paris et certaines communes des Hauts-de-Seine. La présence de grandes gares semble être un facteur déterminant dans la fréquentation élevée de certaines stations. Globalement, le réseau RATP a connu une hausse significative du trafic par rapport à l'année précédente, soulignant l'importance de ces axes pour la mobilité quotidienne.")
