import streamlit as st
from math import ceil

# Dati e configurazioni iniziali
MACRO_TERRITORIES = {
    "Skincare": {"text_pct": 0.90, "media_pct": 0.10},
    "Make Up": {"text_pct": 0.60, "media_pct": 0.40},
    "Fragrance": {"text_pct": 0.90, "media_pct": 0.10},
}
# Se esistono alias per i macro territories, definirli qui
ALIASES = {
    # Esempio: "skin care": "Skincare"
}

# Funzioni di utilità
def normalize_macro_territory(value: str) -> str:
    key = value.strip()
    low = key.lower()
    if low in ALIASES:
        return ALIASES[low]
    for k in MACRO_TERRITORIES:
        if k.lower() == low:
            return k
    raise ValueError(f"Invalid macro territory: {value}")

def maturity_assessment(coverage_ratio: float) -> str:
    """
    Maintenance >= 70%
    Scale      >= 30% e < 70%
    Growth     < 30%
    """
    if coverage_ratio >= 0.70:
        return "Maintenance"
    elif coverage_ratio >= 0.30:
        return "Scale"
    else:
        return "Growth"

def contents_per_queries(maturity: str) -> int:
    return {"Maintenance": 150, "Scale": 100, "Growth": 50}[maturity]

def calculate_plan(macro_territory: str, territory: str, overall_queries: int, covered_queries: int):
    if overall_queries <= 0:
        raise ValueError("Overall Keywords must be > 0.")
    if covered_queries < 0:
        raise ValueError("DMI Keywords cannot be < 0.")
    if covered_queries > overall_queries:
        # Se oltre il 100%, clamp a 100%
        covered_queries = overall_queries

    macro = normalize_macro_territory(macro_territory)
    coverage_ratio = covered_queries / overall_queries
    maturity = maturity_assessment(coverage_ratio)
    gap_queries = max(overall_queries - covered_queries, 0)
    divisor = contents_per_queries(maturity)
    recommended_contents = ceil(gap_queries / divisor)
    split = MACRO_TERRITORIES[macro]
    text_contents = ceil(recommended_contents * split["text_pct"])
    media_contents = recommended_contents - text_contents  # resto

    return {
        "macro_territory": macro,
        "territory": territory.strip(),
        "overall_queries": overall_queries,
        "covered_queries": covered_queries,
        "coverage_ratio": coverage_ratio,
        "maturity": maturity,
        "gap_queries": gap_queries,
        "recommended_contents": recommended_contents,
        "split": {
            "text_contents": text_contents,
            "media_contents": media_contents,
            "text_pct": split["text_pct"],
            "media_pct": split["media_pct"],
        },
    }

def format_md(res: dict) -> str:
    pct = round(res["coverage_ratio"] * 100, 2)
    mt = res["maturity"]
    # Legenda soglie di maturità
    legend = (
        "- **Maintenance**: ≥ 70%\n"
        "- **Scale**: ≥ 30% e < 70%\n"
        "- **Growth**: < 30%\n"
    )
    md = f"""
### Results
**Macro Territory:** {res['macro_territory']}
**Territory:** {res['territory']}

**Coverage:** **{pct}%** → **Maturity: {mt}**
{legend}

**Query Gap:** {res['gap_queries']}

### Recommended Contents
Content Pieces: **{res['recommended_contents']}**

**Content Formats**
- Articles: **{res['split']['text_contents']}** ({int(res['split']['text_pct']*100)}%)
- Media Contents: **{res['split']['media_contents']}** ({int(res['split']['media_pct']*100)}%)
"""
    return md

# Titolo dell'app (facoltativo)
st.title("Keyword Coverage Planner")

# Widget di input per i parametri
selected_macro = st.selectbox("Area:", list(MACRO_TERRITORIES.keys()), index=0)
territory = st.text_input("Territory:", placeholder="es. anti-acne")
overall = st.number_input("Overall KWs:", min_value=1, value=0)
covered = st.number_input("DMI KWs:", min_value=0, value=0)

# Pulsante per calcolare il piano
if st.button("Calculate"):
    try:
        res = calculate_plan(selected_macro, territory, int(overall), int(covered))
        output_md = format_md(res)
        st.markdown(output_md)  # Mostra i risultati formattati in Markdown
    except Exception as e:
        st.error(f"Errore: {e}")
