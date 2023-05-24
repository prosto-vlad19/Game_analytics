import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import sqlite3
import os
import joblib

# Подключение к базе данных
conn = sqlite3.connect('../data/Dataset.db')
cursor = conn.cursor()

query = "SELECT vehicle_type_id,AVG(ships_killed),AVG(planes_killed),AVG(damage),\
AVG(team_damage),AVG(received_damage),AVG(regen_hp),AVG(is_alive),\
AVG(credits),AVG(exp)\
FROM arena_members \
GROUP BY vehicle_type_id"
cursor.execute(query)
data = cursor.fetchall()

# Создаем DataFrame из полученных данных
columns = ['vehicle_type_id','AVG(ships_killed)', 'AVG(planes_killed)', 'AVG(damage)', 'AVG(team_damage)', 'AVG(received_damage)', 'AVG(regen_hp)', 'AVG(is_alive)', 'AVG(credits)', 'AVG(exp)']
df = pd.DataFrame(data, columns=columns)

# Выбор необходимых столбцов
selected_columns = ['AVG(ships_killed)', 'AVG(planes_killed)', 'AVG(damage)', 'AVG(team_damage)', 'AVG(received_damage)', 'AVG(regen_hp)', 'AVG(is_alive)', 'AVG(credits)', 'AVG(exp)']
data_selected = df[selected_columns]

#TODO продумать нормализацию
# Масштабирование данных
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_selected)

# Определение оптимального количества кластеров
inertia = []
for k in range(1, 15):
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(data_scaled)
    inertia.append(kmeans.inertia_)

# Визуализация методом локтя
plt.plot(range(1, 15), inertia)
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia')
plt.title('Elbow Method')
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
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Method')
plt.show()

# Применение метода K-средних с оптимальным количеством кластеров
k = 3
kmeans = KMeans(n_clusters=k, random_state=0)
kmeans.fit(data_scaled)

# Добавление меток кластеров в исходные данные
df['cluster_label'] = kmeans.labels_


# Интерпретация результатов
cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)  # Преобразование центроидов обратно в исходные значения
cluster_labels = ['Cluster {}'.format(i) for i in range(k)]
interpretation_data = pd.DataFrame(cluster_centers, columns=selected_columns)
interpretation_data.insert(0, 'Cluster Label', cluster_labels)

# Вывод DataFrame с интерпретацией
print(interpretation_data)

# Добавление меток кластеров в исходные данные
df['cluster_label'] = kmeans.labels_

# Выбор переменных для классификации
features = ['AVG(ships_killed)', 'AVG(planes_killed)', 'AVG(damage)', 'AVG(team_damage)', 'AVG(received_damage)', 'AVG(regen_hp)', 'AVG(is_alive)', 'AVG(credits)', 'AVG(exp)']

target = 'cluster_label'

# Разделение данных на обучающий и тестовый наборы
X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=0)

# Создание и обучение классификационной модели
classifier = LogisticRegression()
classifier.fit(X_train, y_train)

# Сохранение модели в файл
model_filename = '../task1_2/data_proc/logistic_regression_model.joblib'
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
columns = ['AVG(ships_killed)', 'AVG(planes_killed)', 'AVG(damage)', 'AVG(team_damage)', 'AVG(received_damage)', 'AVG(regen_hp)', 'AVG(is_alive)', 'AVG(credits)', 'AVG(exp)']
df = pd.DataFrame(data, columns=columns)

# Масштабирование данных
data_scaled = scaler.transform(df)

# Классификация записи
predicted_cluster = loaded_model.predict(data_scaled)
print(f"корабль принадлежит классу эффективности {predicted_cluster}")