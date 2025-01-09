import pandas as pd
import requests
from multiprocessing import Pool
import time
import warnings
warnings.filterwarnings("ignore")

def get_current_temperature(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        return temperature
    else:
        print("Ошибка при получении данных:", response.status_code)
        return None


def open_data(path="data/temperature_data.csv"):
    df = pd.read_csv(path)
    return df


def calculate_moving_average(city_data):
    city_data['moving_average'] = city_data['temperature'].rolling(window=30).mean()
    return city_data


def calculate_seasonal_statistics(city_data):
    return city_data.groupby('season')['temperature'].agg(['mean', 'std']).reset_index()


def find_anomalies(city_data):
    mean_temp = city_data['temperature'].mean()
    std_temp = city_data['temperature'].std()
    threshold_upper = mean_temp + 2 * std_temp
    threshold_lower = mean_temp - 2 * std_temp
    city_data['anomaly'] = (city_data['temperature'] > threshold_upper) | (city_data['temperature'] < threshold_lower)
    return city_data


def analyze_city(city_name, df):
    city_data = df[df['city'] == city_name].copy()
    city_data = calculate_moving_average(city_data)
    seasonal_stats = calculate_seasonal_statistics(city_data)
    anomalies = find_anomalies(city_data)
    return seasonal_stats.assign(city=city_name), anomalies


if __name__ == "__main__":

    df = open_data()

    start_time = time.time()

    results_no_parallel = []
    for city in df['city'].unique():
        seasonal_stats, anomalies = analyze_city(city, df)
        results_no_parallel.append((seasonal_stats, anomalies))

    seasonal_stats_df_no_parallel = pd.concat([result[0] for result in results_no_parallel], ignore_index=True)
    anomalies_df_no_parallel = pd.concat([result[1] for result in results_no_parallel], ignore_index=True)

    merged_results = pd.merge(anomalies_df_no_parallel,
                              seasonal_stats_df_no_parallel[['season', 'city', 'mean', 'std']],
                              on=['season', 'city'], how='left')
    end_time = time.time()
    sequential_time = end_time - start_time
    print(f"Последовательное выполнение: {sequential_time:.2f} seconds")

    start_time = time.time()

    with Pool(4) as pool:
        cities = df['city'].unique()
        results = pool.starmap(analyze_city,
                               [(city, df) for city in cities])
    seasonal_stats_list, anomalies_list = zip(*results)
    parallel_seasonal_stats = pd.concat(seasonal_stats_list, ignore_index=True)
    parallel_anomalies = pd.concat(anomalies_list, ignore_index=True)

    end_time = time.time()
    parallel_time = end_time - start_time
    print(f"Параллельное выполнение: {parallel_time:.2f} seconds")