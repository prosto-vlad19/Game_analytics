import warnings

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

warnings.filterwarnings("ignore")

# Подключение к базе данных
conn = sqlite3.connect('../data/Dataset.db')
cursor = conn.cursor()

# запрос 1: Среднее количество уничтоженных кораблей по уровням техники
query_mean_ships_killed_by_lvl = "SELECT item_level,AVG(ships_killed) \
FROM arena_members \
INNER JOIN glossary_ships \
ON arena_members.vehicle_type_id = glossary_ships.item_cd \
GROUP BY item_level \
ORDER BY AVG(ships_killed) DESC"
cursor.execute(query_mean_ships_killed_by_lvl)
data = cursor.fetchall()

# Создание DataFrame из полученных данных
columns = ['item_level', 'average_ships_killed']
df = pd.DataFrame(data, columns=columns)

# Запись данных в файл CSV
df.to_csv('../task1_2/data_proc/mean_ships_killed_by_lvl.csv', index=False)

# Построение столбчатой диаграммы
plt.bar(df['item_level'], df['average_ships_killed'])
plt.xlabel('Item Level')
plt.ylabel('Average Ships Killed')
plt.title('Average Ships Killed by Item Level')
plt.savefig("../task1_2/pictures/mean_ships_killed_by_lvl.csv'.png")
plt.show()

# запрос 2: максимальные среднее количество уничтоженных кораблей по уровню и названию корабля
query_max_mean_ships_killed_by_lvl_and_name = "SELECT t.item_level, t.item_name, t.avg_ships_killed \
FROM ( \
    SELECT item_level, item_name, AVG(ships_killed) as avg_ships_killed \
    FROM arena_members \
    INNER JOIN glossary_ships \
        ON arena_members.vehicle_type_id = glossary_ships.item_cd \
    GROUP BY item_level, item_name \
) AS t \
INNER JOIN ( \
    SELECT item_level, MAX(avg_ships_killed) AS max_avg_ships_killed \
    FROM ( \
        SELECT item_level, item_name, AVG(ships_killed) as avg_ships_killed \
        FROM arena_members \
        INNER JOIN glossary_ships \
            ON arena_members.vehicle_type_id = glossary_ships.item_cd \
        GROUP BY item_level, item_name \
    ) AS subquery \
    GROUP BY item_level \
) AS max_avg \
    ON t.item_level = max_avg.item_level \
    AND t.avg_ships_killed = max_avg.max_avg_ships_killed \
ORDER BY t.item_level \
"
cursor.execute(query_max_mean_ships_killed_by_lvl_and_name)
data = cursor.fetchall()

# Создание DataFrame из полученных данных
columns = ['item_level', 'item_name', 'avg_ships_killed']
df = pd.DataFrame(data, columns=columns)

# Запись данных в файл CSV
df.to_csv('../task1_2/data_proc/max_mean_ships_killed_by_lvl_and_name.csv', index=False)

# Построение графика
plt.figure(figsize=(10, 6))
plt.bar(df.index, df['avg_ships_killed'])
plt.xlabel('Item')
plt.ylabel('Average Ships Killed')
plt.title('Max Average Ships Killed by Item Level and Name')
# Установка позиций и подписей для оси x
plt.xticks(df.index, [f"{item_name}\n(Level {item_level})" for item_name, item_level in zip(df['item_name'], df['item_level'])], rotation=90)
plt.tight_layout()
plt.savefig("../task1_2/pictures/max_mean_ships_killed_by_lvl_and_name.png")
plt.show()

#запрос 3: максимальные среднее количество уничтоженных кораблей по классу и названию корабля
query_max_mean_ships_killed_by_class_and_name = "SELECT t.item_class, t.item_name, t.avg_ships_killed \
FROM ( \
    SELECT item_class, item_name, AVG(ships_killed) as avg_ships_killed \
    FROM arena_members \
    INNER JOIN glossary_ships \
        ON arena_members.vehicle_type_id = glossary_ships.item_cd \
    GROUP BY item_class, item_name \
) AS t \
INNER JOIN ( \
    SELECT item_class, MAX(avg_ships_killed) AS max_avg_ships_killed \
    FROM ( \
        SELECT item_class, item_name, AVG(ships_killed) as avg_ships_killed \
        FROM arena_members \
        INNER JOIN glossary_ships \
            ON arena_members.vehicle_type_id = glossary_ships.item_cd \
        GROUP BY item_class, item_name \
    ) AS subquery \
    GROUP BY item_class \
) AS max_avg \
    ON t.item_class = max_avg.item_class \
    AND t.avg_ships_killed = max_avg.max_avg_ships_killed \
ORDER BY t.item_class \
"
cursor.execute(query_max_mean_ships_killed_by_class_and_name)
data = cursor.fetchall()

# Создание DataFrame из полученных данных
columns = ['item_class', 'item_name', 'avg_ships_killed']
df = pd.DataFrame(data, columns=columns)

# # Запись данных в файл CSV
df.to_csv('../task1_2/data_proc/max_mean_ships_killed_by_class_and_name.csv', index=False)

# Построение графика
plt.figure(figsize=(10, 6))
plt.bar(df.index, df['avg_ships_killed'])
plt.xlabel('Item')
plt.ylabel('Average Ships Killed')
plt.title('Average Ships Killed by Item Class and Name')
# Установка позиций и подписей для оси x
plt.xticks(df.index, [f"{item_name}\n({item_class})" for item_name, item_class in zip(df['item_name'], df['item_class'])], rotation=90)
plt.tight_layout()
plt.savefig("../task1_2/pictures/max_mean_ships_killed_by_class_and_name.png")
plt.show()