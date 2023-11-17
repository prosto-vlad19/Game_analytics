import sqlite3
import warnings

import matplotlib.pyplot as plt
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

    plt.figure(figsize=(10, 6))  # Adjust the figure size

    # Top 3 smallest values
    top3_smallest = group_df.nsmallest(3, "avg_metric")
    plt.bar(
        top3_smallest["item_name"].astype(str),
        top3_smallest["avg_metric"],
        label="Top 3 Smallest",
        color="blue",
        alpha=0.7,
    )

    # Top 3 largest values
    top3_largest = group_df.nlargest(3, "avg_metric")
    plt.bar(
        top3_largest["item_name"].astype(str),
        top3_largest["avg_metric"],
        label="Top 3 Largest",
        color="orange",
        alpha=0.7,
    )

    # Mean value
    mean_value = group_df["avg_metric"].mean()
    plt.axhline(y=mean_value, color="red", linestyle="--", label="Mean Value")

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
    plt.text(
        len(top3_smallest) / 2,
        mean_value,
        f"Mean: {mean_value:.2f}",
        ha="center",
        va="bottom" if mean_value != 0 else "top",
        color="green",
        fontsize=8,
    )

    plt.title(f"Histogram for {cat_name}")
    plt.xlabel("item_name")
    plt.ylabel("avg_metric")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels
    plt.legend()
    plt.tight_layout()  # Adjust layout for better spacing
    plt.show()
