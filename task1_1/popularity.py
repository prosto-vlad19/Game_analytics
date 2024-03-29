import csv
import sqlite3
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Выбор режима аналитики - для всех игороков (full) или не ботов (no_bots)
mode = "no_bots"

if mode == "full":
    postfix = ""
    where = "True"
    title = "Все игроки"

if mode == "no_bots":
    postfix = "_no_bots"
    where = "account_db_id >= 0"
    title = "Игроки без ботов"

# Подключение к базе данных
conn = sqlite3.connect("../data/Dataset.db")
cursor = conn.cursor()
# проверка на наличие некорректных данных
query_checking_for_types_and_not_positive = """
SELECT *
FROM arenas
WHERE 
typeof(arena_id) = NOT 'integer'
OR typeof(periphery_id) = NOT 'integer'
OR typeof(winner_team_id) = NOT 'integer'
OR typeof(start_dt) = NOT 'TEXT'
OR typeof(duration_sec) = NOT 'integer'
OR typeof(map_type_id) = NOT 'integer'
OR typeof(team_build_type_id) = NOT 'integer'
OR typeof(battle_level_id) = NOT 'integer'
OR start_dt <=0
OR duration_sec <= 0
"""

cursor.execute(query_checking_for_types_and_not_positive)
data_checking_for_types_and_not_positive = cursor.fetchall()

if (len(data_checking_for_types_and_not_positive)) == 0:
    print("нет ошибок по типу данных и нет не положительных  значения в столбцах")
else:
    print(
        "!!! ЕСТЬ ошибки по типу данных или по не положительным значениям в столбцах, требуется очистка"
    )

# Запрос 1: определение количества уникальных значений в столбце "team_build_type_id"
unique_modes_query = "SELECT COUNT(DISTINCT team_build_type_id) FROM arenas"
cursor.execute(unique_modes_query)
unique_modes_count = cursor.fetchone()[0]
print("Количество различных игровых режимов:", unique_modes_count)

# Запрос 2 NEW : подсчет количества записей для каждого игрового режима
count_modes_query = f"""
SELECT cat_name, COUNT(*) as count
FROM catalog_items
INNER JOIN arenas
ON arenas.team_build_type_id = catalog_items.cat_value
JOIN arena_members
ON arenas.arena_id = arena_members.arena_id
AND arenas.periphery_id = arena_members.periphery_id
WHERE {where}
AND catalog_items.cat_type = "BATTLE_TYPE" 
GROUP BY team_build_type_id

"""
cursor.execute(count_modes_query)
count_maps_results = cursor.fetchall()

# Вывод результатов
print("Количество записей для каждого игрового режима:")
for row in count_maps_results:
    mode_id, count = row
    print("Режим", mode_id, ": ", count, " записей")

# Разделение результатов на два списка: режимы и количество записей
modes = [row[0] for row in count_maps_results]
counts = [row[1] for row in count_maps_results]

# Создание графика с количеством записей для каждого игрового режима
plt.figure(figsize=(10, 6))
plt.bar(modes, counts)

# Добавьте аннотации (подписи значений) к каждому столбцу
for i in range(len(modes)):
    plt.annotate(f"{counts[i]:.0f}", (modes[i], counts[i]), ha="center", va="bottom")

plt.xlabel("Игровой режим")
plt.ylabel("Количество записей")
plt.title(f"Популярность игровых режимов.{title}")
plt.yscale("log")
plt.savefig(f"../task1_1/pictures/numb_of_rec_for_each_game_mode{postfix}.png")
plt.show()

# Сохранение результатов в файл CSV
filename = f"../task1_1/data_proc/numb_of_rec_for_each_game_mode{postfix}.csv"
with open(filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Игровой режим", "Количество записей"])
    for row in count_maps_results:
        writer.writerow(row)


print("Результаты сохранены в файл", filename)

# Запрос 3 new : получение среднего количества заработанных опыта,
# кредитов и количество записей для каждого игрового режима

bot_count_query = f"""
SELECT cat_name, AVG(exp) as avg_experience, AVG(credits) as avg_credits
FROM catalog_items
JOIN arenas
ON arenas.team_build_type_id = catalog_items.cat_value
JOIN arena_members
ON arenas.arena_id = arena_members.arena_id
AND arenas.periphery_id = arena_members.periphery_id
WHERE {where}
AND catalog_items.cat_type = "BATTLE_TYPE" 
GROUP BY team_build_type_id
"""

cursor.execute(bot_count_query)
avg_results = cursor.fetchall()

# Join результатов двух запросов по team_build_type_id
merged_results = []
for avg_row in avg_results:
    mode_id = avg_row[0]
    avg_exp = avg_row[1]
    avg_credits = avg_row[2]
    count = next((row[1] for row in count_maps_results if row[0] == mode_id), 0)
    merged_results.append((mode_id, avg_exp, avg_credits, count))

# Вывод объединенных результатов
print(
    "Среднее количество заработанных опыта, кредитов и количество"
    "записей для каждого игрового режима:"
)
for row in merged_results:
    mode_id, avg_exp, avg_credits, count = row
    print("Режим", mode_id)
    print("Средний опыт:", avg_exp)
    print("Средние кредиты:", avg_credits)
    print("Количество записей:", count)
    print()

# Создание DataFrame из объединенных результатов
df = pd.DataFrame(
    merged_results,
    columns=["Игровой режим", "Средний опыт", "Средние кредиты", "Количество записей"],
)


# Построение диаграммы
fig, ax = plt.subplots(figsize=(12, 8))  # Увеличьте размер графика
bar_width = 0.25

x = np.arange(len(df["Игровой режим"]))
ax.set_yscale("log")
bar1 = ax.bar(x, df["Средний опыт"], width=bar_width, label="Средний опыт")
bar2 = ax.bar(
    x + bar_width, df["Средние кредиты"], width=bar_width, label="Средние кредиты"
)
bar3 = ax.bar(
    x + 2 * bar_width,
    df["Количество записей"],
    width=bar_width,
    label="Количество записей",
)

ax.set_xlabel("Игровой режим")
ax.set_ylabel("Значения")
ax.set_title(f"Статистика игровых режимов.{title}")
ax.set_xticks(x + bar_width)
ax.set_xticklabels(df["Игровой режим"], rotation=45)
ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

# Добавьте аннотации (подписи значений) к каждому столбцу
for bar in [bar1, bar2, bar3]:
    for rect in bar:
        height = rect.get_height()
        ax.annotate(
            f"{int(height):d}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
        )

plt.tight_layout()
plt.savefig(f"../task1_1/pictures/avg_exp_and_cred_for_each_game_mode{postfix}.png")
plt.show()

# Сохранение таблицы с результатами в файл
filename = f"../task1_1/data_proc/avg_exp_and_cred_for_each_game_mode{postfix}.csv"
with open(filename, "w", encoding="utf-8-sig") as file:
    # Сохранение датафрейма в файл
    df.to_csv(filename, index=False, encoding="utf-8-sig")
print("Таблица с результатами сохранена в файл", filename)


# Запрос 4 new: получение средней доли ботов для каждого игрового режима
bot_query = f"""
SELECT cat_name, AVG(CASE WHEN account_db_id < 0 THEN 1 ELSE 0 END)
as avg_bots
FROM catalog_items
JOIN arenas
ON arenas.team_build_type_id = catalog_items.cat_value
JOIN arena_members
ON arenas.arena_id = arena_members.arena_id
AND arenas.periphery_id = arena_members.periphery_id
WHERE catalog_items.cat_type = "BATTLE_TYPE" 
GROUP BY team_build_type_id
"""

# Выполнение запроса
cursor.execute(bot_query)
bot_results = cursor.fetchall()

# Вывод результатов
print("Средняя доля ботов для каждого игрового режима:")
for row in bot_results:
    mode_id, avg_bots = row
    print("Режим", mode_id)
    print("Средняя доля ботов:", avg_bots)
    print()

bot_results_new = []

for bot_row, record_row in zip(bot_results, count_maps_results):
    mode_id, avg_bots = bot_row
    mode_id_record, count = record_row
    if mode_id == mode_id_record:
        bot_results_new.append((mode_id, avg_bots, count))

bot_results_new = pd.DataFrame(
    bot_results_new,
    columns=["Игровой режим", "Средняя доля ботов", "Количество записей"],
)

fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(bot_results_new))
bar_width = 0.35

bar1 = ax.bar(
    x - bar_width / 2,
    bot_results_new["Средняя доля ботов"],
    width=bar_width,
    label="Средняя доля ботов",
)
bar2 = ax.bar(
    x + bar_width / 2,
    bot_results_new["Количество записей"],
    width=bar_width,
    label="Количество записей",
    alpha=0.5,
)

ax.set_yscale("log")

ax.set_xlabel("Игровой режим")
ax.set_ylabel("Значения")
ax.set_title("Статистика ботов и записей в игровых режимах")
ax.set_xticks(x)
ax.set_xticklabels(bot_results_new["Игровой режим"], rotation=45)
ax.legend()

# Добавьте аннотации (подписи значений) к каждому столбцу
for bar in [bar1, bar2]:
    for rect in bar:
        height = rect.get_height()
        ax.annotate(
            f"{height:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
        )

plt.tight_layout()
plt.savefig(
    f"../task1_1/pictures/avg_proportion_of_bots_for_each_game_mode.png"
)
plt.show()


# Сохранение результатов в файл CSV
filename = "../task1_1/data_proc/avg_proportion_of_bots_for_each_game_mode.csv"
with open(filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Игровой режим", "Средняя доля ботов", "Количество записей"])
    for row in bot_results_new:
        writer.writerow(row)

print("Результаты сохранены в файл", filename)


# Запрос 5 new: получение средней продолжительности боя
# и количество записей для каждого игрового режима
query_avg_dur = f"""
SELECT cat_name,AVG(duration_sec) as avg_duration, COUNT(*)
FROM catalog_items
JOIN arenas
ON arenas.team_build_type_id = catalog_items.cat_value 
JOIN arena_members 
ON arenas.arena_id = arena_members.arena_id
AND arenas.periphery_id = arena_members.periphery_id
WHERE {where}
AND catalog_items.cat_type = "BATTLE_TYPE" 
GROUP BY cat_name
"""

# Выполнение запроса
cursor.execute(query_avg_dur)
results = cursor.fetchall()

# Вывод результатов
print("Средняя продолжительность боя и количество записей для каждого игрового режима:")
for row in results:
    mode_id, avg_duration, count = row
    print("Режим", mode_id)
    print("Средняя продолжительность боя (в секундах):", avg_duration)
    print("Количество записей:", count)
    print()

# Построение диаграммы
df = pd.DataFrame(
    results,
    columns=["Игровой режим", "Средняя продолжительность боя", "Количество записей"],
)


fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(df))

# Ширина каждого столбца
bar_width = 0.35

# Создайте двойные столбцы для каждого игрового режима
bar1 = ax.bar(
    x - bar_width / 2,
    df["Средняя продолжительность боя"],
    width=bar_width,
    label="Средняя продолжительность боя",
)
bar2 = ax.bar(
    x + bar_width / 2,
    df["Количество записей"],
    width=bar_width,
    label="Количество записей",
    alpha=0.5,
)

# Добавьте логарифмическую шкалу по оси y
ax.set_yscale("log")

# Настройка внешнего вида графика
ax.set_xlabel("Игровой режим")
ax.set_ylabel("Значения (логарифмическая шкала)")
ax.set_title(f"Средняя продолжительность боя и количество записей в игровых режимах.{title}")
ax.set_xticks(x)
ax.set_xticklabels(df["Игровой режим"], rotation=45)
ax.legend()

# Добавьте аннотации (подписи значений) к каждому столбцу
for bar in [bar1, bar2]:
    for rect in bar:
        height = rect.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
        )

plt.tight_layout()

# Сохраните график
plt.savefig(
    f"../task1_1/pictures/avg_battle_durat_and_numb_of_rec_for_each_game_mode{postfix}.png"
)

# Отобразите график
plt.show()


# Сохранение результатов в файл CSV
filename = f"../task1_1/data_proc/avg_battle_durat_and_numb_of_rec_for_each_game_mode{postfix}.csv"
with open(filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        ["Игровой режим", "Средняя продолжительность боя", "Количество записей"]
    )
    for row in results:
        writer.writerow(row)

print("Результаты сохранены в файл", filename)

# Запрос 6: получение дня недели боя и подсчета количества записей
query_day = f"""
SELECT CASE WHEN strftime('%w', start_dt) = '0' THEN '7'
ELSE strftime('%w', start_dt) END as weekday, COUNT(*) as count
FROM arenas
JOIN arena_members 
ON arenas.arena_id = arena_members.arena_id
AND arenas.periphery_id = arena_members.periphery_id
WHERE {where}
GROUP BY weekday
"""

# Выполнение запроса
cursor.execute(query_day)
results = cursor.fetchall()

# Вывод результатов
print("День недели боя и количество записей:")
for row in results:
    weekday, count = row
    print("День недели", weekday)
    print("Количество записей:", count)
    print()

# Построение диаграммы
df = pd.DataFrame(results, columns=["День недели", "Количество записей"])
fig, ax = plt.subplots()
x = df["День недели"]
ax.bar(x, df["Количество записей"])

ax.set_xlabel("День недели")
ax.set_ylabel("Количество записей")
ax.set_title(f"Статистика записей по дням недели.{title}")
ax.set_xticks(x)
ax.set_xticklabels(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"])

# Добавьте аннотации (подписи значений) к каждому столбцу
for rect in ax.patches:
    height = rect.get_height()
    ax.annotate(
        f"{int(height)}",
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
    )

plt.tight_layout()
plt.savefig(f"../task1_1/pictures/numb_of_rec_by_day_of_the_week{postfix}.png")
plt.show()


# Сохранение результатов в файл CSV
filename = f"../task1_1/data_proc/numb_of_rec_by_day_of_the_week{postfix}.csv"
with open(filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["День недели", "Количество записей"])
    for row in results:
        writer.writerow(row)

print("Результаты сохранены в файл", filename)


# Запрос 7: подсчет количества записей для каждой карты
count_maps_query = f"""
   SELECT map_type_id, COUNT(*) as count
FROM arenas
JOIN arena_members 
ON arenas.arena_id = arena_members.arena_id
AND arenas.periphery_id = arena_members.periphery_id
WHERE {where}
GROUP BY map_type_id
"""
cursor.execute(count_maps_query)
count_maps_results = cursor.fetchall()

# Вывод результатов
print("Карта и количество записей:")
for row in count_maps_results:
    map_id, count = row
    print("Карта ID:", map_id)
    print("Количество записей:", count)
    print()


df = pd.DataFrame(count_maps_results, columns=["Карта ID", "Количество записей"])

plt.figure(figsize=(15, 7))
x = df["Карта ID"]
y = df["Количество записей"]

# Создаем гистограмму
plt.bar(x, y, label="Количество записей")

# Добавляем медианное значение
median_value = np.median(y)
plt.axhline(
    y=median_value, color="r", linestyle="--", label=f"Медиана: {int(median_value)}"
)

plt.xlabel("Карта ID")
plt.ylabel("Количество записей")
plt.title(f"Статистика записей по картам.{title}")
plt.xticks(x)
plt.legend()

# Добавьте серую сетку
plt.grid(axis="y", linestyle="--", alpha=0.7, color="gray")

plt.tight_layout()
plt.savefig(f"../task1_1/pictures/numb_of_rec_for_each_map{postfix}.png")
plt.show()


# Сохранение результатов в файл CSV
filename = f"../task1_1/data_proc/numb_of_rec_for_each_map{postfix}.csv"
with open(filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Карта ID", "Количество записей"])
    for row in count_maps_results:
        writer.writerow(row)

print("Результаты сохранены в файл", filename)

# Запрос 8: подсчет количества записей для каждого уровня боя
count_levels_query = f"""
       SELECT battle_level_id, COUNT(*) as count 
    FROM arenas 
    JOIN arena_members 
    ON arenas.arena_id = arena_members.arena_id
    AND arenas.periphery_id = arena_members.periphery_id
    WHERE {where}
    GROUP BY battle_level_id
"""
cursor.execute(count_levels_query)
count_lv_results = cursor.fetchall()

# Построение диаграммы
df = pd.DataFrame(count_lv_results, columns=["Уровень боя", "Количество записей"])

plt.figure(figsize=(10, 6))
x = df["Уровень боя"]
y = df["Количество записей"]

plt.bar(x, y)
plt.xlabel("Уровень боя")
plt.ylabel("Количество записей")
plt.title(f"Статистика записей по уровням боя.{title}")

# Добавляем подписи значений
for i, v in enumerate(y):
    plt.text(x[i], v, str(v), ha="center", va="bottom")

plt.tight_layout()
plt.savefig(f"../task1_1/pictures/numb_of_rec_for_each_battle_level{postfix}.png")
plt.show()


# Сохранение результатов в файл CSV
filename = f"../task1_1/data_proc/numb_of_rec_for_each_battle_level{postfix}.csv"
with open(filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Уровень боя", "Количество записей"])
    for row in count_lv_results:
        writer.writerow(row)

print("Результаты сохранены в файл", filename)

# Закрытие соединения с базой данных
cursor.close()
conn.close()
