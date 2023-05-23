import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sqlite3
from sklearn.preprocessing import RobustScaler

# Подключение к базе данных
conn = sqlite3.connect('Dataset.db')
cursor = conn.cursor()

# Извлекаем данные из таблицы arena_members
query = "SELECT ships_killed, planes_killed, damage, received_damage, is_alive, credits, exp FROM arena_members"
cursor.execute(query)
data = cursor.fetchall()

# Создаем DataFrame из полученных данных
columns = ['ships_killed', 'planes_killed', 'damage', 'received_damage', 'is_alive', 'credits', 'exp']
df = pd.DataFrame(data, columns=columns)
print(df)

# Select the columns for normalization
columns_to_normalize = ['ships_killed', 'planes_killed', 'damage', 'received_damage', 'credits', 'exp']

# Построение box plot для каждого столбца данных
plt.figure(figsize=(10, 6))
df.boxplot(column=columns_to_normalize)
plt.xticks(rotation=45)
plt.title('Box Plot of Data')
plt.show()

#много выбросов демонстрирует boxplot - выберем RobustScaler, как более устойчивый к выбросам метод
# Initialize the RobustScaler
scaler = RobustScaler()

# Perform robust scaling on the selected columns
df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])

# Print the normalized DataFrame
print(df)

# Разделяем данные на независимые переменные (X) и зависимую переменную (y)
X = df.drop('ships_killed', axis=1)
y = df['ships_killed']

# Обучаем линейную регрессию
regression = LinearRegression()
regression.fit(X, y)

# Выводим важность каждой независимой переменной
importance = regression.coef_
print(importance)

# Визуализируем результаты
plt.figure(figsize=(10, 6))
plt.bar(columns[1:], importance)
plt.xlabel('Independent Variables')
plt.ylabel('Coefficient')
plt.title('Importance of Independent Variables')
plt.xticks(rotation=45)
plt.show()

# Извлекаем данные из таблицы arena_members
query = "SELECT ships_killed, planes_killed, damage, received_damage, is_alive, credits, exp FROM arena_members"
cursor.execute(query)
data = cursor.fetchall()

# Создаем DataFrame из полученных данных
columns = ['ships_killed', 'planes_killed', 'damage', 'received_damage', 'is_alive', 'credits', 'exp']
df = pd.DataFrame(data, columns=columns)
print(df)

# Select the columns for normalization
columns_to_normalize = ['ships_killed', 'planes_killed', 'damage', 'received_damage', 'credits', 'exp']

# Initialize the StandardScaler
scaler = RobustScaler()

# Perform standardization on the selected columns
df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])

# Print the standardized DataFrame
print(df)

# Разделяем данные на независимые переменные (X) и зависимые переменные (y)
X = df.drop(['credits', 'exp'], axis=1)
y = df[['credits', 'exp']]

# Обучаем множественную линейную регрессию
regression = LinearRegression()
regression.fit(X, y)

# Выводим важность каждой независимой переменной
importance = regression.coef_
print(importance)

# Построение графика
plt.figure(figsize=(10, 6))
plt.bar(X.columns, importance[0], label='Credits')
plt.bar(X.columns, importance[1], label='Experience')
plt.xlabel('Independent Variables')
plt.ylabel('Coefficient')
plt.title('Importance of Independent Variables')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Отображение графика
plt.show()


# Закрываем соединение с базой данных
conn.close()
