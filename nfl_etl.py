import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import requests
import numpy as np

# Configuración
URL = 'https://raw.githubusercontent.com/fivethirtyeight/nfl-elo-game/master/data/nfl_games.csv'
ULTIMO_ANO = 2018
CARPETA_GRAFICOS = "graficos"

# --------------------------
# Funciones generales
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

# --------------------------
# KPIs principales
# --------------------------
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

    # 3️⃣ Partidos ganados por año
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

    # --------------------
    # 7️⃣ KPIs ofensiva
    kpi_ofensiva(df)

    # --------------------
    # 8️⃣ KPIs defensiva
    kpi_defensiva(df)

    # --------------------
    # 9️⃣ Proyección del Super Bowl
    proyectar_super_bowl(df, proyeccion, diff_prom)

    print("Todos los gráficos del dashboard se han generado en la carpeta:", CARPETA_GRAFICOS)

# --------------------------
# KPIs ofensiva y defensiva
# --------------------------
def kpi_ofensiva(df):
    # Simulación de yardas basadas en puntajes
    df_of = df.copy()
    df_of['yards_team1'] = df_of['score1'] * 10
    df_of['yards_team2'] = df_of['score2'] * 10
    
    yards = pd.concat([
        df_of[['team1','yards_team1']].rename(columns={'team1':'Equipo','yards_team1':'Yardas'}),
        df_of[['team2','yards_team2']].rename(columns={'team2':'Equipo','yards_team2':'Yardas'})
    ])
    
    yardas_promedio = yards.groupby('Equipo')['Yardas'].mean().reset_index()
    
    plt.figure(figsize=(12,6))
    sns.barplot(x='Equipo', y='Yardas', data=yardas_promedio.sort_values('Yardas', ascending=False))
    plt.xticks(rotation=90)
    plt.title('Mejores ofensivas (yardas promedio por partido)')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/mejores_ofensivas.png')
    plt.close()

def kpi_defensiva(df):
    # Simulación de sacks y yardas permitidas
    df_def = df.copy()
    df_def['sacks_team1'] = df_def['score2'] // 10
    df_def['sacks_team2'] = df_def['score1'] // 10
    df_def['yards_allowed_team1'] = df_def['score2'] * 15
    df_def['yards_allowed_team2'] = df_def['score1'] * 15
    
    # Sumar por equipo
    sacks = pd.concat([
        df_def[['team1','sacks_team1']].rename(columns={'team1':'Equipo','sacks_team1':'Sacks'}),
        df_def[['team2','sacks_team2']].rename(columns={'team2':'Equipo','sacks_team2':'Sacks'})
    ])
    sacks_promedio = sacks.groupby('Equipo')['Sacks'].mean().reset_index()
    
    yards_allowed = pd.concat([
        df_def[['team1','yards_allowed_team1']].rename(columns={'team1':'Equipo','yards_allowed_team1':'YardasPermitidas'}),
        df_def[['team2','yards_allowed_team2']].rename(columns={'team2':'Equipo','yards_allowed_team2':'YardasPermitidas'})
    ])
    yards_promedio = yards_allowed.groupby('Equipo')['YardasPermitidas'].mean().reset_index()
    
    # Gráfico Sacks
    plt.figure(figsize=(12,6))
    sns.barplot(x='Equipo', y='Sacks', data=sacks_promedio.sort_values('Sacks', ascending=False))
    plt.xticks(rotation=90)
    plt.title('Defensas con más sacks promedio')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/defensas_sacks.png')
    plt.close()
    
    # Gráfico Yardas permitidas
    plt.figure(figsize=(12,6))
    sns.barplot(x='Equipo', y='YardasPermitidas', data=yards_promedio.sort_values('YardasPermitidas'))
    plt.xticks(rotation=90)
    plt.title('Defensas con menos yardas permitidas promedio')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/defensas_yardas_permitidas.png')
    plt.close()

# --------------------------
# Proyección ganador Super Bowl
# --------------------------
def proyectar_super_bowl(df, victorias_proj, diff_prom):
    """
    Proyección simple: combinamos victorias proyectadas y diferencia de puntos promedio.
    Elegimos el equipo con mayor valor combinado como favorito al Super Bowl.
    """
    merged = pd.merge(victorias_proj, diff_prom, left_on='Equipo', right_on='Ganador')
    merged['Score'] = merged['Victorias_Proyectadas'] + merged['Diferencia_Puntos']
    
    ganador_favorito = merged.sort_values('Score', ascending=False).iloc[0]['Equipo']
    
    plt.figure(figsize=(8,6))
    sns.barplot(x='Equipo', y='Score', data=merged.sort_values('Score', ascending=False))
    plt.xticks(rotation=90)
    plt.title(f'Proyección del ganador del Super Bowl: {ganador_favorito}')
    plt.tight_layout()
    plt.savefig(f'{CARPETA_GRAFICOS}/proyeccion_super_bowl.png')
    plt.close()

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
