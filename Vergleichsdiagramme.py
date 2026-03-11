import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from math import pi
import os
import shutil

# ---------------- KONFIGURATION ----------------
filename = 
output_folder = 
ADJUSTMENT_FACTOR = 15 

# Konfiguration (Kategorien)
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

# ---------------- FUNKTIONEN ----------------

def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except:
        return pd.read_excel(file_path)

def parse_overrides(input_str):
    overrides = {}
    if not input_str.strip(): return overrides
    entries = input_str.split(';')
    for entry in entries:
        if not entry.strip(): continue
        try:
            parts = entry.split(',')
            if len(parts) != 3: continue
            p_id = int(parts[0].strip())
            s_col = parts[1].strip()
            val = float(parts[2].strip())
            if p_id not in overrides: overrides[p_id] = {}
            overrides[p_id][s_col] = val
        except ValueError: pass
    return overrides

def calculate_both_scores(row, overrides):
    raw_scores = {}
    adj_scores = {}
    p_id = row['id']
    
    for cat, config in categories_config.items():
        # Raw
        val_sum = sum(row.get(col, 0) if pd.notna(row.get(col, 0)) else 0 for col in config['columns'])
        formula_result = (val_sum - config['sub']) / config['div']
        raw_percentage = max(0, min(1, formula_result)) * 100
        raw_scores[cat] = raw_percentage
        
        # Adjusted
        adj_percentage = raw_percentage
        fb_col = config['feedback_col']
        feedback_val = row.get(fb_col)
        
        if pd.notna(feedback_val):
            try:
                if int(feedback_val) == 1: adj_percentage += ADJUSTMENT_FACTOR
                elif int(feedback_val) == 3: adj_percentage -= ADJUSTMENT_FACTOR
            except: pass
        
        if p_id in overrides and fb_col in overrides[p_id]:
            adj_percentage = overrides[p_id][fb_col]
        
        adj_scores[cat] = max(0, min(100, adj_percentage))
        
    return raw_scores, adj_scores

def create_comparison_radar_chart(participant_id, raw_scores, adj_scores, target_folder):
    categories = list(raw_scores.keys())
    N = len(categories)
    
    values_raw = list(raw_scores.values()) + list(raw_scores.values())[:1]
    values_adj = list(adj_scores.values()) + list(adj_scores.values())[:1]
    angles = [n / float(N) * 2 * pi for n in range(N)] + [0]
    
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], categories, size=10)
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=8)
    plt.ylim(0, 100)
    
    ax.plot(angles, values_raw, linewidth=1, linestyle='dashed', color='blue', label='Ursprünglich')
    ax.fill(angles, values_raw, 'blue', alpha=0.05)
    
    ax.plot(angles, values_adj, linewidth=2, linestyle='solid', color='green', label='Angepasst')
    ax.fill(angles, values_adj, 'green', alpha=0.1)
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.title(f"ID: {participant_id}", size=15, y=1.08)
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        
    save_path = os.path.join(target_folder, f'vergleich_teilnehmer_{participant_id}.png')
    plt.savefig(save_path)
    plt.close()

# ---------------- HAUPTPROGRAMM ----------------

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

df = load_data(filename)

print("--- Manual Override ---")
override_input = input("Format ID,Spalte,Wert; (Enter für Skip): ")
overrides = parse_overrides(override_input)

# 1. Schritt: Alle Scores berechnen und sammeln
print("\nBerechne Scores für alle Teilnehmer...")
temp_data_list = []

for index, row in df.iterrows():
    p_id = row['id']
    try:
        raw, adj = calculate_both_scores(row, overrides)
        
        row_dict = {'Teilnehmer ID': p_id}
        for cat in categories_config.keys():
            clean = cat.replace('\n', ' ')
            row_dict[f"{clean} (Original)"] = raw[cat]
            row_dict[f"{clean} (Angepasst)"] = adj[cat]
        
        temp_data_list.append(row_dict)
    except Exception as e:
        print(f"Fehler bei ID {p_id}: {e}")

# DataFrame erstellen
results_df = pd.DataFrame(temp_data_list)

# 2. Schritt: Clustering und ABWEICHUNG berechnen
print("Führe Clustering und Analyse durch...")

if len(results_df) >= 4:
    # Nur angepasste Werte nehmen
    adj_cols = [c for c in results_df.columns if '(Angepasst)' in c]
    X = results_df[adj_cols].fillna(0)
    
    # --- Standardabweichung berechnen (Maß für Ausgeglichenheit) ---
    results_df['Standardabweichung'] = results_df[adj_cols].std(axis=1)
    
    # K-Means
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    results_df['Cluster_ID'] = kmeans.fit_predict(X)
    
    # Ranking der Cluster
    results_df['Mean_Score'] = results_df[adj_cols].mean(axis=1)
    cluster_quality = results_df.groupby('Cluster_ID')['Mean_Score'].mean().sort_values(ascending=False)
    
    ranked_indices = cluster_quality.index.tolist()
    
    folder_map = {
        ranked_indices[0]: "Sehr gut",
        ranked_indices[1]: "Mittelfeld",
        ranked_indices[2]: "Mittelfeld",
        ranked_indices[3]: "Schlecht"
    }
    
    results_df['Gruppe'] = results_df['Cluster_ID'].map(folder_map)

else:
    print("Zu wenig Teilnehmer für Clustering.")
    results_df['Gruppe'] = "Allgemein"
    adj_cols = [c for c in results_df.columns if '(Angepasst)' in c]
    results_df['Standardabweichung'] = results_df[adj_cols].std(axis=1)
    results_df['Mean_Score'] = results_df[adj_cols].mean(axis=1)

group_stats = results_df.groupby('Gruppe').agg({
    'Standardabweichung': 'mean',
    'Mean_Score': 'mean',
    'Teilnehmer ID': 'count'
}).reset_index()

group_stats.columns = ['Gruppe', 'Ø Standardabweichung (Abweichung)', 'Ø Gesamtscore', 'Anzahl Teilnehmer']
group_stats = group_stats.sort_values('Ø Gesamtscore', ascending=False)

print("\n-----------------------------------------------------------")
print("GRUPPEN-STATISTIK:")
print(group_stats)
print("-----------------------------------------------------------\n")

# 3. Schritt: Plotten
print("Erstelle Diagramme in Unterordnern...")
for index, row in results_df.iterrows():
    p_id = row['Teilnehmer ID']
    group_folder_name = row['Gruppe']
    full_target_path = os.path.join(output_folder, group_folder_name)
    
    raw_scores_plot = {}
    adj_scores_plot = {}
    
    for cat in categories_config.keys():
        clean = cat.replace('\n', ' ')
        raw_scores_plot[cat] = row[f"{clean} (Original)"]
        adj_scores_plot[cat] = row[f"{clean} (Angepasst)"]
    
    create_comparison_radar_chart(p_id, raw_scores_plot, adj_scores_plot, full_target_path)
    print(f"ID {p_id} -> {group_folder_name}")

# 4. Schritt: Export
print("\nSpeichere Excel-Dateien...")
cols = ['Teilnehmer ID', 'Gruppe', 'Standardabweichung'] + [c for c in results_df.columns if c not in ['Teilnehmer ID', 'Gruppe', 'Cluster_ID', 'Mean_Score', 'Standardabweichung']]
export_df = results_df[cols]

# Korrelationen
adj_cols_export = [c for c in export_df.columns if '(Angepasst)' in c]
corr_adj = export_df[adj_cols_export].copy()
corr_adj.columns = [c.replace(' (Angepasst)', '') for c in corr_adj.columns]
matrix_adj = corr_adj.corr()

orig_cols_export = [c for c in export_df.columns if '(Original)' in c]
corr_orig = export_df[orig_cols_export].copy()
corr_orig.columns = [c.replace(' (Original)', '') for c in corr_orig.columns]
matrix_orig = corr_orig.corr()

# Heatmaps
plt.figure(figsize=(12, 10))
sns.heatmap(matrix_adj, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'Korrelationsmatrix_Angepasst.png'))
plt.close()

plt.figure(figsize=(12, 10))
sns.heatmap(matrix_orig, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'Korrelationsmatrix_Original.png'))
plt.close()

# Excel speichern (jetzt mit Extra-Blatt für Gruppen-Statistik)
excel_path = os.path.join(output_folder, 'Alle_Vergleichsdaten_Gruppiert.xlsx')
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    # 1. Hauptdaten
    export_df.to_excel(writer, sheet_name='Daten', index=False)
    # 2. Gruppen-Statistik (NEU)
    group_stats.to_excel(writer, sheet_name='Gruppen_Statistik', index=False)
    # 3. Korrelationen
    matrix_adj.to_excel(writer, sheet_name='Korrelation_Angepasst')
    matrix_orig.to_excel(writer, sheet_name='Korrelation_Original')

print(f"\nFertig! Diagramme wurden in Unterordner sortiert: {output_folder}")
print(f"Die Gruppenstatistik findest du im Excel-Tabellenblatt 'Gruppen_Statistik'.")