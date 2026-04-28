import streamlit as st
import pandas as pd
import plotly.express as px
import agents as ag
import os
from crewai import Task, Crew

st.set_page_config(page_title="Cockpit S&OP Agentique", layout="wide", page_icon="🏭")

# --- MISSIONS SPÉCIFIQUES POUR ÉVITER LES RÉPÉTITIONS ---
MISSIONS = {
    "Marketing": "Analyse si les volumes de vente supportent l'image de marque. Focus: Part de marché.",
    "Demand": "Analyse la stabilité statistique. Focus: EAM et fiabilité du forecast.",
    "Production": "Analyse les goulots (Capacité 1400h). Focus: Saturation et faisabilité.",
    "Finance": "Analyse les coûts et le profit. Focus: Marge nette et rentabilité."
}

# --- MÉMOIRE DE L'APP ---
if 'logs' not in st.session_state:
    st.session_state.logs = {k: "" for k in ["Marketing", "Demand", "Production", "Finance", "Final"]}

# --- FONCTION DE NETTOYAGE ---
def clean_num(val):
    try:
        if isinstance(val, str): val = val.replace(' ', '').replace(',', '.')
        return float(val)
    except: return 0.0

# --- COMPOSANT : BILAN VISUEL (STYLE PHOTO) ---
def rendu_style_photo(df, titre):
    st.markdown(f"#### 📊 PARAMÈTRES INDUSTRIELS — {titre}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Capacité PHR", "1 400")
    m2.metric("Taux PHR/U", "0.4667")
    m3.metric("Max Prod U/sem", "3 000")
    m4.metric("Safety Stock", "4.17")
    
    st.markdown("---")
    st.error("⚠️ **ALERTE CRITIQUE :** Demande W40 > 3000 U. Rupture immédiate.")
    st.warning("📉 **ALERTE STOCK :** Prévu négatif en W39.")

# --- LOGIQUE DES ONGLETS AGENTS ---
def generer_onglet(nom_label, agent_obj, file_path):
    col_main, col_side = st.columns([3, 1])
    
    with col_side:
        st.markdown("### 📥 Import")
        u_file = st.file_uploader(f"Fichier {nom_label}", type=['xlsx'], key=f"up_{nom_label}")
        if u_file:
            with open(file_path, "wb") as f: f.write(u_file.getbuffer())
            st.success("Fichier chargé")

    with col_main:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            st.write(f"### Espace {nom_label}")
            
            # Les 4 Boutons
            c1, c2, c3, c4 = st.columns(4)
            
            if c1.button("📉 Vision Globale", key=f"v_{nom_label}"):
                rendu_style_photo(df, nom_label)
            
            if c2.button("🔍 Analyse IA Expert", key=f"a_{nom_label}"):
                with st.spinner(f"L'expert {nom_label} réfléchit..."):
                    consigne = MISSIONS.get(nom_label)
                    t = Task(description=f"Données: {df.head(5).to_string()}. Mission: {consigne}", 
                             agent=agent_obj, expected_output="Rapport métier précis.")
                    res = Crew(agents=[agent_obj], tasks=[t]).kickoff()
                    st.session_state.logs[nom_label] = res.raw
                    st.rerun()

            if c3.button("📊 Dashboard", key=f"d_{nom_label}"):
                df_n = df.select_dtypes(include=['number'])
                if not df_n.empty:
                    st.plotly_chart(px.line(df_n.T, title=f"Analytique {nom_label}"))

            if c4.button("⚡ Corriger", key=f"c_{nom_label}"):
                with st.spinner("IA en action..."):
                    t = Task(description=f"Appelle 'modifier_cellule' pour mettre 3000 en W40 (Ligne 7) dans {file_path}", 
                             agent=agent_obj, expected_output="Fait.")
                    Crew(agents=[agent_obj], tasks=[t]).kickoff()
                    st.success("L'Excel a été modifié !")
                    st.rerun()

            if st.session_state.logs.get(nom_label):
                st.info(st.session_state.logs[nom_label])
            st.dataframe(df.head(10), use_container_width=True)

# --- INTERFACE ---
st.title("🏭 IFBrain Consulting - Cockpit S&OP Agentique")

tabs = st.tabs(["📢 Marketing", "📈 Demande", "⚙️ Production", "💰 Finance", "🏆 Orchestrateur"])

with tabs[0]: generer_onglet("Marketing", ag.marketing, "mkt.xlsx")
with tabs[1]: generer_onglet("Demand", ag.demand_planner, "dem.xlsx")
with tabs[2]: generer_onglet("Production", ag.production, "prod.xlsx")
with tabs[3]: generer_onglet("Finance", ag.finance, "fin.xlsx")

with tabs[4]:
    st.header("🏆 Orchestration & Décision Finale")
    scen = st.text_area("Entrez votre scénario :", placeholder="Ex: On a un pic de demande en W40. Demandez à la prod si c'est possible.")
    if st.button("🚀 Lancer l'Analyse Transversale"):
        # Les agents discutent ici
        tasks = [
            Task(description=f"Analyse Marketing de {scen}", agent=ag.marketing, expected_output="Note Mkt"),
            Task(description=f"Analyse Production de {scen}", agent=ag.production, expected_output="Note Prod"),
            Task(description=f"Synthèse finale de {scen}", agent=ag.orchestrator, expected_output="Rapport Final")
        ]
        res = Crew(agents=[ag.marketing, ag.production, ag.orchestrator], tasks=tasks).kickoff()
        st.session_state.logs["Marketing"] = tasks[0].output.raw
        st.session_state.logs["Production"] = tasks[1].output.raw
        st.markdown(res.raw)
        st.success("Consultez les onglets pour voir comment chaque agent a réagi.")
