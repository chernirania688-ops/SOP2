import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

# --- CONFIGURATION SÉCURISÉE ---
st.set_page_config(page_title="S&OP Master", layout="wide")

# Récupération de la clé depuis les secrets de Streamlit
# Si tu es en local, crée .streamlit/secrets.toml avec GROQ_API_KEY="ta_cle"
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ Clé API manquante dans les Secrets Streamlit !")
    st.stop()

# Utilisation d'un modèle plus léger pour éviter les blocages de quota
cerveau = LLM(model="groq/llama3-8b-8192", api_key=api_key)

# --- 1. LES OUTILS (TOOLS) ---
@tool("modifier_excel")
def modifier_excel(ligne: int, colonne: str, valeur: float):
    """Modifie une cellule dans le fichier prod_data.xlsx."""
    try:
        df = pd.read_excel("prod_data.xlsx")
        df.at[ligne, colonne] = valeur
        df.to_excel("prod_data.xlsx", index=False)
        return f"Succès : {colonne} mis à jour."
    except Exception as e:
        return f"Erreur : {e}"

# --- 2. LES AGENTS ---
def creer_expert(role, goal, backstory, tools=[]):
    return Agent(
        role=role, goal=goal, backstory=backstory,
        llm=cerveau, verbose=True, allow_delegation=False,
        max_rpm=1, max_iter=1, tools=tools, memory=False
    )

marketing = creer_expert("Marketing", "Analyser l'image", "Expert en stratégie.")
demand_planner = creer_expert("Demand", "Calculer forecast", "Expert en chiffres.")
production = creer_expert("Production", "Gérer capacité", "Expert industriel.", [modifier_excel])
finance = creer_expert("Finance", "Calculer profit", "Expert rentabilité.")
orchestrator = creer_expert("Directeur S&OP", "Prendre la décision", "Arbitre final.")

# --- 3. LOGIQUE D'INTERFACE ---
st.title("🏭 Cockpit S&OP Master - IFBrain")

if 'logs' not in st.session_state:
    st.session_state.logs = {k: "" for k in ["Marketing", "Demand", "Production", "Finance", "Final"]}

tabs = st.tabs(["📢 Marketing", "📈 Demande", "⚙️ Production", "💰 Finance", "🏆 Orchestrateur"])

def rendu_onglet(onglet, agent, file_name, label):
    with onglet:
        c_tab, c_file = st.columns([3, 1])
        with c_file:
            f = st.file_uploader(f"Import {label}", type=['xlsx'], key=f"up_{label}")
            if f:
                with open(file_name, "wb") as file: file.write(f.getbuffer())
                st.success("Chargé")
        
        with c_tab:
            if os.path.exists(file_name):
                df = pd.read_excel(file_name)
                st.write(f"### Espace {label}")
                
                col_b1, col_b2, col_b3 = st.columns(3)
                if col_b1.button("📉 Vision Globale", key=f"v_{label}"):
                    st.metric("Max Capacité", "3000")
                    if "W40 Y23" in df.columns:
                        val = df.iloc[0]["W40 Y23"]
                        st.warning(f"Demande W40 : {val}")
                
                if col_b2.button("🔍 Analyse IA", key=f"a_{label}"):
                    with st.spinner("Réflexion..."):
                        t = Task(description=f"Analyse les 5 premières lignes de ce fichier : {df.head(5).to_string()}", 
                                 agent=agent, expected_output="Rapport court.")
                        res = Crew(agents=[agent], tasks=[t]).kickoff()
                        st.session_state.logs[label] = res.raw
                
                if col_b3.button("⚡ Corriger W40", key=f"c_{label}"):
                    with st.spinner("L'IA modifie l'Excel..."):
                        t = Task(description=f"Utilise 'modifier_excel' pour mettre 3000 en 'W40 Y23' ligne 7 dans {file_name}", 
                                 agent=agent, expected_output="Fait.")
                        Crew(agents=[agent], tasks=[t]).kickoff()
                        st.success("Modifié !")
                        time.sleep(2)
                        st.rerun()

                if st.session_state.logs[label]:
                    st.info(st.session_state.logs[label])
                st.dataframe(df)

rendu_onglet(tabs[0], marketing, "mkt_data.xlsx", "Marketing")
rendu_onglet(tabs[1], demand_planner, "dem_data.xlsx", "Demand")
rendu_onglet(tabs[2], production, "prod_data.xlsx", "Production")
rendu_onglet(tabs[3], finance, "fin_data.xlsx", "Finance")

with tabs[4]:
    st.header("🏆 Décision Finale")
    scen = st.text_area("Scénario :")
    if st.button("🚀 Lancer l'Orchestration"):
        t = Task(description=f"Analyse ce scénario avec les autres experts : {scen}", agent=orchestrator, expected_output="Décision")
        res = Crew(agents=[orchestrator], tasks=[t]).kickoff()
        st.markdown(res.raw)
