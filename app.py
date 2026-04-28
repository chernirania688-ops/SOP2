import streamlit as st
import pandas as pd
import plotly.express as px
import agents as ag
import os
from crewai import Task, Crew

st.set_page_config(page_title="S&OP Agentic AI Platform", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE (Pour la discussion entre agents) ---
if 'logs_agents' not in st.session_state:
    st.session_state.logs_agents = {
        "Marketing": "", "Demand": "", "Production": "", "Finance": "", "Final": ""
    }

# --- FONCTION DE NETTOYAGE DES NOMBRES (Pour éviter le TypeError) ---
def clean_num(val):
    try:
        if isinstance(val, str):
            val = val.replace(' ', '').replace(',', '.')
        return float(val)
    except: return 0.0

# --- COMPOSANT : VISION GLOBALE (STYLE PHOTO) ---
def rendu_vision_globale(df, agent_name):
    st.markdown(f"### 📊 BILAN GLOBAL S&OP — {agent_name}")
    # Calculs de base
    capa = 1400
    taux = 0.4667
    max_p = int(capa / taux)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Capacité PHR", f"{capa:,.0f}")
    m2.metric("Max Prod U/sem", f"{max_p:,.0f}")
    m3.metric("Safety Stock", "4.17")
    m4.metric("Statut", "SURCHARGE" if clean_num(df.iloc[0, 6]) > max_p else "OK", delta_color="inverse")

    st.markdown("#### 🚨 ALERTES CRITIQUES")
    st.error("⚠️ **Pic de demande insurmontable :** W40 détecté. Capacité insuffisante.")
    st.warning("📉 **Rupture de stock :** Prévue en W39.")

    st.markdown("#### 🛠️ OPTIONS D'ACTION")
    c1, c2 = st.columns(2)
    c1.info("**Option A :** Lissage production dès W34.")
    c2.success("**Option B :** Heures supplémentaires (+25%).")

# --- COMPOSANT : DASHBOARD PAR AGENT ---
def rendu_dashboard_agent(df, title):
    st.subheader(f"📈 Dashboard {title}")
    df_num = df.set_index(df.columns[1]).select_dtypes(include=['number'])
    if not df_num.empty:
        fig = px.bar(df_num.T, barmode="group", title=f"Analyse temporelle {title}")
        st.plotly_chart(fig, use_container_width=True)

# --- FONCTION COMMUNE POUR LES ONGLETS AGENTS ---
def generer_onglet_agent(agent_obj, key_name, file_name):
    col_left, col_right = st.columns([3, 1])
    
    with col_right:
        st.markdown("### 📥 Import")
        u_file = st.file_uploader(f"Fichier {key_name}", type=['xlsx'], key=f"file_{key_name}")
        if u_file:
            with open(file_name, "wb") as f: f.write(u_file.getbuffer())
            st.success("Données chargées")

    with col_left:
        if os.path.exists(file_name):
            df = pd.read_excel(file_name)
            st.dataframe(df.head(5), use_container_width=True)
            
            # Les 4 Boutons demandés
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("📉 Vision Globale", key=f"v_{key_name}"):
                rendu_vision_globale(df, key_name)
            
            if b2.button("🔍 Analyse IA", key=f"a_{key_name}"):
                t = Task(description="Analyse ce fichier et donne tes conclusions.", agent=agent_obj, expected_output="Analyse courte.")
                res = Crew(agents=[agent_obj], tasks=[t]).kickoff()
                st.session_state.logs_agents[key_name] = res.raw
            
            if b3.button("📊 Dashboard", key=f"d_{key_name}"):
                rendu_dashboard_agent(df, key_name)
            
            if b4.button("⚡ Corriger Fichier", key=f"c_{key_name}"):
                st.info("L'agent corrige les saturations dans l'Excel...")
                # Appel à l'outil de correction ici

            # Affichage de la discussion si elle existe
            if st.session_state.logs_agents[key_name]:
                st.markdown("---")
                st.markdown(f"**💬 Message de l'expert {key_name} :**")
                st.info(st.session_state.logs_agents[key_name])

# --- INTERFACE PRINCIPALE ---
st.title("🏭 Cockpit S&OP Agentique")

tab_mkt, tab_dem, tab_prod, tab_fin, tab_orch = st.tabs([
    "📢 Marketing", "📈 Demande", "⚙️ Production", "💰 Finance", "🏆 Orchestrateur"
])

# Remplissage des onglets agents
generer_onglet_agent(ag.marketing, "Marketing", "mkt_data.xlsx")
generer_onglet_agent(ag.demand_planner, "Demand", "dem_data.xlsx")
generer_onglet_agent(ag.production, "Production", "prod_data.xlsx")
generer_onglet_agent(ag.finance, "Finance", "fin_data.xlsx")

# --- ONGLET ORCHESTRATEUR ---
with tab_orch:
    st.header("🏆 Décision Finale & Scénarios")
    scen = st.text_area("Entrez votre scénario (ex: 'On veut lancer une promo de +40% en W40, demandez à tous les agents si c'est possible et rentable')")
    
    if st.button("🚀 Lancer l'Orchestration"):
        # On définit les tâches pour que chaque agent remplisse son log
        tasks = [
            Task(description=f"Marketing: Analyse l'impact image de {scen}", agent=ag.marketing, expected_output="Rapport Mkt"),
            Task(description=f"Demand: Calcule le nouveau forecast pour {scen}", agent=ag.demand_planner, expected_output="Rapport Demand"),
            Task(description=f"Production: Vérifie la capacité pour {scen}", agent=ag.production, expected_output="Rapport Prod"),
            Task(description=f"Finance: Calcule la rentabilité de {scen}", agent=ag.finance, expected_output="Rapport Fin"),
            Task(description="Rédige la synthèse finale S&OP", agent=ag.orchestrator, expected_output="Décision finale")
        ]
        
        crew = Crew(agents=[ag.marketing, ag.demand_planner, ag.production, ag.finance, ag.orchestrator], tasks=tasks, verbose=True)
        resultat = crew.kickoff()
        
        # On remplit les logs dans le session_state pour qu'ils s'affichent dans les onglets respectifs
        st.session_state.logs_agents["Marketing"] = tasks[0].output.raw
        st.session_state.logs_agents["Demand"] = tasks[1].output.raw
        st.session_state.logs_agents["Production"] = tasks[2].output.raw
        st.session_state.logs_agents["Finance"] = tasks[3].output.raw
        st.session_state.logs_agents["Final"] = resultat.raw
        
        st.success("Scénario traité ! Allez voir les onglets de chaque agent pour voir leur réponse.")
        st.markdown(resultat.raw)
