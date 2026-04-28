import streamlit as st
import pandas as pd
import plotly.express as px
import agents as ag
import os  # <--- AJOUTE CETTE LIGNE ICI
from crewai import Task, Crew

st.set_page_config(page_title="S&OP Agentic AI", layout="wide")

# --- Initialisation de la mémoire de l'application ---
if 'historique_orchestre' not in st.session_state:
    st.session_state.historique_orchestre = []

# --- Fonction helper pour l'analyse ---
def executer_analyse(agent, fichier, prompt):
    tache = Task(
        description=f"Analyse le fichier {fichier}. {prompt}",
        expected_output="Une analyse détaillée et une confirmation d'action.",
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[tache])
    return crew.kickoff()

# --- INTERFACE ---
st.title("🏭 Plateforme S&OP Agentique Interactive")

tab_dash, tab_mkt, tab_dem, tab_prod, tab_fin, tab_orch = st.tabs([
    "📊 Dashboard", "📢 Marketing", "📈 Demande", "⚙️ Production", "💰 Finance", "🏆 Orchestrateur"
])

# --- FONCTION COMMUNE POUR CHAQUE ONGLET AGENT ---
def rendu_onglet_agent(onglet, agent, nom_fichier_defaut):
    with onglet:
        col1, col2 = st.columns([2, 1])
        with col2:
            u_file = st.file_uploader(f"Importer données {agent.role}", type=['xlsx'], key=f"up_{agent.role}")
            if u_file:
                with open(nom_fichier_defaut, "wb") as f: f.write(u_file.getbuffer())
                st.success("Fichier prêt !")

        with col1:
            st.subheader(f"🧠 Espace de travail : {agent.role}")
            if os.path.exists(nom_fichier_defaut):
                df = pd.read_excel(nom_fichier_defaut)
                st.dataframe(df.head(5))
                
                # Boutons d'actions rapides
                c1, c2, c3 = st.columns(3)
                if c1.button("Vision Globale", key=f"v_{agent.role}"):
                    res = executer_analyse(agent, nom_fichier_defaut, "Donne une vision globale des données.")
                    st.info(res)
                if c2.button("Détecter Surcharge/Alertes", key=f"s_{agent.role}"):
                    res = executer_analyse(agent, nom_fichier_defaut, "Cherche les anomalies ou surcharges.")
                    st.warning(res)
                
                # Q&A Libre
                question = st.text_input("Poser une question ou donner un ordre spécifique :", key=f"q_{agent.role}")
                if st.button("Exécuter", key=f"b_{agent.role}"):
                    res = executer_analyse(agent, nom_fichier_defaut, question)
                    st.success(res)

# Rendu des onglets
rendu_onglet_agent(tab_mkt, ag.marketing, "mkt_data.xlsx")
rendu_onglet_agent(tab_dem, ag.demand_planner, "dem_data.xlsx")
rendu_onglet_agent(tab_prod, ag.production, "prod_data.xlsx")
rendu_onglet_agent(tab_fin, ag.finance, "fin_data.xlsx")

# --- ONGLET DASHBOARD ---
with tab_dash:
    st.header("📈 Tableau de Bord Global")
    
    if os.path.exists("prod_data.xlsx"):
        df_p = pd.read_excel("prod_data.xlsx")
        
        # --- NETTOYAGE POUR LE GRAPHIQUE ---
        # 1. On définit la colonne 'Donnee' comme index pour avoir de jolies légendes
        # 2. On ne garde que les colonnes qui contiennent des nombres (les semaines)
        if 'Donnee' in df_p.columns:
            df_numerique = df_p.set_index('Donnee').select_dtypes(include=['number'])
        else:
            df_numerique = df_p.select_dtypes(include=['number'])
        
        if not df_numerique.empty:
            # On transpose pour avoir le temps (W34, W35...) sur l'axe X
            df_graph = df_numerique.T
            
            fig = px.line(
                df_graph, 
                title="Évolution des indicateurs de Production (S&OP)",
                labels={"index": "Semaines", "value": "Volume"},
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Affichage d'un petit résumé en dessous
            st.subheader("📋 Résumé des données")
            st.dataframe(df_p)
        else:
            st.warning("⚠️ Aucune donnée numérique trouvée dans le fichier pour tracer le graphique.")
            
    else:
        st.info("💡 Chargez des données dans les onglets 'Demande' ou 'Production' pour voir les graphiques s'afficher ici.")
# --- ONGLET ORCHESTRATEUR ---
with tab_orch:
    st.header("🏆 Orchestration des Scénarios")
    scenario = st.text_area("Entrez un scénario complexe (ex: Promotion vs Capacité) :")
    if st.button("Lancer l'Orchestration"):
        # On crée une équipe collaborative
        equipe = Crew(
            agents=[ag.marketing, ag.demand_planner, ag.production, ag.finance],
            tasks=[Task(description=scenario, agent=ag.orchestrator, expected_output="Rapport final décisionnel")],
            verbose=True
        )
        with st.spinner("L'Orchestrateur consulte les experts..."):
            resultat = equipe.kickoff()
            st.markdown(resultat.raw)
            # Log de l'orchestration (simulé par le verbose de CrewAI qui s'affiche en console)
            st.session_state.historique_orchestre.append(f"Scénario: {scenario} -> Résolu")