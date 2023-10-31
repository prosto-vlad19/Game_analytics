# Analysis of free-to-play games about ships.
## Description 
You need to complete tasks using a database SQLite3 containing information about the game.

## Task
1) Analyze the popularity of game modes.
2) Analyze the efficiency of ships

## Initial data

1. Arenas table – characteristic data of the battle (mode, map, duration, etc.)

| Column               | Комментарий                                                       |
|----------------------|-------------------------------------------------------------------|
| `arena_id`           | Unique battle ID                                                  |
| `periphery_id`       | Unique cluster ID                                                 |
| `winner_team_id`     | Winning team ID, -1 means draw                                    |
| `start_dt`           | Start time of the battle                                          |
| `duration_sec`       | Duration of battle (in seconds)                                   |
| `map_type_id`        | Game card ID (ref catalog_items, category ‘ARENA_TYPES’)          |
| `team_build_type_id` | Game mode ID (ref catalog_items, category 'TEAM_BUILD_TYPE')      |
| `battle_level_id`    | Battle level ID (usually the maximum level of the ship in battle) |

2. Table arena_members – user data on played battles.
What vehicle was the player on, how successfully did he perform the battle, etc.
Negative player ID values correspond to bots.


| Column            | Комментарий                                                  |
|-------------------|--------------------------------------------------------------|
| `arena_id`        | Unique battle ID                                             |
| `periphery_id`    | Unique cluster ID                                            |
| `account_db_id`   | Player ID. AI-controlled players (bots) have a negative ID   |
| `team_id`         | Player team, usually 0 or 1                                  |
| `clan_db_id`      | Clan ID                                                      |
| `vehicle_type_id` | ID of the ship used                                          |
| `ships_killed`    | Number of enemy ships destroyed                              |
| `planes_killed`   | Number of enemy aircraft destroyed                           |
| `damage`          | Damage caused to enemy ships                                 |
| `team_damage`     | Damage dealt to allies in battle                             |
| `received_damage` | Damage received in battle                                    |
| `regen_hp`        | Amount of health restored in battle                          |
| `max_hp`          | Maximum ship health                                          |
| `is_alive`        | 1 – if the player’s ship “survived at the end of the battle” |
| `distance`        | The path taken                                               |
| `credits`         | Number of credits earned                                     |
| `exp`             | Amount of experience earned                                  |

3. Таблица glossary_ships – словарь для расшифровки техники.
4. Таблица catalog_items – словарь для расшифровки других игровых сущностей (например, игрового режима).



## Structure of project
## Files and Modules and What They Do

| Name                   | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `./task1_1`            | Folder with the code for solving the first task.                            |
| `./task1_2`            | Folder with the code for solving the second task.                           |
