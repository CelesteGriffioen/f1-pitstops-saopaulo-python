# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 21:47:21 2025

@author: pc
"""
#Importar librerias
import matplotlib.pyplot as plt
import pandas as pd
import statistics as stats

#Cargar archivos
df1 = pd.read_csv("pit_stops.csv") 
df2= pd.read_csv("races.csv")

df1.head(10)
df2.head(10)

#Identificar el id del circuito de Brasil (Interlagos)
circuito_brazil = df2[df2["name"].str.contains("Brazilian Grand Prix|São Paulo Grand Prix", case=False)]
circuito_brazil[["name", "circuitId", "year"]]
circuito_brazil_final = circuito_brazil.loc[(circuito_brazil["year"] > 2010)]

#El circuitId es 18, se usa del 2010 para adelante por falta de datos de temporadas previas
#Guardar los raceId
ids_brazil = circuito_brazil_final["raceId"].tolist()
temporada_ids = circuito_brazil_final[["raceId", "year"]]

#No usamos el ultimo valor porque no paso la carrera 2025
#Filtrar el df de pits stops con la lista de los raceId
pits_brazil = df1[df1["raceId"].isin(ids_brazil)]

#Elimino miliseconds (no da informacion nueva)
pits_brazil = pits_brazil.drop(["milliseconds"], axis=1)

#Uso merge para que aparezca la temporada de cada carrera
pits_brazil = pits_brazil.merge(right = temporada_ids, how = "left", left_on = "raceId", right_on = "raceId")

#Cargo los archivos csv para que aparezcan las escuderias
df3 = pd.read_csv("results.csv")
df4 = pd.read_csv("constructors.csv")

pit_results = pits_brazil.merge(
    df3[["raceId", "driverId", "constructorId"]],
    on=["raceId", "driverId"],
    how="left"
)

pits_final = pit_results.merge(
    df4[["constructorId", "name"]],
    on="constructorId",
    how="left"
)

pits_final.head(10)

#Pasar el df a archivos csv final para hacer el análisis
pits_final.to_csv("pits_brazil.csv", index=False, header=True, sep=",", decimal=".")

df1 = pd.read_csv("pits_brazil.csv") 

#Pits por temporada
pits_por_carrera = df1.groupby(["raceId", "year"])["stop"].count()

#Grafico pits por temporada
pits_por_carrera.plot(
    kind="bar",
    x="year",
    y="stop",
    title="Cantidad de pit stops por año en el GP de Brasil",
    xlabel="Año",
    ylabel="Cantidad de pit stops",
    figsize=(10,5),
    color="red"
)

plt.xticks(rotation=45)
plt.show()

#Duracion de los pits por año
#Cambiar a dato numérico
df1["duration"] = pd.to_numeric(df1["duration"], errors="coerce")

#Duracion por temporada (promedio)
duracion_por_temporada = df1.groupby("year")["duration"].mean()

#Grafico promedio de duración por temporada
grafico = duracion_por_temporada.plot(
    kind="line",
    title="Duración promedio de pit stops por temporada",
    xlabel="Año",
    ylabel="Duración promedio (en segundos)",
    figsize=(10,5),
    color="red"
)

#Agregar etiquetas de datos
for x, y in zip(duracion_por_temporada.index, duracion_por_temporada.values):
    grafico.text(x, y + 0.075, f"{y:.2f}", ha='center', fontsize=9, color='black')

plt.show()

#Confirmar si hay relacion o no entre temporadas
#Relacion entre duración y temporada (avance de tecnología)
from sklearn.linear_model import LinearRegression

#Armar modelo
modelo1 = LinearRegression()
modelo1.fit(pits_actuales[["year"]], pits_actuales["duration"])
prediccion1 = modelo1.predict(pits_actuales[["year"]])

#Grafico
ax = pits_actuales.plot.scatter(x="year", y="duration", alpha=0.5)
ax.plot(pits_actuales["year"], prediccion1, c="r")
plt.title("Relación entre temporada y duración promedio")
plt.show()

#Recta
modelo1.coef_
modelo1.intercept_

#R^2
modelo1.score(pits_actuales[["year"]], pits_actuales["duration"])

#Predicciones para temporadas futuras
duracion_futuro = pd.DataFrame({"year":[2025, 2026, 2027]})
predicciones = modelo1.predict(duracion_futuro)
print(predicciones)

#Duracion promedio por escuderia
duracion_por_equipo = df1.groupby("name")["duration"].mean()
duracion_por_equipo = duracion_por_equipo.sort_values(ascending=True)

#Grafico
duracion_por_equipo.plot(
    kind="bar",
    title="Duración promedio de pit stops por equipo",
    xlabel="Equipo",
    ylabel="Duración promedio en segundos",
    figsize=(10,5),
    color="red"
)
plt.ylim(22, 27)

#Agregar etiquetas de datos
ax.bar_label(ax.containers[0], fmt='%.2f')
plt.show()

#Lista de escuderias a incluir
equipos_a_mostrar = [
    "Mercedes", "McLaren", "Ferrari", "Williams", "Red Bull",
    "Kick Sauber", "Haas", "Aston Martin", "Alpine", "Racing Bulls"
]

#Filtrar antes de agrupar
df_filtrado = df1[df1["name"].isin(equipos_a_mostrar)]

#Calcular la duracion promedio solo para los equipos filtrados
duracion_por_equipo = df_filtrado.groupby("name")["duration"].mean()
duracion_por_equipo = duracion_por_equipo.sort_values(ascending=True)

#Generar el grafico y capturar el objeto por axes
ax = duracion_por_equipo.plot(
    kind="bar",
    title="Duración promedio de pit stops por equipo (Seleccionados)",
    xlabel="Equipo",
    ylabel="Duración promedio en segundos",
    figsize=(10, 5),
    color="red"
)

plt.ylim(22, 27)

#Agregar etiquetas de datos
ax.bar_label(ax.containers[0], fmt='%.2f')

plt.show()

#Parilla actual
#Filtrar a equipos actuales
df1["name"].unique()

#Renombrar registros (escuderias que cambiaron nombre)
df1["name"] = df1["name"].replace({
    "Toro Rosso": "Racing Bulls",
    "AlphaTauri": "Racing Bulls",
    "RB F1 Team": "Racing Bulls",
    "Renault": "Alpine",
    "Alpine F1 Team": "Alpine",
    "Alfa Romeo": "Kick Sauber",
    "Sauber": "Kick Sauber",
    "Haas F1 Team": "Haas"
})

parrilla_actual = ["Mercedes", "McLaren", "Ferrari", "Williams", "Red Bull", "Kick Sauber", "Haas", "Aston Martin", "Alpine", "Racing Bulls"]
pits_actuales = df1[df1["name"].isin(parrilla_actual)]


#Distribucion de desvio por equipo
desvio_ppt = pits_actuales.groupby("name")["duration"].std()

#Grafico de desvio por equipo
grafico = desvio_ppt.plot(
    kind="bar",
    title="Desvío estándar de la duración por equipo",
    color="red",
    figsize=(10,5)
)

plt.show()

#Distribucion por pit windows
#Cambiar a dato numerico
df1["lap"] = pd.to_numeric(df1["lap"], errors="coerce")

#Hacer intervalos
pits_actuales = pits_actuales.copy()

pits_actuales["pit_window"] = pd.cut(
    pits_actuales["lap"],
    bins = [0,15,30,45,60,71],
    labels = ["0 a 15", "15 a 30", "30 a 45", "45 a 60", "60 a 71"]
)

#Contar frecuencia
conteo_pits_window = pits_actuales["pit_window"].value_counts()

#Grafico
conteo_pits_window.plot(
    kind="pie",
    figsize=(6,6),
    autopct="%1.1f%%",
    startangle=90,
    title="Distribución de pit stops por tramo de vueltas "
)
plt.ylabel("")
plt.show()

#Evolucion de Mercedes, Ferrari, Red Bull
df = pd.read_csv("pits_brazil.csv")

#Datos 
data = df.filter (items=["duration","name","year"])
data["duration"] = pd.to_numeric(data["duration"], errors="coerce")
data = data.dropna(subset=["duration"])
data = data[data["name"].isin(["Mercedes","Ferrari","Red Bull"])]
promedio= data.groupby(["year", "name"])["duration"].mean().reset_index()

plt.figure (figsize=(8,5))
for equipo in promedio["name"].unique():
    subset = promedio[promedio["name"] == equipo]
    plt.plot(subset["year"], subset["duration"], marker="o", label=equipo)

plt.title("Duración promedio de pit stops por año")
plt.xlabel("Año")
plt.ylabel("Duración promedio (s)")

plt.legend(title="Escudería")
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()

#Medidas de tendencia central de STOPS
import statistics as stats
stats.mode(df.stop)
stats.mean(df.stop)
stats.median(df.stop)

#Medidas de tendencia central de DURATION
stats.mode(df1.duration)
stats.median(df1.duration)
stats.mean(df1.duration)