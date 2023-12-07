import json

# Creare una lista di oggetti corso
corsi = [
    {
        "nome_corso": "Enterprise Mobile Application Development",
        "codice_corso": 11111,
        "prof": "Rita Francese",
        "orario_corso": "Lunedì e Mercoledì, 14:00-16:00",
        "cfu": 6,
    },
    {
        "nome_corso": "Data Science Fundamentals",
        "codice_corso": 22222,
        "prof": "Prof. Johnson",
        "orario_corso": "Martedì e Giovedì, 10:00-12:00",
        "cfu": 9,
    },
    {
        "nome_corso": "Compilatori",
        "codice_corso": 33333,
        "prof": "Gennaro Costagliola",
        "orario_corso": "Martedì e Giovedì, 10:00-12:00",
        "cfu": 9,
    },
    # Aggiungi altri corsi secondo necessità
]

# Salvare la lista di oggetti in un file JSON
with open("json/corsi.json", "w") as json_file:
    json.dump(corsi, json_file, indent=2)


menu_settimana = [
    {
        "giorno": "lunedì",
        "primo": "pasta al sugo",
        "secondo": "pollo",
        "contorno": "insalata",
    },
    {
        "giorno": "martedì",
        "primo": "pasta al pesto",
        "secondo": "carne",
        "contorno": "insalata",
    },
    {
        "giorno": "mercoledì",
        "primo": "pasta e patate",
        "secondo": "pesce",
        "contorno": "insalata",
    },
    {
        "giorno": "giovedì",
        "primo": "pasta e patate",
        "secondo": "pesce",
        "contorno": "insalata",
    },
    {
        "giorno": "venerdì",
        "primo": "pasta e patate",
        "secondo": "pesce",
        "contorno": "insalata",
    },
    {
        "giorno": "sabato",
        "primo": "pasta e patate",
        "secondo": "pesce",
        "contorno": "insalata",
    },
]

# Scrivi i dati nel file JSON con codifica UTF-8
with open("json/menu.json", "w", encoding="utf-8") as json_file:
    json.dump(
        menu_settimana, json_file, indent=2
    )  # ensure_ascii=False per gestire UTF-8
