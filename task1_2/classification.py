import sqlite3
import warnings

import joblib
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

warnings.filterwarnings("ignore")

# Подключение к базе данных
conn = sqlite3.connect("../data/Dataset.db")
cursor = conn.cursor()

# Выбор режима аналитики - для всех игроков (full) или не ботов (no_bots)
mode = "no_bots"

if mode == "full":
    postfix = ""
    where = "True"

if mode == "no_bots":
    postfix = "_no_bots"
    where = "account_db_id >= 0"

# получаем список режимов игры
query_game_mode = """
SELECT DISTINCT(cat_name)
FROM catalog_items
INNER JOIN arenas
ON arenas.team_build_type_id = catalog_items.cat_value
WHERE catalog_items.cat_type = "BATTLE_TYPE"
"""
cursor.execute(query_game_mode)
game_modes = cursor.fetchall()

for game_mode in game_modes:
    # Извлекаем данные из таблиц для текущего режима игры
    query = f"""SELECT cat_name,vehicle_type_id,AVG(ships_killed),AVG(planes_killed),AVG(damage),
    AVG(team_damage),AVG(received_damage),AVG(regen_hp),AVG(is_alive),
    AVG(credits),AVG(exp)
    FROM arenas
    JOIN arena_members
    ON arenas.arena_id = arena_members.arena_id
    AND arenas.periphery_id = arena_members.periphery_id
    JOIN catalog_items
    ON arenas.team_build_type_id = catalog_items.cat_value
    WHERE typeof(account_db_id) = 'integer' 
    AND {where}
    AND catalog_items.cat_type = "BATTLE_TYPE" 
    AND cat_name = "{str(game_mode[0])}"
    GROUP BY vehicle_type_id 
    """
    cursor.execute(query)
    data = cursor.fetchall()

    if len(data) < 14:
        continue
    # Создаем DataFrame из полученных данных
    columns = [
        "cat_name",
        "vehicle_type_id",
        "AVG(ships_killed)",
        "AVG(planes_killed)",
        "AVG(damage)",
        "AVG(team_damage)",
        "AVG(received_damage)",
        "AVG(regen_hp)",
        "AVG(is_alive)",
        "AVG(credits)",
        "AVG(exp)",
    ]
    df = pd.DataFrame(data, columns=columns)

    # Выбор необходимых столбцов
    selected_columns = [
        "AVG(ships_killed)",
        "AVG(planes_killed)",
        "AVG(damage)",
        "AVG(team_damage)",
        "AVG(received_damage)",
        "AVG(regen_hp)",
        "AVG(is_alive)",
        "AVG(credits)",
        "AVG(exp)",
    ]
    data_selected = df[selected_columns]

    # необходимо для определения способа нормализации

    plt.figure(figsize=(16, 12))
    plt.subplots_adjust(bottom=0.15, top=0.95)
    plt.boxplot(data_selected)
    plt.xticks(
        np.arange(1, len(selected_columns) + 1),
        selected_columns,
        fontsize=14,
        rotation=30,
    )
    plt.yticks(fontsize=16)
    plt.yscale("log")  # Применение логарифмической шкалы по оси y
    plt.title(
        f"Box Plot of Data (Log Scale). Game Mode: {str(game_mode[0])} ", fontsize=18
    )
    plt.savefig(f"../task1_2/pictures/box_plot_classification_{game_mode}{postfix}.png")
    plt.show()

    # Масштабирование данных
    scaler = RobustScaler()
    data_scaled = scaler.fit_transform(data_selected)

    # определение оптимального количества кластеров
    silhouette_scores = []
    for optimal_k in range(2, 15):
        kmeans = KMeans(n_clusters=optimal_k, random_state=0)
        kmeans.fit(data_scaled)
        labels = kmeans.labels_
        silhouette_scores.append(silhouette_score(data_scaled, labels))

    optimal_k_index = np.argmax(silhouette_scores)
    optimal_k = optimal_k_index + 2  # +2, так как индексация начинается с 0

    # визуализация методом силуэта
    plt.plot(range(2, 15), silhouette_scores)
    plt.xlabel("Number of Clusters")
    plt.ylabel("Silhouette Score")
    plt.title(f"Silhouette Method. Game Mode: {str(game_mode[0])}")
    plt.show()

    # Применение метода K-средних с оптимальным количеством кластеров
    kmeans = KMeans(n_clusters=optimal_k, random_state=0)
    kmeans.fit(data_scaled)

    # Добавление меток кластеров в исходные данные
    df["cluster_label"] = kmeans.labels_

    # Интерпретация результатов
    cluster_centers = scaler.inverse_transform(
        kmeans.cluster_centers_
    )  # Преобразование центроидов обратно в исходные значения
    cluster_labels = ["Cluster {}".format(i) for i in range(optimal_k)]
    interpretation_data = pd.DataFrame(cluster_centers, columns=selected_columns)
    interpretation_data.insert(0, "Cluster Label", cluster_labels)

    # Явные типы данных для каждого столбца
    dtypes = {
        "Cluster Label": "object",  # или int, если номер кластера целое число
        "AVG(ships_killed)": "float64",
        "AVG(planes_killed)": "float64",
        "AVG(damage)": "float64",
        "AVG(team_damage)": "float64",
        "AVG(received_damage)": "float64",
        "AVG(regen_hp)": "float64",
        "AVG(is_alive)": "float64",
        "AVG(credits)": "float64",
        "AVG(exp)": "float64",
    }

    # Применение явных типов данных к DataFrame
    interpretation_data = interpretation_data.astype(dtypes)

    # Округление значений в DataFrame до двух знаков после запятой
    interpretation_data = interpretation_data.round(2)

    # Вывод DataFrame с интерпретацией
    print(f"game_mode: {str(game_mode[0])}")
    print(interpretation_data)

    # Сохранение классификации кораблей в файл формата Excel (.xlsx)
    filename_xlsx = f"../task1_2/data_proc/classification_ships{optimal_k}_{str(game_mode[0])}{postfix}.xlsx"
    interpretation_data.to_excel(filename_xlsx, index=False)

    # Добавление меток кластеров в исходные данные
    df["cluster_label"] = kmeans.labels_

    # Выбор переменных для классификации
    features = [
        "AVG(ships_killed)",
        "AVG(planes_killed)",
        "AVG(damage)",
        "AVG(team_damage)",
        "AVG(received_damage)",
        "AVG(regen_hp)",
        "AVG(is_alive)",
        "AVG(credits)",
        "AVG(exp)",
    ]

    target = "cluster_label"

    # Разделение данных на обучающий и тестовый наборы
    X_train, X_test, y_train, y_test = train_test_split(
        df[features], df[target], test_size=0.2, random_state=0
    )

    # Создание и обучение классификационной модели
    classifier = LogisticRegression()
    classifier.fit(X_train, y_train)

    # Сохранение модели в файл
    model_filename = f"../task1_2/data_proc/logistic_regression_model{optimal_k}_{str(game_mode[0])}{postfix}.joblib"
    joblib.dump(classifier, model_filename)

    # Прогнозирование классов на тестовом наборе данных
    y_pred = classifier.predict(X_test)

    # Вывод отчета о классификации
    report = classification_report(y_test, y_pred)
    print(report)

    loaded_model = joblib.load(model_filename)

    # Пример классификации корабля по конкретной записи в таблице arena_members
    query = "SELECT AVG(ships_killed), AVG(planes_killed), AVG(damage), AVG(team_damage), AVG(received_damage), AVG(regen_hp), AVG(is_alive), AVG(credits), AVG(exp) FROM arena_members WHERE vehicle_type_id = 4289640432"
    cursor.execute(query)
    data = cursor.fetchall()

    # Создаем DataFrame из полученных данных
    columns = [
        "AVG(ships_killed)",
        "AVG(planes_killed)",
        "AVG(damage)",
        "AVG(team_damage)",
        "AVG(received_damage)",
        "AVG(regen_hp)",
        "AVG(is_alive)",
        "AVG(credits)",
        "AVG(exp)",
    ]
    df = pd.DataFrame(data, columns=columns)

    # Масштабирование данных
    data_scaled = scaler.transform(df)

    # Классификация записи
    predicted_cluster = loaded_model.predict(data_scaled)
    print(f"корабль принадлежит классу эффективности {predicted_cluster}")
