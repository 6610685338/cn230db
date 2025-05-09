#6610685338 ศุภกิตติ์ อัศววุฒิโรจน์
import requests
import sqlite3

url = "https://api.opendota.com/api/heroStats"
response = requests.get(url)
heroes = response.json()

conn = sqlite3.connect("dota_heroes.db")
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS heroes (
        id INTEGER PRIMARY KEY,
        name TEXT,
        localized_name TEXT,
        primary_attr TEXT,
        attack_type TEXT,
        base_health INTEGER,
        base_attack_min INTEGER,
        base_attack_max INTEGER,
        roles TEXT
    )
"""
)

for hero in heroes:
    cur.execute(
        """
        INSERT OR REPLACE INTO heroes (
            id, name, localized_name, primary_attr, attack_type,
            base_health, base_attack_min, base_attack_max
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            hero["id"],
            hero["name"],
            hero["localized_name"],
            hero["primary_attr"],
            hero["attack_type"],
            hero["base_health"],
            hero["base_attack_min"],
            hero["base_attack_max"],
        ),
    )

conn.commit()

print("\n Top 5 strongest base attack (max):")
for row in cur.execute(
    """
    SELECT localized_name, base_attack_max 
    FROM heroes 
    WHERE localized_name IS NOT NULL AND base_attack_max IS NOT NULL
    ORDER BY base_attack_max DESC, localized_name ASC
    LIMIT 5
"""
):
    print(f"   → {row[0]}: {row[1]} attack")

print("\n Average base health by primary attribute:")
for row in cur.execute(
    """
    SELECT primary_attr, ROUND(AVG(base_health), 2) as avg_hp
    FROM heroes
    WHERE primary_attr IS NOT NULL AND base_health IS NOT NULL
    GROUP BY primary_attr
    ORDER BY primary_attr
"""
):
    attr = row[0].upper()
    avg_hp = row[1]
    print(f"   → {attr}: {avg_hp} HP")

import matplotlib.pyplot as plt

attributes = []
average_health = []

for row in cur.execute(
    """
    SELECT primary_attr, AVG(base_health)
    FROM heroes
    WHERE primary_attr IS NOT NULL AND base_health IS NOT NULL
    GROUP BY primary_attr
"""
):
    attributes.append(row[0].upper())
    average_health.append(row[1])

plt.figure(figsize=(6, 4))
plt.bar(attributes, average_health)
plt.title("Average Base Health by Primary Attribute")
plt.xlabel("Primary Attribute")
plt.ylabel("Average Base Health")
plt.ylim(min(average_health) - 50, max(average_health) + 50)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()

conn.close()
