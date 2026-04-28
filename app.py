import streamlit as st
import pandas as pd
import plotly.express as px
import agents as ag
import os
from crewai import Task, Crew

st.set_page_config(page_title="IFBrain Consulting - S&OP Cockpit", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE ---
if 'logs' not in st.session_state:
    st.session_state.logs = {k: "" for k in ["Marketing", "Demande", "Production", "Finance", "Orchestrateur"]}
if 'dfs' not in st.session_state:
    st.session_state.dfs = {k: None for k in ["Marketing", "Demande", "Production", "Finance"]}

# --- FONCTION DE NETTOYAGE DES CHIFFRES ---
def clean_df(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = df[col].str.replace(' ', '').str.replace(',', '.').astype(float)
            except: pass
    return df

# --- FONCTION D'ANALYSE IA ---
def lancer_analyse_agent(agent, df, prompt):
    txt_data = df.head(10).to_string()
    tache = Task(
        description=f"Données: {txt_data}. Consigne: {prompt}",
        expected_output="Analyse concise et recommandations.",
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[tache])
    return crew.kickoff().raw

# --- LOGIQUE D'AFFICHAGE D'UN ONGLET AGENT ---
def rendu_agent(nom, agent, key_df):
    # Ligne du haut : Titre à gauche, Import à droite
    header_col, import_col = st.columns([3, 1])
    with header_col:
        st.subheader(f"💼 Espace {nom}")
    with import_col:
        file = st.file_uploader(f"Importer fichier {nom}", type=['xlsx'], key=f"up_{nom}", label_visibility="collapsed")
        if file:
            st.session_state.dfs[key_df] = clean_df(pd.read_excel(file))
            st.success("Fichier importé")

    # Si le fichier est présent, on affiche les boutons et le contenu
    if st.session_state.dfs[key_df] is not None:
        df = st.session_state.dfs[key_df]
        
        # Ligne de 4 boutons (comme sur ton dessin)
        b1, b2, b3, b4 = st.columns(4)
        
        if b1.button(f"🔍 Analyse {nom}", key=f"btn_a_{nom}"):
            with st.spinner("Analyse..."):
                res = lancer_analyse_agent(agent, df, "Fais une analyse globale de la situation.")
                st.session_state.logs[nom] = res
        
        if b2.button(f"📈 Dashboard", key=f"btn_d_{nom}"):
            st.session_state.logs[nom] = "DASHBOARD_MODE"
            
        if b3.button(f"⚠️ Surcharge ?", key=f"btn_s_{nom}"):
            with st.spinner("Vérification..."):
                res = lancer_analyse_agent(agent, df, "Détecte uniquement les surcharges ou anomalies critiques.")
                st.session_state.logs[nom] = res

        b4.button(f"⚙️ Config", key=f"btn_c_{nom}")

        # Affichage des résultats sous les boutons
        if st.session_state.logs[nom] == "DASHBOARD_MODE":
            df_plot = df.select_dtypes(include=['number'])
            if not df_plot.empty:
                fig = px.line(df_plot.T, title=f"Visualisation {nom}")
                st.plotly_chart(fig, use_container_width=True)
        elif st.session_state.logs[nom]:
            st.info(st.session_state.logs[nom])
        
        st.write("---")
        st.write("**Aperçu des données :**")
        st.dataframe(df.head(10), use_container_width=True)

# --- INTERFACE PRINCIPALE (ONGLETS) ---
st.markdown("<h1 style='text-align: center;'>🏭 Cockpit S&OP Agentique</h1>", unsafe_allow_html=True)
st.caption("IFBrain Consulting - Decision Support System")

tab_mkt, tab_dem, tab_prod, tab_fin, tab_orch = st.tabs([
    "Marketing", "Demande", "Production", "Finance", "🏆 Orchestrateur"
])

with tab_mkt: rendu_agent("Marketing", ag.marketing, "Marketing")
with tab_dem: rendu_agent("Demande", ag.demand_planner, "Demande")
with tab_prod: rendu_agent("Production", ag.production, "Production")
with tab_fin: rendu_agent("Finance", ag.finance, "Finance")

# --- ONGLET ORCHESTRATEUR (SCÉNARIO GLOBAL) ---
with tab_orch:
    st.subheader("🏆 Direction Générale & Orchestration")
    
    if st.session_state.logs["Orchestrateur"]:
        st.success("**Décision Finale du Comité S&OP :**")
        st.markdown(st.session_state.logs["Orchestrateur"])

# --- BARRE DE CHAT / SCÉNARIO (TOUT EN BAS) ---
st.markdown("---")
user_input = st.chat_input("Entrez un scénario ou posez une question à l'Orchestrateur...")

if user_input:
    # L'orchestrateur appelle les agents nécessaires
    with st.spinner("L'Orchestrateur consulte les départements..."):
        # On simule la discussion S&OP
        t_global = Task(
            description=f"Scénario: {user_input}. Analyse la situation avec tous les agents et propose un plan.",
            agent=ag.orchestrator,
            expected_output="Rapport de décision final."
        )
        # On crée le processus où les agents discutent
        crew = Crew(
            agents=[ag.marketing, ag.demand_planner, ag.production, ag.finance, ag.orchestrator],
            tasks=[t_global],
            verbose=True
        )
        resultat = crew.kickoff()
        st.session_state.logs["Orchestrateur"] = resultat.raw
        st.rerun()
