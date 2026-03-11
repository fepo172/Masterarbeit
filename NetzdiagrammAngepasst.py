import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import os

# ---------------- KONFIGURATION ----------------
filename = 
output_folder = 

# Faktor für die Anpassung nach Feedback (in Prozentpunkten)
# Wenn Teilnehmer sagt "zu niedrig", wird dieser Wert addiert.
ADJUSTMENT_FACTOR = 15 

# Konfiguration der Kategorien, Formeln und zugehörigen Feedback-Spalten (SXX)
categories_config = {
    "Schemagesteuertes Lösen &\nDomänenspezifisches Wissen": {
        "columns": ['D0[D5]', 'D0[D6]', 'P0[P1]', 'P0[P3]', 'P0[P4]', 'A0[A2]', 'A0[A7]'],
        "sub": 7, "div": 28, "feedback_col": "S10"
    },
    "Problemzerlegung &\nUnterzielen": {
        "columns": ['D0[D7]', 'D0[D8]', 'A0[A3]', 'B0[B12]'],
        "sub": 4, "div": 16, "feedback_col": "S20"
    },
    "Arbeiten\nVorwärts": {
        "columns": ['P0[P7]', 'A0[A4]', 'B0[B5]', 'B0[B6]'],
        "sub": 4, "div": 16, "feedback_col": "S30"
    },
    "Arbeiten\nRückwärts": {
        "columns": ['D0[D9]', 'D0[D10]', 'A0[A6]', 'B0[B7]', 'B0[B10]'],
        "sub": 5, "div": 20, "feedback_col": "S40"
    },
    "Generieren und\nTesten": {
        "columns": ['D0[D3]', 'D0[D4]', 'P0[P9]', 'P0[P11]', 'B0[B2]', 'B0[B3]', 'B0[B4]', 'B0[B8]', 'B0[B9]', 'B0[B13]', 'B0[B14]'],
        "sub": 11, "div": 44, "feedback_col": "S50"
    },
    "Problemlösung durch\nAnalogie": {
        "columns": ['P0[P8]', 'A0[A8]'],
        "sub": 2, "div": 8, "feedback_col": "S60"
    },
    "Metakognitive und\nAffektive Strategien": {
        "columns": ['D0[D2]', 'D0[D13]', 'D0[D14]', 'P0[P2]', 'P0[P5]', 'P0[P10]', 'A0[A1]', 'A0[A5]', 'A0[A9]', 'A0[A10]', 'B0[B11]'],
        "sub": 11, "div": 44, "feedback_col": "S70"
    },
    "Planungsstrategie": {
        "columns": ['D0[D1]', 'D0[D11]', 'D0[D12]', 'P0[P6]', 'B0[B1]'],
        "sub": 5, "div": 20, "feedback_col": "S80"
    }
}
# ------------------------------------------------

def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Konnte CSV nicht laden, versuche Excel... ({e})")
        return pd.read_excel(file_path)

def parse_overrides(input_str):
    """
    Parst den Override-String: "1,S10,80;5,S30,50"
    Rückgabe: Dict { teilnehmer_id: { 'S10': 80.0, ... } }
    """
    overrides = {}
    if not input_str.strip():
        return overrides
    
    entries = input_str.split(';')
    for entry in entries:
        if not entry.strip(): continue
        try:
            parts = entry.split(',')
            if len(parts) != 3:
                print(f"Warnung: Ungültiges Format in '{entry}', überspringe.")
                continue
            
            p_id = int(parts[0].strip()) 
            s_col = parts[1].strip()
            val = float(parts[2].strip())
            
            if p_id not in overrides:
                overrides[p_id] = {}
            overrides[p_id][s_col] = val
        except ValueError as e:
            print(f"Fehler beim Parsen von '{entry}': {e}")
            
    return overrides

def calculate_scores_and_adjust(row, overrides):
    """
    Berechnet Scores, wendet Feedback-Logik an und berücksichtigt Overrides.
    """
    scores = {}
    p_id = row['id']
    
    for cat, config in categories_config.items():
        # 1. Basis-Formel berechnen
        val_sum = sum(row.get(col, 0) if pd.notna(row.get(col, 0)) else 0 for col in config['columns'])
        formula_result = (val_sum - config['sub']) / config['div']
        percentage = max(0, min(1, formula_result)) * 100
        
        # 2. Feedback-Anpassung (S-Spalten)
        fb_col = config['feedback_col']
        # Limesurvey exportiert Zahlen (1=zu niedrig, 2=passend, 3=zu hoch)
        # Manchmal NaN, daher Check
        feedback_val = row.get(fb_col)
        
        if pd.notna(feedback_val):
            try:
                feedback_val = int(feedback_val)
                if feedback_val == 1: # "Zu niedrig" -> Score erhöhen
                    percentage += ADJUSTMENT_FACTOR
                elif feedback_val == 3: # "Zu hoch" -> Score senken
                    percentage -= ADJUSTMENT_FACTOR
            except ValueError:
                pass # Falls Text statt Zahl drin steht, ignorieren
        
        # 3. Manual Override (hat Priorität)
        if p_id in overrides and fb_col in overrides[p_id]:
            percentage = overrides[p_id][fb_col]
            print(f" -> Override angewendet für ID {p_id}, {cat} ({fb_col}): Neuer Wert {percentage}%")

        # Begrenzung auf 0-100%
        scores[cat] = max(0, min(100, percentage))
        
    return scores

def create_radar_chart(participant_id, scores):
    categories = list(scores.keys())
    values = list(scores.values())
    N = len(categories)

    values += values[:1]
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    plt.xticks(angles[:-1], categories, size=10)
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=8)
    plt.ylim(0, 100)

    ax.plot(angles, values, linewidth=2, linestyle='solid', label=f'ID {participant_id}')
    ax.fill(angles, values, 'b', alpha=0.1)

    plt.title(f"Ergebnisse für Teilnehmer ID: {participant_id}", size=15, y=1.05)
    
    save_path = os.path.join(output_folder, f'radar_chart_teilnehmer_{participant_id}.png')
    plt.savefig(save_path)
    plt.close()

# ---------------- HAUPTPROGRAMM ----------------

# 1. Daten laden
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
df = load_data(filename)

# 2. Manual Override abfragen
print("--- Manual Override ---")
print("Bitte Overrides eingeben im Format: TeilnehmerID,S-Spalte,Wert;...")
print("Beispiel: 1,S10,80;5,S30,50")
override_input = input("Eingabe (oder Enter für keine): ")

overrides = parse_overrides(override_input)
if overrides:
    print(f"Erkannte Overrides: {overrides}")

# 3. Durchlauf
print("\nStarte Berechnung und Erstellung der Diagramme...")
for index, row in df.iterrows():
    p_id = row['id']
    try:
        final_scores = calculate_scores_and_adjust(row, overrides)
        create_radar_chart(p_id, final_scores)
    except Exception as e:
        print(f"Fehler bei ID {p_id}: {e}")

print(f"Fertig! Bilder in '{output_folder}' gespeichert.")