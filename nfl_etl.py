import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import requests

# Configuración
URL = 'https://raw.githubusercontent.com/fivethirtyeight/nfl-elo-game/master/data/nfl_games.csv'
ULTIMO_ANO = 2018
CARPETA_GRAFICOS = "graficos"

# --------------------------
# Funciones
# --------------------------
def validar_url(url):
    try:
        respuesta = requests.head(url)
        return respuesta.status_code == 200
    except:
        return False

def extraer_datos(url):
    return pd.read_csv(url)

def transformar_datos(df, ultimo_ano):
    df = df.dropna(subset=['score1','score2','team1','team2'])
    df['date'] = pd.to_datetime(df['date'])
    df['Ganador'] = df.apply(lambda x: x['team1'] if x['score1'] > x['score2'] else x['team2'], axis=1)
    df['Diferencia_Puntos'] = df['score1'] - df['score2']
    df_reciente = df[df['date'].dt.year >= ultimo_ano]
    df_reciente['Año'] = df_reciente['date'].dt.year
    return df_reciente

def generar_dashboard(df):
    if not os.path.exists(CARPETA_GRAFICOS):
        os.makedirs(CARPETA_GRAFICOS)

    # 1️⃣ Victories per team
    victorias = df['Ganador'].value_counts().reset_index()
    victorias.columns = ['Equipo','Victorias']
    plt.figure(figsize=(12,6))
    sns.barplot(x='Equipo', y='Victorias', data=victorias)
    plt.xticks(rotation=90)
    plt.title('Victorias por equipo (2018-2024)')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/victorias_equipo.png')
    plt.close()

    # 2️⃣ Diferencia de puntos promedio por equipo
    diff_prom = df.groupby('Ganador')['Diferencia_Puntos'].mean().reset_index().sort_values('Diferencia_Puntos', ascending=False)
    plt.figure(figsize=(12,6))
    sns.barplot(x='Ganador', y='Diferencia_Puntos', data=diff_prom)
    plt.xticks(rotation=90)
    plt.title('Diferencia de puntos promedio por equipo')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/diferencia_promedio.png')
    plt.close()

    # 3️⃣ Partidos ganados por año (línea)
    ganados_anio = df.groupby(['Año','Ganador']).size().reset_index(name='Partidos_Ganados')
    plt.figure(figsize=(12,6))
    sns.lineplot(data=ganados_anio, x='Año', y='Partidos_Ganados', hue='Ganador', legend=None)
    plt.title('Partidos ganados por año')
    plt.savefig(f'{CARPETA_GRAFICOS}/partidos_ganados_anio.png')
    plt.close()

    # 4️⃣ Distribución de diferencia de puntos por equipo (boxplot)
    plt.figure(figsize=(12,6))
    sns.boxplot(x='Ganador', y='Diferencia_Puntos', data=df)
    plt.xticks(rotation=90)
    plt.title('Distribución de diferencia de puntos por equipo')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/boxplot_diferencia_puntos.png')
    plt.close()

    # 5️⃣ Top 5 equipos por victorias y diferencia de puntos
    top5_victorias = victorias.head(5)['Equipo']
    df_top5 = df[df['Ganador'].isin(top5_victorias)]
    plt.figure(figsize=(12,6))
    sns.barplot(x='Ganador', y='Diferencia_Puntos', data=df_top5, estimator=lambda x: sum(x>0))
    plt.title('Top 5 equipos por victorias: cantidad de partidos con diferencia positiva')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/top5_diferencia.png')
    plt.close()

    # 6️⃣ Proyección de victorias para el siguiente año
    df_anual = df.groupby(['Año','Ganador']).size().reset_index(name='Victorias')
    proyeccion = df_anual.groupby('Ganador')['Victorias'].mean().reset_index()
    proyeccion.columns = ['Equipo','Victorias_Proyectadas']
    plt.figure(figsize=(12,6))
    sns.barplot(x='Equipo', y='Victorias_Proyectadas', data=proyeccion.sort_values('Victorias_Proyectadas', ascending=False))
    plt.xticks(rotation=90)
    plt.title('Proyección de victorias por equipo para el siguiente año')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/proyeccion_victorias.png')
    plt.close()

    print("Todos los gráficos del dashboard se han generado en la carpeta:", CARPETA_GRAFICOS)

# --------------------------
# Main
# --------------------------
def main():
    if not validar_url(URL):
        print("URL inválida")
        return
    df = extraer_datos(URL)
    df_reciente = transformar_datos(df, ULTIMO_ANO)
    generar_dashboard(df_reciente)

if __name__ == "__main__":
    main()
