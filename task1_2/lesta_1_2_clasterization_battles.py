import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import RobustScaler

# Подключение к базе данных
conn = sqlite3.connect("../data/Dataset.db")
cursor = conn.cursor()

query_checking_for_types_and_nulls = """
SELECT ships_killed, planes_killed, damage, team_damage, received_damage, regen_hp, is_alive, credits, exp
FROM arena_members
WHERE typeof(account_db_id) = 'integer' AND account_db_id >= 0
  AND (
    NOT (typeof(ships_killed) = 'integer' OR  ships_killed >= 0)
    OR NOT (typeof(planes_killed) = 'integer' OR  planes_killed >= 0)
    OR NOT (typeof(damage) = 'integer' OR  damage >= 0)
    OR NOT (typeof(team_damage) = 'integer' OR  team_damage >= 0)
    OR NOT (typeof(received_damage) = 'integer' OR  received_damage >= 0)
    OR NOT (typeof(regen_hp) = 'integer' OR  regen_hp >= 0)
    OR NOT (typeof(is_alive) = 'integer' OR  is_alive >= 0)
    OR NOT (typeof(credits) = 'integer' OR  credits >= 0)
    OR NOT (typeof(exp) = 'integer' OR  exp >= 0)
  )
"""
cursor.execute(query_checking_for_types_and_nulls)
data_checking_for_types_and_nulls = cursor.fetchall()

if(len(data_checking_for_types_and_nulls)) == 0:
    print("нет ошибок по типу данных и нет отрицательных значения в столбцах")
else:
    print("!!! ЕСТЬ ошибки по типу данных или по отрицательным значениям в столбцах, требуется очистка")


query = "SELECT ships_killed, planes_killed, damage, team_damage, received_damage,  regen_hp, is_alive, credits, exp \
FROM arena_members \
WHERE typeof(account_db_id) = 'integer' AND account_db_id >= 0 \
"
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

# Построение box plot для каждого столбца данных
# необходимо для определения способа нормализации

plt.figure(figsize=(12, 9))
plt.subplots_adjust(bottom=0.15, top=0.95)
df.boxplot(column=columns)
plt.xticks(fontsize=14, rotation=30)
plt.yticks(fontsize=16)
plt.title("Box Plot of Data", fontsize=18)
plt.savefig("../task1_2/pictures/box_plot.png")
plt.show()

# Масштабирование данных
scaler = RobustScaler()
data_scaled = scaler.fit_transform(df)

"""
# Определение оптимального количества кластеров
inertia = []
silhouette_scores = []

for k in range(2, 4):
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(data_scaled)

    # Расчет значения силуэта
    labels = kmeans.labels_
    silhouette_avg = silhouette_score(data_scaled, labels)

    # Сохранение значений
    inertia.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_avg)

# Визуализация методом локтя
plt.figure(figsize=(10, 6))
plt.plot(range(2, 11), inertia, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.show()

# Визуализация методом силуэта
plt.figure(figsize=(10, 6))
plt.plot(range(2, 11), silhouette_scores, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Method")
plt.show()
"""


"""
# Использование алгоритма MiniBatchKMeans
inertia_mb = []
silhouette_scores_mb = []
for k in range(2, 4):
    minibatch_kmeans = MiniBatchKMeans(n_clusters=k, random_state=0)
    minibatch_kmeans.fit(data_scaled)

    # Расчет значения силуэта
    labels_mb = minibatch_kmeans.labels_
    silhouette_avg_mb = silhouette_score(data_scaled, labels_mb)

    # Сохранение значений
    inertia_mb.append(minibatch_kmeans.inertia_)
    silhouette_scores_mb.append(silhouette_avg_mb)

# Визуализация методом локтя для MiniBatchKMeans
plt.figure(figsize=(10, 6))
plt.plot(range(2, 4), inertia_mb, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia (MiniBatchKMeans)")
plt.title("Elbow Method")
plt.show()

# Визуализация методом силуэта для MiniBatchKMeans
plt.figure(figsize=(10, 6))
plt.plot(range(2, 14), silhouette_scores_mb, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Score (MiniBatchKMeans)")
plt.title("Silhouette Method")
plt.show()
"""

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
k = 5
kmeans = KMeans(n_clusters=k, random_state=0)
kmeans.fit(data_scaled)

# Добавление меток кластеров в исходные данные
df["cluster_label"] = kmeans.labels_

# Интерпретация результатов
cluster_centers = scaler.inverse_transform(
    kmeans.cluster_centers_
)  # Преобразование центроидов обратно в исходные значения
cluster_labels = ["Cluster {}".format(i) for i in range(k)]
interpretation_data = pd.DataFrame(cluster_centers, columns=columns)
interpretation_data.insert(0, "Cluster Label", cluster_labels)

# Вывод DataFrame с интерпретацией
print(interpretation_data)


filename = "../task1_2/data_proc/clasterization_battle.csv"
with open(filename, "w", encoding="utf-8-sig") as file:
    # Сохранение датафрейма в файл
    interpretation_data.to_csv(filename, index=False, encoding="utf-8-sig")
