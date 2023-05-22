import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sqlite3

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

# Закрываем соединение с базой данных
conn.close()
