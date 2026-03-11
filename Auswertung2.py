import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------- KONFIGURATION ----------------
filename = 
output_folder = 

ADJUSTMENT_FACTOR = 15 

# Mappings für die demographischen Fragen
demog_labels = {
    'PE1': {'AO01': '<1 Jahr', 'AO02': '1-5 Jahre', 'AO03': '5-10 Jahre', 'AO04': '10-15 Jahre', 'AO05': '>15 Jahre'},
    'PE2': {'AO01': 'sehr unerfahren', 'AO02': 'etwas weniger erfahren', 'AO03': 'etwa ähnlich erfahren', 'AO04': 'etwas erfahrener', 'AO05': 'deutlich erfahrener'},
    'PE3': {'AO01': 'einmal im Monat oder seltener', 'AO02': 'mehrmals im Monat', 'AO03': 'einmal pro Woche', 'AO04': 'mehrmals in der Woche', 'AO05': 'täglich'},
    'PE4': {'AO01': 'weniger als 4', 'AO02': 'zwischen 4 und 7', 'AO03': 'mehr als 7'}
}

pe_mapping = {
    'PE1': {'AO01': 1, 'AO02': 2, 'AO03': 3, 'AO04': 4, 'AO05': 5}, 
    'PE2': {'AO01': 1, 'AO02': 2, 'AO03': 3, 'AO04': 4, 'AO05': 5},
    'PE3': {'AO01': 1, 'AO02': 2, 'AO03': 3, 'AO04': 4, 'AO05': 5},
    'PE4': {'AO01': 1, 'AO02': 2, 'AO03': 3}
}

# --- KONFIG 1: Psychologische Strategien ---
psych_config = {
    "Schemagesteuertes Lösen": { "columns": ['D0[D5]', 'D0[D6]', 'P0[P1]', 'P0[P3]', 'P0[P4]', 'A0[A2]', 'A0[A7]'], "sub": 7, "div": 28, "fb": "S10" },
    "Problemzerlegung": { "columns": ['D0[D7]', 'D0[D8]', 'A0[A3]', 'B0[B12]'], "sub": 4, "div": 16, "fb": "S20" },
    "Arbeiten Vorwärts": { "columns": ['P0[P7]', 'A0[A4]', 'B0[B5]', 'B0[B6]'], "sub": 4, "div": 16, "fb": "S30" },
    "Arbeiten Rückwärts": { "columns": ['D0[D9]', 'D0[D10]', 'A0[A6]', 'B0[B7]', 'B0[B10]'], "sub": 5, "div": 20, "fb": "S40" },
    "Generieren und Testen": { "columns": ['D0[D3]', 'D0[D4]', 'P0[P9]', 'P0[P11]', 'B0[B2]', 'B0[B3]', 'B0[B4]', 'B0[B8]', 'B0[B9]', 'B0[B13]', 'B0[B14]'], "sub": 11, "div": 44, "fb": "S50" },
    "Analogie": { "columns": ['P0[P8]', 'A0[A8]'], "sub": 2, "div": 8, "fb": "S60" },
    "Metakognitive Strat.": { "columns": ['D0[D2]', 'D0[D13]', 'D0[D14]', 'P0[P2]', 'P0[P5]', 'P0[P10]', 'A0[A1]', 'A0[A5]', 'A0[A9]', 'A0[A10]', 'B0[B11]'], "sub": 11, "div": 44, "fb": "S70" },
    "Planungsstrategie": { "columns": ['D0[D1]', 'D0[D11]', 'D0[D12]', 'P0[P6]', 'B0[B1]'], "sub": 5, "div": 20, "fb": "S80" }
}

# --- KONFIG 2: Programmierstrategien ---
prog_config = {
    "Agile & Lean Methoden": ['D0[D1]', 'D0[D2]'],
    "Test-Driven Development (TDD)": ['D0[D3]', 'D0[D4]'],
    "Design Patterns & Muster Sprachen": ['D0[D5]', 'D0[D6]'],
    "Dekomposition / Zerlegung": ['D0[D7]', 'D0[D8]'],
    "Typkonstruktion als Strategie": ['D0[D9]', 'D0[D10]'],
    "Skizzierung (Sketching)": ['D0[D11]', 'D0[D12]'],
    "Analytisches Denken & Trade-offs": ['D0[D13]', 'D0[D14]'],
    "Explizite Programmierstrategien": ['P0[P1]', 'P0[P2]'],
    "Programmier-Pläne (Initialisierung)": ['P0[P3]'],
    "Programmier-Pläne (Guarded Division)": ['P0[P4]'],
    "Selbstreguliertes Lernen (SRL)": ['P0[P5]', 'P0[P6]'],
    "Inkrementelles/Systematisches Vorgehen": ['P0[P7]'],
    "Code-Wiederverwendung": ['P0[P8]'],
    "Exploratives Programmieren": ['P0[P9]', 'P0[P10]'],
    "LLM-unterstützte Codegenerierung": ['P0[P11]'],
    "Scent-Following": ['A0[A1]'],
    "Kognitive Modelle & Abstraktion": ['A0[A2]', 'A0[A3]'],
    "Compiler als Assistent": ['A0[A4]', 'A0[A5]'],
    "Interaktion mit der UI": ['A0[A6]'],
    "Wissensnutzung & Mustererkennung": ['A0[A7]', 'A0[A8]'],
    "SRL: Auflösung von Schwierigkeiten": ['A0[A9]', 'A0[A10]'],
    "Strategischer Dreiklang": ['B0[B1]', 'B0[B2]'],
    "Traditionelle & Manuelle Strategien": ['B0[B3]', 'B0[B4]'],
    "Code Tracing": ['B0[B5]', 'B0[B6]'],
    "Systematische Fehlerlokalisierung": ['B0[B7]', 'B0[B8]'],
    "Trial and Error": ['B0[B9]'],
    "Output-Zentriertes Debugging (Whyline)": ['B0[B10]', 'B0[B11]'],
    "Slicing-basierte Techniken": ['B0[B12]'],
    "Automatisierte Fehlerlokalisierung (FL)": ['B0[B13]', 'B0[B14]']
}

# ---------------- FUNKTIONEN ----------------

def load_and_prep_data():
    try:
        df = pd.read_csv(filename)
    except:
        try: df = pd.read_excel(filename)
        except: return None
    for col, mapping in pe_mapping.items():
        if col in df.columns:
            df[f'{col}_Num'] = df[col].map(mapping)
    return df

def clean_col_name(col_name):
    if '[' in col_name and ']' in col_name:
        return col_name.split('[')[1].replace(']', '')
    return col_name

def calc_psych_scores(df):
    results = []
    for _, row in df.iterrows():
        res = {'id': row['id']}
        for pe in pe_mapping.keys(): res[f'{pe}_Num'] = row.get(f'{pe}_Num', np.nan)
        for cat, conf in psych_config.items():
            items = [row.get(c, 0) if pd.notna(row.get(c, 0)) else 0 for c in conf['columns']]
            raw_pct = max(0, min(1, (sum(items) - conf['sub']) / conf['div'])) * 100
            adj_pct = raw_pct
            fb_val = row.get(conf['fb'])
            if pd.notna(fb_val):
                try:
                    if int(fb_val) == 1: adj_pct += ADJUSTMENT_FACTOR
                    elif int(fb_val) == 3: adj_pct -= ADJUSTMENT_FACTOR
                except: pass
            res[cat] = max(0, min(100, adj_pct))
            res[f"{cat}_RAW"] = max(0, min(100, raw_pct))
        results.append(res)
    return pd.DataFrame(results)

def calc_prog_scores(df):
    results = []
    for _, row in df.iterrows():
        res = {'id': row['id']}
        for pe in pe_mapping.keys(): res[f'{pe}_Num'] = row.get(f'{pe}_Num', np.nan)
        for cat, cols in prog_config.items():
            vals = [row.get(c) for c in cols if pd.notna(row.get(c))]
            res[cat] = np.mean(vals) if vals else np.nan
        results.append(res)
    return pd.DataFrame(results)

def cronbach_alpha(df_items):
    df_drop = df_items.dropna()
    if df_drop.empty: return 0
    item_var = df_drop.var(axis=0, ddof=1)
    tot_var = df_drop.sum(axis=1).var(ddof=1)
    n = len(df_items.columns)
    if tot_var == 0 or n < 2: return 0
    return (n / (n - 1)) * (1 - (item_var.sum() / tot_var))

# ---------------- MAIN ----------------

if not os.path.exists(output_folder): os.makedirs(output_folder)
print(f"Lade Daten: {filename}")
df_raw = load_and_prep_data()

if df_raw is not None:
    df_psych = calc_psych_scores(df_raw)
    df_prog = calc_prog_scores(df_raw)
    pe_cols_num = ['PE1_Num', 'PE2_Num', 'PE3_Num', 'PE4_Num']
    
    df_psych.to_csv(os.path.join(output_folder, "Ergebnisse_Psychologische_Strategien.csv"), index=False, sep=';', encoding='utf-8-sig')
    df_prog.to_csv(os.path.join(output_folder, "Ergebnisse_Programmierstrategien.csv"), index=False, sep=';', encoding='utf-8-sig')

    # =========================================================
    # TEIL A: Psychologische Strategien
    # =========================================================
    print("\n>>> [Teil A] Analysiere Psych. Strategien...")
    psych_cols = list(psych_config.keys())
    
    # Boxplot Top/Flop Items
    all_psych_items = []
    for c in psych_config.values(): all_psych_items.extend(c['columns'])
    all_items_clean = df_raw[all_psych_items].copy()
    all_items_clean.columns = [clean_col_name(c) for c in all_items_clean.columns]
    stats_all = all_items_clean.describe().transpose().sort_values('mean', ascending=False)
    selection = stats_all.head(10).index.tolist() + stats_all.tail(10).index.tolist()
    
    stats_all.to_csv(os.path.join(output_folder, "RQ1_Psych_Item_Statistiken.csv"), sep=';', encoding='utf-8-sig')
    
    plt.figure(figsize=(12, 10))
    sns.boxplot(data=all_items_clean[selection], orient='h', palette="Greens")
    plt.title("RQ1: Fragebogen Items Top 10 / Flop 10")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "RQ1_Fragebogen_Items_Boxplot.png"))
    plt.close()

    # Boxplot Strategien 
    for suffix, title_part in [("", "Adjusted"), ("_RAW", "Unadjusted")]:
        cols = psych_cols if suffix == "" else [f"{c}_RAW" for c in psych_cols]
        plt.figure(figsize=(14, 7))
        sns.boxplot(data=df_psych[cols], palette="Greens")
        plt.xticks(rotation=45, ha='right')
        plt.title(f"RQ2: Psychologische Strategien ({title_part})")
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f"RQ2_Psych_{title_part}_Boxplot.png"))
        plt.close()

    # Heatmap 
    corr_psych = df_psych[pe_cols_num + psych_cols].corr(method='spearman').loc[psych_cols, pe_cols_num]
    corr_psych.to_csv(os.path.join(output_folder, "RQ3_Psych_Korrelationen.csv"), sep=';', encoding='utf-8-sig')
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_psych, annot=True, cmap="coolwarm", center=0, fmt=".2f")
    plt.title("RQ3: Psych. Strategien vs. Erfahrung (Spearman)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "RQ3_Psych_Heatmap_Spearman.png"))
    plt.close()

    # =========================================================
    # TEIL B: Programmierstrategien
    # =========================================================
    print("\n>>> [Teil B] Analysiere Programmierstrategien...")
    prog_cols = list(prog_config.keys())
    sorted_prog = df_prog[prog_cols].median().sort_values(ascending=False).index.tolist()
    
    plt.figure(figsize=(12, 12))
    sns.boxplot(data=df_prog[sorted_prog], orient='h', palette="Greens_r")
    plt.title("RQ1: Programmierstrategien (Boxplot)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "RQ1_Prog_Strategien_Boxplot.png"))
    plt.close()

    # Heatmap 
    corr_prog = df_prog[pe_cols_num + prog_cols].corr(method='spearman').loc[prog_cols, pe_cols_num]
    corr_prog.to_csv(os.path.join(output_folder, "RQ3_Prog_Korrelationen.csv"), sep=';', encoding='utf-8-sig')
    
    plt.figure(figsize=(12, 12))
    sns.heatmap(corr_prog, annot=True, cmap="coolwarm", center=0, fmt=".2f")
    plt.title("RQ3: Prog. Strategien vs. Erfahrung (Spearman)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "RQ3_Prog_Strategien_Heatmap_Spearman.png"))
    plt.close()

    # =========================================================
    # TEIL C: Demographische Auswertung
    # =========================================================
    print("\n>>> [Teil C] Analysiere Demographie (PE1-PE4)...")
    demog_stats_list = []
    
    for col in ['PE1', 'PE2', 'PE3', 'PE4']:
        if col in df_raw.columns:
            counts = df_raw[col].map(demog_labels[col]).value_counts().reset_index()
            counts.columns = ['Antwort', 'Anzahl']
            order = list(demog_labels[col].values())
            counts['Antwort'] = pd.Categorical(counts['Antwort'], categories=order, ordered=True)
            counts = counts.sort_values('Antwort')
            counts['Prozent'] = (counts['Anzahl'] / counts['Anzahl'].sum() * 100).round(2)
            counts['Frage'] = col
            demog_stats_list.append(counts)

            plt.figure(figsize=(10, 6))
            sns.barplot(data=counts, x='Anzahl', y='Antwort', palette="Greens_d")
            plt.tight_layout()
            plt.savefig(os.path.join(output_folder, f"Demographie_{col}_Barplot.png"))
            plt.close()

    if demog_stats_list:
        combined_demog = pd.concat(demog_stats_list)
        combined_demog.to_excel(os.path.join(output_folder, "Demographie_Statistiken.xlsx"), index=False)
        combined_demog.to_csv(os.path.join(output_folder, "Demographie_Statistiken.csv"), index=False, sep=';', encoding='utf-8-sig')

    print(f"\nFERTIG! Alle Analysen, Diagramme, Excels und CSVs in: {output_folder}")
else:
    print("Fehler: Keine Daten gefunden.")