import sqlite3
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Suppress all warnings
warnings.filterwarnings("ignore")

# Подключение к базе данных
conn = sqlite3.connect("../data/Dataset.db")
cursor = conn.cursor()

# Выбор режима аналитики - для всех игроков (full) или не ботов (no_bots)
mode = "no_bots"

if mode == "full":
    postfix = ""
    where = "True"

if mode == "no_bots":
    postfix = "_no_bots"
    where = "account_db_id >= 0"


# 1 killed metric
query_killed_alive = f"""
SELECT cat_name,item_name,
AVG((ships_killed + planes_killed) * is_alive) AS avg_metric
FROM catalog_items
JOIN arenas
ON arenas.team_build_type_id = catalog_items.cat_value 
JOIN arena_members 
ON arenas.arena_id = arena_members.arena_id
JOIN glossary_ships 
ON arena_members.vehicle_type_id = glossary_ships.item_cd
WHERE {where}
AND catalog_items.cat_type = "BATTLE_TYPE" 
GROUP BY cat_name, item_name
"""
cursor.execute(query_killed_alive)
data = cursor.fetchall()

columns = ["cat_name", "item_name", "avg_metric"]
df = pd.DataFrame(data, columns=columns)

# Построение гистограмм
for cat_name, group_df in df.groupby("cat_name"):
    if cat_name == "PerfomanceTest":
        continue  # Skip building histogram for "PerformanceTest" category

    plt.figure(figsize=(12, 6))  # Adjust the figure size

    # Top 3 smallest values
    top3_smallest = group_df.nsmallest(3, "avg_metric")
    bars1 = plt.bar(
        top3_smallest["item_name"].astype(str),
        top3_smallest["avg_metric"],
        label="Top 3 Smallest",
        color="blue",
        alpha=0.7,
    )

    # Top 3 largest values
    top3_largest = group_df.nlargest(3, "avg_metric")
    bars2 = plt.bar(
        top3_largest["item_name"].astype(str),
        top3_largest["avg_metric"],
        label="Top 3 Largest",
        color="orange",
        alpha=0.7,
    )

    # Mean value
    mean_value = group_df["avg_metric"].mean()

    # Annotate each bar with its value
    for i, value in enumerate(top3_smallest["avg_metric"]):
        plt.text(
            i,
            value,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            color="black",
            fontsize=8,
        )

    for i, value in enumerate(top3_largest["avg_metric"]):
        plt.text(
            i + len(top3_smallest),
            value,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            color="black",
            fontsize=8,
        )

    # Mean value annotation
    plt.axhline(y=mean_value, color="red", linestyle="--", label="Mean Value")
    plt.text(
        -0.5,  # Смещение в крайнее левое положение
        mean_value,
        f"Mean: {mean_value:.2f}",
        ha="left",
        va="bottom",
        color="black",  # Черный цвет шрифта
        fontsize=10,  # Увеличенный размер шрифта
    )


    # Annotation with metric formula
    formula_annotation = (
        "Formula: AVG((ships_killed + planes_killed) * is_alive)\n"
        "This is the formula for calculating the killed metric."
    )

    # Calculate the height for the formula annotation
    height = max(top3_largest["avg_metric"]) * 1.1
    bbox = dict(boxstyle="round", alpha=0.1)
    plt.annotate(
        formula_annotation,
        xy=(0, 1.02),
        xycoords="axes fraction",
        fontsize=8,
        ha="left",
        va="bottom",
        bbox=bbox,
    )

    # Legend in the upper left corner
    plt.legend(loc="upper left")

    plt.title(f"Killed metric {cat_name}")
    plt.xlabel("item_name")
    plt.ylabel("avg_metric")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels
    plt.tight_layout()  # Adjust layout for better spacing
    plt.savefig(f"../task1_2/pictures/killed_metric_{cat_name}{postfix}.png")
    plt.show()

# 2 damage metric
# Query for average damage and received damage
query_avg_damage = f"""
SELECT cat_name, item_name,
       AVG(damage) AS avg_damage,
       AVG(received_damage) AS avg_received_damage,
       COUNT(*) AS num_records  -- Count the number of records for each ship
FROM catalog_items
JOIN arenas ON arenas.team_build_type_id = catalog_items.cat_value 
JOIN arena_members ON arenas.arena_id = arena_members.arena_id
JOIN glossary_ships ON arena_members.vehicle_type_id = glossary_ships.item_cd
WHERE {where}
AND catalog_items.cat_type = "BATTLE_TYPE" 
GROUP BY cat_name, item_name
"""
cursor.execute(query_avg_damage)
data_avg_damage = cursor.fetchall()

columns_avg_damage = [
    "cat_name",
    "item_name",
    "avg_damage",
    "avg_received_damage",
    "num_records",
]
df_avg_damage = pd.DataFrame(data_avg_damage, columns=columns_avg_damage)

# Calculate new metric: damage / received damage
df_avg_damage["damage_received_ratio"] = (
        df_avg_damage["avg_damage"] / df_avg_damage["avg_received_damage"]
)

# Построение гистограмм для damage_received_ratio по каждой cat_name
for cat_name, group_df in df_avg_damage.groupby("cat_name"):
    if cat_name == "PerfomanceTest":
        continue  # Skip building histogram for "PerformanceTest" category

    plt.figure(figsize=(12, 6))  # Adjust the figure size

    # Check for ships with zero received damage
    zero_received_damage_ships = group_df[group_df["avg_received_damage"] == 0]
    if not zero_received_damage_ships.empty:
        print(f"Ships with zero received damage in {cat_name} category:")
        print(
            zero_received_damage_ships[
                ["item_name", "avg_received_damage", "num_records"]
            ]
        )
        zero_received_damage_ships.to_csv(
            f"../task1_2/data_proc/zero_received_damage_{cat_name}{postfix}.csv",
            index=False,
        )  # Save to CSV

    # Check for ships with zero damage
    zero_damage_ships = group_df[group_df["avg_damage"] == 0]
    if not zero_damage_ships.empty:
        print(f"Ships with zero damage in {cat_name} category:")
        print(zero_damage_ships[["item_name", "avg_damage", "num_records"]])
        zero_damage_ships.to_csv(
            f"../task1_2/data_proc/zero_damage_{cat_name}{postfix}.csv", index=False
        )  # Save to CSV

    # Remove infinite values for damage_received_ratio
    group_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    group_df.dropna(subset=["damage_received_ratio"], inplace=True)

    # Top 3 smallest values for damage_received_ratio
    top3_smallest_ratio = group_df.nsmallest(3, "damage_received_ratio")
    bars1 = plt.bar(
        top3_smallest_ratio["item_name"].astype(str),
        top3_smallest_ratio["damage_received_ratio"],
        label="Top 3 Smallest (damage_received_ratio)",
        color="blue",
        alpha=0.7,
    )

    # Top 3 largest values for damage_received_ratio
    top3_largest_ratio = group_df.nlargest(3, "damage_received_ratio")
    bars2 = plt.bar(
        top3_largest_ratio["item_name"].astype(str),
        top3_largest_ratio["damage_received_ratio"],
        label="Top 3 Largest (damage_received_ratio)",
        color="orange",
        alpha=0.7,
    )

    # Mean value for damage_received_ratio
    mean_ratio_value = group_df["damage_received_ratio"].mean()

    # Annotate each bar with its value for damage_received_ratio
    for i, value in enumerate(top3_smallest_ratio["damage_received_ratio"]):
        plt.text(
            i,
            value,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            color="black",
            fontsize=8,
        )

    for i, value in enumerate(top3_largest_ratio["damage_received_ratio"]):
        plt.text(
            i + len(top3_smallest_ratio),
            value,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            color="black",
            fontsize=8,
        )

    # Annotation with metric formula
    formula_annotation = (
        "Formula: AVG(damage) / AVG(received_damage)\n"
        "This is the formula for calculating the damage_received_ratio."
    )

    # Calculate the height for the formula annotation
    height = max(top3_largest_ratio["damage_received_ratio"]) * 1.1
    bbox = dict(boxstyle="round", alpha=0.1)
    plt.annotate(
        formula_annotation,
        xy=(0, 1.02),
        xycoords="axes fraction",
        fontsize=8,
        ha="left",
        va="bottom",
        bbox=bbox,
    )

    # Mean value for damage_received_ratio
    mean_ratio_value = group_df["damage_received_ratio"].mean()

    # Annotate mean value at the extreme left position
    plt.text(
        -0.5,  # Смещение в крайнее левое положение
        mean_ratio_value,
        f"Mean: {mean_ratio_value:.2f}",
        ha="left",
        va="bottom",
        color="black",  # Черный цвет шрифта
        fontsize=10,  # Увеличенный размер шрифта
    )

    # Legend in the upper left corner
    handles, labels = plt.gca().get_legend_handles_labels()
    handles.append(plt.axhline(y=mean_ratio_value, color="red", linestyle="--"))
    labels.append(f"Mean Value (damage_received_ratio): {mean_ratio_value:.2f}")
    plt.legend(handles, labels, loc="upper left")

    plt.title(f"Damage Received Ratio - {cat_name}")
    plt.xlabel("item_name")
    plt.ylabel("damage_received_ratio")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels
    plt.tight_layout()  # Adjust layout for better spacing
    plt.savefig(f"../task1_2/pictures/damage_metric_{cat_name}{postfix}.png")
    plt.show()

#3 Наибольшее число побед
query_win_percentage = f"""
SELECT
    cat_name,
    item_name,
    COUNT(*) AS total_games,
    SUM(CASE WHEN a.winner_team_id = am.team_id THEN 1 ELSE 0 END) AS wins,
    100.0 * SUM(CASE WHEN a.winner_team_id = am.team_id THEN 1 ELSE 0 END) / COUNT(*) AS win_percentage
FROM
    catalog_items AS c
    JOIN arenas AS a ON a.team_build_type_id = c.cat_value
    JOIN arena_members AS am ON a.arena_id = am.arena_id AND a.periphery_id = am.periphery_id
    JOIN glossary_ships AS gs ON am.vehicle_type_id = gs.item_cd
WHERE
    c.cat_type = "BATTLE_TYPE"
    AND {where}
GROUP BY
    cat_name, item_name;
"""

# Выполните запрос
cursor.execute(query_win_percentage)
data_win_percentage = cursor.fetchall()

# Создайте DataFrame
columns_win_percentage = [
    "cat_name",
    "item_name",
    "total_games",
    "wins",
    "win_percentage",
]
df_win_percentage = pd.DataFrame(data_win_percentage, columns=columns_win_percentage)

# Построение диаграмм
for cat_name, group_df in df_win_percentage.groupby("cat_name"):
    plt.figure(figsize=(12, 6))  # Размер диаграммы

    # Топ 3 корабля с самым малым процентом побед
    top3_smallest = group_df.nsmallest(3, "win_percentage")
    bars1 = plt.bar(
        top3_smallest["item_name"].astype(str),
        top3_smallest["win_percentage"],
        label="Top 3 Smallest Win Percentage",
        color="blue",
        alpha=0.7,
    )

    # Топ 3 корабля с самым большим процентом побед
    top3_largest = group_df.nlargest(3, "win_percentage")
    bars2 = plt.bar(
        top3_largest["item_name"].astype(str),
        top3_largest["win_percentage"],
        label="Top 3 Largest Win Percentage",
        color="orange",
        alpha=0.7,
    )

    # Аннотация каждого бара с его значением
    for bars, offset in zip([bars1, bars2], [0, len(top3_smallest)]):
        for i, value in enumerate(bars):
            plt.text(
                i + offset,
                value.get_height(),
                f"{value.get_height():.2f}%",
                ha="center",
                va="bottom",
                color="black",
                fontsize=8,
            )

    # Легенда в верхнем левом углу
    plt.legend(loc="upper left")

    plt.title(f"Win Percentage - {cat_name}")
    plt.xlabel("item_name")
    plt.ylabel("win_percentage")
    plt.xticks(rotation=45, ha="right")  # Поворот меток по оси x
    plt.tight_layout()  # Регулировка макета для лучшего распределения
    plt.savefig(f"../task1_2/pictures/win_percentage_{cat_name}{postfix}.png")
    plt.show()
