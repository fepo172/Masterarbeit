import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import os

# 1. Datei laden
filename = 
try:
    df = pd.read_excel(filename)
except Exception as e:
    print(f"Fehler beim Laden als CSV, versuche Excel... ({e})")
    df = pd.read_excel(filename)

# Ausgabeordner für die Bilder erstellen
output_folder = 
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 2. Konfiguration der Kategorien und Formeln
categories_config = {
    "Schemagesteuertes Lösen &\nDomänenspezifisches Wissen": {
        "columns": ['D0[D5]', 'D0[D6]', 'P0[P1]', 'P0[P3]', 'P0[P4]', 'A0[A2]', 'A0[A7]'],
        "sub": 7, "div": 28
    },
    "Problemzerlegung &\nUnterzielen": {
        "columns": ['D0[D7]', 'D0[D8]', 'A0[A3]', 'B0[B12]'],
        "sub": 4, "div": 16
    },
    "Arbeiten\nVorwärts": {
        "columns": ['P0[P7]', 'A0[A4]', 'B0[B5]', 'B0[B6]'],
        "sub": 4, "div": 16
    },
    "Arbeiten\nRückwärts": {
        "columns": ['D0[D9]', 'D0[D10]', 'A0[A6]', 'B0[B7]', 'B0[B10]'],
        "sub": 5, "div": 20
    },
    "Generieren und\nTesten": {
        "columns": ['D0[D3]', 'D0[D4]', 'P0[P9]', 'P0[P11]', 'B0[B2]', 'B0[B3]', 'B0[B4]', 'B0[B8]', 'B0[B9]', 'B0[B13]', 'B0[B14]'],
        "sub": 11, "div": 44
    },
    "Problemlösung durch\nAnalogie": {
        "columns": ['P0[P8]', 'A0[A8]'],
        "sub": 2, "div": 8
    },
    "Metakognitive und\nAffektive Strategien": {
        "columns": ['D0[D2]', 'D0[D13]', 'D0[D14]', 'P0[P2]', 'P0[P5]', 'P0[P10]', 'A0[A1]', 'A0[A5]', 'A0[A9]', 'A0[A10]', 'B0[B11]'],
        "sub": 11, "div": 44
    },
    "Planungsstrategie": {
        "columns": ['D0[D1]', 'D0[D11]', 'D0[D12]', 'P0[P6]', 'B0[B1]'],
        "sub": 5, "div": 20
    }
}

def calculate_scores(row):
    """Berechnet die Prozentwerte für eine Zeile basierend auf der Konfiguration."""
    scores = {}
    for cat, config in categories_config.items():
        # Summe berechnen, NaN (leere Felder) als 0 werten
        val_sum = sum(row.get(col, 0) if pd.notna(row.get(col, 0)) else 0 for col in config['columns'])
        
        # Formel anwenden: (Summe - Subtrahend) / Divisor
        formula_result = (val_sum - config['sub']) / config['div']
        
        # Begrenzung auf [0, 1] und Umrechnung in Prozent
        percentage = max(0, min(1, formula_result)) * 100
        scores[cat] = percentage
    return scores

def create_radar_chart(participant_id, scores):
    """Erstellt ein Netzdiagramm für einen Teilnehmer."""
    categories = list(scores.keys())
    values = list(scores.values())
    N = len(categories)

    # Ersten Wert am Ende wiederholen, damit sich der Kreis schließt
    values += values[:1]
    
    # Winkel für jede Achse berechnen
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Plot initialisieren
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)
    
    # Start oben (12 Uhr) und im Uhrzeigersinn
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Achsenbeschriftungen
    plt.xticks(angles[:-1], categories, size=10)
    
    # Y-Achsen Beschriftung
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=8)
    plt.ylim(0, 100)

    # Daten plotten
    ax.plot(angles, values, linewidth=2, linestyle='solid', label=f'ID {participant_id}')
    ax.fill(angles, values, 'b', alpha=0.1)

    plt.title(f"Ergebnisse für Teilnehmer ID: {participant_id}", size=15, y=1.05)
    
    # Speichern
    save_path = os.path.join(output_folder, f'radar_chart_teilnehmer_{participant_id}.png')
    plt.savefig(save_path)
    plt.close() # Speicher freigeben

# 3. Hauptschleife über alle Teilnehmer
print("Starte Generierung der Diagramme...")
for index, row in df.iterrows():
    p_id = row['id']
    try:
        scores = calculate_scores(row)
        create_radar_chart(p_id, scores)
        print(f"Diagramm erstellt für ID: {p_id}")
    except Exception as e:
        print(f"Fehler bei ID {p_id}: {e}")

print(f"Fertig! Alle Bilder wurden im Ordner '{output_folder}' gespeichert.")