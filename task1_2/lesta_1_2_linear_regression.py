import sqlite3
import warnings

import matplotlib.cbook
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import RobustScaler

warnings.filterwarnings(
    "ignore", category=matplotlib.cbook.MatplotlibDeprecationWarning
)

# Подключение к базе данных
conn = sqlite3.connect("../data/Dataset.db")
cursor = conn.cursor()

# Извлекаем данные из таблицы arena_members
query = "SELECT ships_killed, planes_killed, damage,team_damage, received_damage,regen_hp, is_alive, credits, exp FROM arena_members"
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

# Выбираем столбцы, подлежащие нормализации
columns_to_normalize = [
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

# Построение box plot для каждого столбца данных
# необходимо для определения способа нормализации

plt.figure(figsize=(12, 9))
plt.subplots_adjust(bottom=0.15, top=0.95)
df.boxplot(column=columns_to_normalize)
plt.xticks(fontsize=14, rotation=30)
plt.yticks(fontsize=16)
plt.title("Box Plot of Data", fontsize=18)
plt.savefig("../task1_2/pictures/box_plot_linear_regression.png")
plt.show()

# много выбросов демонстрирует boxplot - выберем RobustScaler, как более устойчивый к выбросам метод
scaler = RobustScaler()

# Выполняем robust scaling для выбранных столбцов
df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
df_copy = df.copy()

# Разделяем данные на независимые переменные (X) и зависимую переменную (y)
X = df.drop("ships_killed", axis=1)
y = df["ships_killed"]

# Обучаем линейную регрессию
regression = LinearRegression()
regression.fit(X, y)

# Выводим важность каждой независимой переменной
importance = regression.coef_
print("Коэффициенты линейной регрессии ships_killed:", importance)

# Визуализируем результаты
plt.figure(figsize=(16, 12))
plt.subplots_adjust(bottom=0.15, top=0.95)
plt.bar(columns[1:], importance)
plt.xticks(
    fontsize=14,
    rotation=30,
)
plt.yticks(fontsize=16)
plt.xlabel("Independent Variables", fontsize=18)
plt.ylabel("Coefficient", fontsize=18)
plt.title("Importance of Independent Variables", fontsize=18)
plt.savefig("../task1_2/pictures/linear_regression_ships_killed.png")
plt.show()

# Разделяем данные на независимые переменные (X) и зависимые переменные (y)
X = df_copy.drop(["credits", "exp"], axis=1)
y = df_copy[["credits", "exp"]]

# Обучаем множественную линейную регрессию
regression = LinearRegression()
regression.fit(X, y)

# Выводим важность каждой независимой переменной
importance = regression.coef_
print("Коэффициенты линейной регрессии credits и exp:", importance)

# Построение графика
plt.figure(figsize=(16, 12))
plt.subplots_adjust(bottom=0.15, top=0.95)
plt.bar(X.columns, importance[0], label="Credits")
plt.bar(X.columns, importance[1], label="Experience")
plt.xticks(fontsize=14, rotation=30)
plt.yticks(fontsize=16)
plt.xlabel("Independent Variables", fontsize=18)
plt.ylabel("Coefficient", fontsize=18)
plt.title("Importance of Independent Variables", fontsize=18)
plt.legend(fontsize=18)
plt.savefig("../task1_2/pictures/linear_regression_credits_exp.png")
plt.show()

# Закрываем соединение с базой данных
conn.close()
