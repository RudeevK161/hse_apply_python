import pandas as pd
import streamlit as st
from functions_parallel_test import analyze_city, get_current_temperature
import plotly.graph_objs as go


def get_season(date):
    if date in [12, 1, 2]:
        return 'winter'
    elif date in [3, 4, 5]:
        return 'spring'
    elif date in [6, 7, 8]:
        return 'summer'
    else:
        return 'autumn'


st.title("Анализ исторических данных о погоде")

uploaded_file = st.file_uploader("Загрузите файл с историческими данными (CSV)", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    st.write("Исторические данные:")
    st.dataframe(data.head())

    cities = data['city'].unique()
    selected_city = st.selectbox("Выберите город", cities)

    st.subheader("Описательная статистика")
    season_stats, city_data = analyze_city(selected_city, data)
    st.write(city_data[['timestamp', 'temperature']].describe())

    st.subheader("Временной ряд температур")
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=city_data['timestamp'],
        y=city_data['temperature'],
        mode='lines',
        name='Temperature'
    ))

    anomalies = city_data[city_data['anomaly']]
    fig.add_trace(go.Scatter(
        x=anomalies['timestamp'],
        y=anomalies['temperature'],
        mode='markers',
        name='Anomalies',
        marker=dict(color='orange', size=10),
        text=[f"Дата: {row['timestamp']}<br>Температура - аномалия: {round(row['temperature'])} °C" for index, row in
              anomalies.iterrows()],
        hoverinfo='text'
    ))

    fig.update_layout(
        title=f"Температура в {selected_city}",
        xaxis_title="Дата",
        yaxis_title="Температура (°C)"
    )

    st.plotly_chart(fig)

    st.subheader("Сезонные профили")
    st.write("Гистограмма средних значений по сезонам:")
    season_stats_pivot_mean = season_stats.pivot(index='season', columns='city', values='mean')
    st.bar_chart(season_stats_pivot_mean)
    st.write("Сезонные профили с указанием среднего и стандартного отклонения:")
    st.write(season_stats)


api_key = st.text_input("Введите ваш API-ключ OpenWeatherMap")
if api_key:
    current_weather = get_current_temperature(selected_city, api_key)
    if current_weather == None:
        st.error("Неверный API-ключ. Пожалуйста, проверьте его.")
    else:
        st.write(f"Текущая температура в {selected_city}: {current_weather} °C")

        current_month = pd.to_datetime("today").month
        season = get_season(current_month)
        seasonal_mean = season_stats[season_stats['season'] == season]['mean'].item()
        seasonal_std = season_stats[season_stats['season'] == season]['std'].item()
        if current_weather < (seasonal_mean - 2*seasonal_std):
            st.write("Температура ниже нормы для этого сезона.")
        elif current_weather > (seasonal_mean + 2*seasonal_std) :
            st.write("Температура выше нормы для этого сезона.")
        else:
            st.write("Температура в пределах нормы для этого сезона.")