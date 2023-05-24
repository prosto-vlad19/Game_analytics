import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Подключение к базе данных
conn = sqlite3.connect("../data/Dataset.db")
cursor = conn.cursor()

query = "SELECT ships_killed, planes_killed, damage, team_damage, received_damage, regen_hp, is_alive, credits, exp FROM arena_members"
cursor.execute(query)
data = cursor.fetchall()

# Создаем DataFrame из полученных данных
columns = [
    "ships_killed",
    "planes_killed",
    "damage",
    "team_damage",
    "received_damage",
    "regen_hp",
    "is_alive",
    "credits",
    "exp",
]
df = pd.DataFrame(data, columns=columns)

# Выбор необходимых столбцов
selected_columns = [
    "ships_killed",
    "planes_killed",
    "damage",
    "team_damage",
    "received_damage",
    "regen_hp",
    "is_alive",
    "credits",
    "exp",
]
data_selected = df[selected_columns]

# Масштабирование данных
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_selected)

# Определение оптимального количества кластеров
inertia = []
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(data_scaled)
    inertia.append(kmeans.inertia_)

# Визуализация методом локтя
plt.plot(range(1, 11), inertia)
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.show()

# Применение метода K-средних с оптимальным количеством кластеров
k = 7
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


filename = "../task1_2/data_proc/clasterization_battle.csv"
with open(filename, "w", encoding="utf-8-sig") as file:
    # Сохранение датафрейма в файл
    interpretation_data.to_csv(filename, index=False, encoding="utf-8-sig")
