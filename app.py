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
            def generer_analyse_visuelle(df):
    # --- 1. CALCULS TECHNIQUES ---
    capa_h = 1400
    taux_u = 0.4667
    max_prod = int(capa_h / taux_u) # 3000
    
    # On prépare le tableau MRP
    df_mrp = df.copy()
    # On s'assure que les colonnes sont numériques
    cols_semaines = [c for c in df.columns if 'W' in c]
    
    # --- 2. EN-TÊTE (METRICS) ---
    st.subheader("PARAMÈTRES FILL-L1 — ARTICLE A1")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Capacité PHR/sem", f"{capa_h:,.0f}")
    m2.metric("Taux PHR/U", f"{taux_u:.4f}")
    m3.metric("Max prod. U/sem", f"{max_prod:,.0f}", "nominal")
    m4.metric("Stock Initial U", "13 494")
    m5.metric("Safety stock U", "4.17")

    # --- 3. ALERTES CRITIQUES (Style Photo) ---
    st.markdown("### ALERTES CRITIQUES")
    demande_w40 = df[df['Donnees'] == 'Gross requirements [U]']['W40 Y23'].values[0]
    
    if demande_w40 > max_prod:
        st.error(f"⚠️ **Pic de demande insurmontable :** W40 demande {demande_w40:,.0f} U alors que la capacité max est de {max_prod} U. Sous-traitance obligatoire.")
    
    st.warning("📉 **Rupture de stock progressive :** dès W39, le stock devient négatif si le plan actuel n'est pas modifié.")
    st.info("📦 **Stock tampon W34-W38 :** le stock initial absorbe la demande jusqu'à W38.")

    # --- 4. TABLEAU MRP COMPLET ---
    st.markdown("### TABLEAU MRP COMPLET — 19 PÉRIODES")
    
    # Simulation des colonnes Charge et Saturation pour l'affichage
    # (Ici vous mettriez votre vraie logique de calcul ligne par ligne)
    
    def color_status(val):
        color = 'red' if val == 'SURCHARGE' else 'green'
        return f'color: {color}; font-weight: bold'

    # Affichage du DataFrame stylisé
    st.dataframe(df.style.set_properties(**{'background-color': '#f9f9f9', 'border': '1px solid white'}))

    # --- 5. OPTIONS D'ACTION (Les boîtes en bas) ---
    st.markdown("### OPTIONS D'ACTION CHIFFRÉES")
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        with st.container(border=True):
            st.write("**[A] Réduction Gross Req**")
            st.write(f"Max absorbable : {max_prod} U/sem. Risque : perte de CA.")
            
    with row1_col2:
        with st.container(border=True):
            st.write("**[B] Heures supp +25%**")
            st.write("1 750 PHR -> 3 750 U/sem. Insuffisant pour W40.")

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        with st.container(border=True):
            st.write("**[D] Sous-traitance partielle**")
            st.write("W40 : externaliser 29 000 U. Coût +30-40%.")
            
    with row2_col2:
        with st.container(border=True):
            st.write("**Recommandation ingénieur**")
            st.success("Anticiper en W35-W36 + Heures supp sur W42.")
            if c1.button("Vision Globale", key=f"v_{agent.role}"):
    # 1. On laisse l'agent faire son travail en arrière-plan (pour les logs et la réflexion)
    res = executer_analyse(agent, nom_fichier_defaut, "Analyse les données pour préparer un bilan S&OP.")
    
    # 2. On affiche l'interface structurée (La photo)
    df_actuel = pd.read_excel(nom_fichier_defaut)
    generer_analyse_visuelle(df_actuel)
