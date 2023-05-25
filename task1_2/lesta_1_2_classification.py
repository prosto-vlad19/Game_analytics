import sqlite3
import warnings

import joblib
import matplotlib.pyplot as plt
import numpy as np
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

query = "SELECT vehicle_type_id,AVG(ships_killed),AVG(planes_killed),AVG(damage),\
AVG(team_damage),AVG(received_damage),AVG(regen_hp),AVG(is_alive),\
AVG(credits),AVG(exp)\
FROM arena_members \
GROUP BY vehicle_type_id \
HAVING typeof(account_db_id) = 'integer' AND account_db_id >= 0"
cursor.execute(query)
data = cursor.fetchall()

# Создаем DataFrame из полученных данных
columns = [
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
    np.arange(1, len(selected_columns) + 1), selected_columns, fontsize=14, rotation=30
)
plt.yticks(fontsize=16)
plt.yscale("log")  # Применение логарифмической шкалы по оси y
plt.title("Box Plot of Data (Log Scale)", fontsize=18)
plt.savefig("../task1_2/pictures/box_plot_classification_no_bots.png")
plt.show()

# Масштабирование данных
scaler = RobustScaler()
data_scaled = scaler.fit_transform(data_selected)

# Определение оптимального количества кластеров
inertia = []
for k in range(1, 15):
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(data_scaled)
    inertia.append(kmeans.inertia_)

# Визуализация методом локтя
plt.plot(range(1, 15), inertia)
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.show()

# определение оптимального количества кластеров
silhouette_scores = []
for k in range(2, 15):
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(data_scaled)
    labels = kmeans.labels_
    silhouette_scores.append(silhouette_score(data_scaled, labels))

# визуализация методом силуэта
plt.plot(range(2, 15), silhouette_scores)
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Method")
plt.show()

# Применение метода K-средних с оптимальным количеством кластеров
k = 2
kmeans = KMeans(n_clusters=k, random_state=0)
kmeans.fit(data_scaled)

# Добавление меток кластеров в исходные данные
df["cluster_label"] = kmeans.labels_


# Интерпретация результатов
cluster_centers = scaler.inverse_transform(
    kmeans.cluster_centers_
)  # Преобразование центроидов обратно в исходные значения
cluster_labels = ["Cluster {}".format(i) for i in range(k)]
interpretation_data = pd.DataFrame(cluster_centers, columns=selected_columns)
interpretation_data.insert(0, "Cluster Label", cluster_labels)

# Вывод DataFrame с интерпретацией
print(interpretation_data)

# сохранение классификации кораблей в файл
filename = "../task1_2/data_proc/classification_ships_no_bots.csv"
with open(filename, "w", encoding="utf-8-sig") as file:
    # Сохранение датафрейма в файл
    interpretation_data.to_csv(filename, index=False, encoding="utf-8-sig")

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
model_filename = "../task1_2/data_proc/logistic_regression_model_no_bots.joblib"
joblib.dump(classifier, model_filename)

# Прогнозирование классов на тестовом наборе данных
y_pred = classifier.predict(X_test)

# Вывод отчета о классификации
classification_report = classification_report(y_test, y_pred)
print(classification_report)

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
