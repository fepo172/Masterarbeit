import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------- KONFIGURATION ----------------
filename = 
output_folder = 

ADJUSTMENT_FACTOR = 15 

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
    "Programmier-Pläne": ['P0[P3]', 'P0[P4]'],
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
    """Macht aus D0[D1] -> D1"""
    if '[' in col_name and ']' in col_name:
        return col_name.split('[')[1].replace(']', '')
    return col_name

def calc_psych_scores(df):
    results = []
    for _, row in df.iterrows():
        res = {'id': row['id']}
        for pe in pe_mapping.keys(): res[f'{pe}_Num'] = row.get(f'{pe}_Num', np.nan)
        
        for cat, conf in psych_config.items():
            # 1. Raw Calculation
            items = [row.get(c, 0) if pd.notna(row.get(c, 0)) else 0 for c in conf['columns']]
            raw_pct = max(0, min(1, (sum(items) - conf['sub']) / conf['div'])) * 100
            
            # 2. Adjusted Calculation
            adj_pct = raw_pct
            fb_val = row.get(conf['fb'])
            if pd.notna(fb_val):
                try:
                    if int(fb_val) == 1: adj_pct += ADJUSTMENT_FACTOR
                    elif int(fb_val) == 3: adj_pct -= ADJUSTMENT_FACTOR
                except: pass
            
            # Save Adjusted
            res[cat] = max(0, min(100, adj_pct))
            # Save Raw separately
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
    pe_cols = ['PE1_Num', 'PE2_Num', 'PE3_Num', 'PE4_Num']

    # =========================================================
    # TEIL A: Psychologische Strategien (Fragebogen)
    # =========================================================
    print("\n>>> [Teil A] Analysiere Fragebogen & Psych. Strategien...")
    psych_cols = list(psych_config.keys())

    # ---------------------------------------------------------
    # Fragebogen Items (Zweifach sortiert)
    # ---------------------------------------------------------
    print("    ->  1: Fragebogen Items (Boxplot)...")
    all_psych_items = []
    for c in psych_config.values(): all_psych_items.extend(c['columns'])

    all_items_clean = df_raw[all_psych_items].copy()
    all_items_clean.columns = [clean_col_name(c) for c in all_items_clean.columns]

    stats_all = all_items_clean.describe().transpose()
    stats_all['median'] = all_items_clean.median()
    stats_all = stats_all.sort_values(by=['50%', 'mean'], ascending=False)

    stats_all.to_excel(os.path.join(output_folder, "1_Fragebogen_Items_Stats.xlsx"))

    top_items = stats_all.head(10).index.tolist()
    flop_items = stats_all.tail(10).index.tolist()
    selection = top_items + flop_items

    plt.figure(figsize=(12, 10))
    sns.boxplot(data=all_items_clean[selection], orient='h', palette="Greens", order=selection)
    plt.xlabel("Likert Skala (1=nie, 5=sehr oft)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "1_Fragebogen_Items_Boxplot.png"))
    plt.close()
    
    # ---------------------------------------------------------
    # Verteilung Psychologische Strategien (MIT & OHNE ADJUSTMENT)
    # ---------------------------------------------------------
    print("    -> 2: Psych. Strategien (Boxplots)...")
    
    print("       ...Adjusted")
    df_psych[psych_cols].describe().transpose().to_excel(os.path.join(output_folder, "2_Psych_Adjusted_Stats.xlsx"))
    
    plt.figure(figsize=(14, 7))
    sns.boxplot(data=df_psych[psych_cols], palette="Greens")
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Score (0-100%)")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "2_Psych_Adjusted_Boxplot.png"))
    plt.close()

    print("       ...Unadjusted")
    raw_cols = [f"{c}_RAW" for c in psych_cols]
    
    df_raw_plot = df_psych[raw_cols].copy()
    df_raw_plot.columns = psych_cols 
    
    df_raw_plot.describe().transpose().to_excel(os.path.join(output_folder, "2_Psych_Unadjusted_Stats.xlsx"))
    
    plt.figure(figsize=(14, 7))
    sns.boxplot(data=df_raw_plot, palette="Greens") 
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Score (0-100%)")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "2_Psych_Unadjusted_Boxplot.png"))
    plt.close()

    # ---------------------------------------------------------
    # Einfluss Erfahrung (Psych)
    # ---------------------------------------------------------
    print("    -> 3: Einfluss Erfahrung (Heatmap)...")
    
    corr_psych = df_psych[pe_cols + psych_cols].corr(method='spearman').loc[psych_cols, pe_cols]
    
    corr_psych.to_excel(os.path.join(output_folder, "3_Psych_Korrelation_Spearman.xlsx"))
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_psych, annot=True, cmap="coolwarm", center=0, fmt=".2f")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "3_Psych_Heatmap_Spearman.png"))
    plt.close()
    
    # ---------------------------------------------------------
    # Cronbachs Alpha
    # ---------------------------------------------------------
    alphas = []
    for cat, conf in psych_config.items():
        alphas.append({'Kategorie': cat, 'Alpha': cronbach_alpha(df_raw[conf['columns']])})
    pd.DataFrame(alphas).to_excel(os.path.join(output_folder, "4_Psych_Alpha.xlsx"))


    # =========================================================
    # TEIL B: Programmierstrategien (Fachlich)
    # =========================================================
    print("\n>>> [Teil B] Analysiere Programmierstrategien...")
    prog_cols = list(prog_config.keys())

    # ---------------------------------------------------------
    # Programmierstrategien (Zweifach sortiert)
    # ---------------------------------------------------------
    print("    -> 1: Prog. Strategien (Boxplot)...")

    prog_stats_temp = pd.DataFrame({
        'median': df_prog[prog_cols].median(),
        'mean': df_prog[prog_cols].mean()
    }).sort_values(by=['median', 'mean'], ascending=False)

    sorted_cols = prog_stats_temp.index.tolist()

    df_prog[sorted_cols].describe().transpose().to_excel(os.path.join(output_folder, "1_Prog_Strategien_Stats.xlsx"))

    plt.figure(figsize=(12, 12))
    sns.boxplot(data=df_prog[sorted_cols], orient='h', palette="Greens")
    plt.xlabel("Mittelwert (1=nie, 5=sehr oft)")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "1_Prog_Strategien_Boxplot.png"))
    plt.close()

    # ---------------------------------------------------------
    # Einfluss Erfahrung (Prog)
    # ---------------------------------------------------------
    print("    -> 3: Einfluss Erfahrung (Heatmap)...")
    
    corr_prog = df_prog[pe_cols + prog_cols].corr(method='spearman').loc[prog_cols, pe_cols]
    
    corr_prog.to_excel(os.path.join(output_folder, "3_Prog_Strategien_Korrelation_Spearman.xlsx"))
    
    plt.figure(figsize=(12, 12))
    sns.heatmap(corr_prog, annot=True, cmap="coolwarm", center=0, fmt=".2f", cbar_kws={'label': 'Spearman Korrelation'})
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "3_Prog_Strategien_Heatmap_Spearman.png"))
    plt.close()

    print(f"\nFERTIG! Alle Analysen und CSVs in: {output_folder}")
else:
    print("Fehler: Keine Daten.")