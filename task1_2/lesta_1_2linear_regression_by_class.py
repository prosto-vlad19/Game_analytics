import sqlite3
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import RobustScaler

warnings.filterwarnings("ignore")

# Попробуем сделать линейную регрессию для каждого класса кораблей в отдельности

# Подключение к базе данных
conn = sqlite3.connect("../data/Dataset.db")
cursor = conn.cursor()

# Извлекаем данные из таблицы arena_members
query_checking_for_types_and_nulls = """
SELECT *
FROM glossary_ships
WHERE typeof(item_class) != 'text' OR LENGTH(item_class) <= 0
"""
cursor.execute(query_checking_for_types_and_nulls)
data_checking_for_types_and_nulls = cursor.fetchall()

if (len(data_checking_for_types_and_nulls)) == 0:
    print("нет ошибок по типу данных и нет отрицательных значения в столбцах")
else:
    print(
        "!!! ЕСТЬ ошибки по типу данных или по отрицательным значениям в столбцах, требуется очистка"
    )

query_different_class = "SELECT distinct(item_class) \
FROM arena_members \
INNER JOIN glossary_ships \
ON arena_members.vehicle_type_id = glossary_ships.item_cd \
WHERE typeof(item_class) = 'text' AND LENGTH(item_class) > 0 \
"
cursor.execute(query_different_class)
classes = cursor.fetchall()

# Проходим по каждому классу
for class_data in classes:
    # Извлекаем данные из таблиц для текущего класса кораблей
    query_class = f"SELECT ships_killed, planes_killed, damage, team_damage, \
                    received_damage, regen_hp, is_alive, credits, exp \
                    FROM arena_members \
                    INNER JOIN glossary_ships \
                    ON arena_members.vehicle_type_id = glossary_ships.item_cd \
                    WHERE typeof(item_class) = 'text' AND LENGTH(item_class) > 0 AND typeof(account_db_id) = 'integer' AND item_class = '{str(class_data[0])}' "

    cursor.execute(query_class)
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
    df_class = pd.DataFrame(data, columns=columns)

    scaler = RobustScaler()
    # Выполняем нормализацию данных
    df_class[columns] = scaler.fit_transform(df_class[columns])
    df_copy = df_class.copy()

    # Разделяем данные на независимые переменные (X) и зависимую переменную (y)
    X = df_class.drop("ships_killed", axis=1)
    y = df_class["ships_killed"]

    # Обучаем линейную регрессию
    regression = LinearRegression()
    regression.fit(X, y)

    # Выводим важность каждой независимой переменной
    importance = regression.coef_
    print(
        f"Коэффициенты линейной регрессии для класса {str(class_data[0])}: {importance}"
    )

    # сохраняем коэффициенты регрессии в файл
    filename = f"../task1_2/data_proc/linear_regression_ships_killed_class_{str(class_data[0])}.csv"
    np.savetxt(filename, importance, delimiter=',', fmt='%.6f')

    # Визуализируем результаты
    plt.figure(figsize=(16, 12))
    plt.subplots_adjust(bottom=0.15, top=0.95)
    plt.bar(columns[1:], importance)
    plt.xticks(fontsize=14, rotation=30)
    plt.yticks(fontsize=16)
    plt.xlabel("Independent Variables", fontsize=18)
    plt.ylabel("Coefficient", fontsize=18)
    plt.title(
        f"Importance of Independent Variables (Class: {str(class_data[0])})",
        fontsize=18,
    )
    plt.savefig(
        f"../task1_2/pictures/linear_regression_ships_killed_class_{str(class_data[0])}.png"
    )
    plt.show()
