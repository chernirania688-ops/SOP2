import streamlit as st
import pandas as pd
import plotly.express as px
import agents as ag
import os
from crewai import Task, Crew

st.set_page_config(page_title="S&OP Agentic AI", layout="wide")

# --- 1. FONCTIONS DE CALCUL ET D'AFFICHAGE (Style Photo) ---

def generer_analyse_visuelle(df):
    """Génère le tableau de bord structuré comme sur la photo."""
    # --- CALCULS TECHNIQUES ---
    # On essaie d'extraire les valeurs réelles depuis l'Excel
    try:
        capa_h = df[df['Donnees'].str.contains('Available capacity', na=False)].iloc[0, 3] # W34
        taux_u = df[df['Donnees'].str.contains('Variable requirement', na=False)].iloc[0, 3]
    except:
        capa_h = 1400
        taux_u = 0.4667
        
    max_prod = int(capa_h / taux_u) if taux_u > 0 else 3000

    # --- EN-TÊTE (METRICS) ---
    st.markdown("---")
    st.subheader("📊 PARAMÈTRES INDUSTRIELS — ARTICLE A1")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Capacité PHR/sem", f"{capa_h:,.0f}")
    m2.metric("Taux PHR/U", f"{taux_u:.4f}")
    m3.metric("Max prod. U/sem", f"{max_prod:,.0f}", "nominal")
    m4.metric("Stock Initial U", "13 494")
    m5.metric("Safety stock U", "4.17")

    # --- ALERTES CRITIQUES ---
    st.markdown("### ⚠️ ALERTES CRITIQUES")
    
    # Vérification surcharge W40
    try:
        demande_w40 = df[df['Donnees'].str.contains('Gross requirements', na=False)]['W40 Y23'].values[0]
        if demande_w40 > max_prod:
            st.error(f"**Pic de demande insurmontable :** W40 demande {demande_w40:,.0f} U alors que la capacité max est de {max_prod} U. Sous-traitance obligatoire.")
    except:
        st.info("Données W40 non disponibles pour alerte.")

    st.warning("**Rupture de stock progressive :** dès W39, le stock devient négatif si le plan n'est pas lissé.")
    st.info("**Stock tampon W34-W38 :** le stock initial absorbe la demande jusqu'à la fin du mois.")

    # --- OPTIONS D'ACTION ---
    st.markdown("### 🛠️ OPTIONS D'ACTION CHIFFRÉES")
    colA, colB = st.columns(2)
    with colA:
        with st.container(border=True):
            st.write("**[A] Réduction Demande**")
            st.write(f"Plafonner à {max_prod} U/sem. Risque : Perte de CA.")
    with colB:
        with st.container(border=True):
            st.write("**[B] Heures supp +25%**")
            st.write(f"Capacité passe à {int(max_prod*1.25)} U/sem. Coût Main d'oeuvre +25%.")

# --- 2. LOGIQUE DES AGENTS ---

def executer_analyse(agent, fichier, prompt):
    tache = Task(
        description=f"Analyse le fichier {fichier}. {prompt}",
        expected_output="Une analyse détaillée.",
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[tache])
    return crew.kickoff()

# --- 3. INTERFACE STREAMLIT ---

st.title("🏭 Plateforme S&OP Agentique Interactive")

tab_dash, tab_mkt, tab_dem, tab_prod, tab_fin, tab_orch = st.tabs([
    "📊 Dashboard", "📢 Marketing", "📈 Demande", "⚙️ Production", "💰 Finance", "🏆 Orchestrateur"
])

def rendu_onglet_agent(onglet, agent, nom_fichier_defaut):
    with onglet:
        col_txt, col_file = st.columns([2, 1])
        with col_file:
            st.markdown("### 📥 Importation")
            u_file = st.file_uploader(f"Charger Excel {agent.role}", type=['xlsx'], key=f"up_{agent.role}")
            if u_file:
                with open(nom_fichier_defaut, "wb") as f: f.write(u_file.getbuffer())
                st.success("Fichier synchronisé !")

        with col_txt:
            st.subheader(f"🧠 Assistant : {agent.role}")
            if os.path.exists(nom_fichier_defaut):
                df = pd.read_excel(nom_fichier_defaut)
                st.dataframe(df.head(5))
                
                c1, c2 = st.columns(2)
                if c1.button("📉 Vision Globale (Style S&OP)", key=f"v_{agent.role}"):
                    generer_analyse_visuelle(df)
                
                if c2.button("🔍 Analyse par l'Agent IA", key=f"ai_{agent.role}"):
                    res = executer_analyse(agent, nom_fichier_defaut, "Fais une analyse critique des données.")
                    st.write(res.raw)

                # Question libre
                ordre = st.text_input("Poser une question ou donner un ordre :", key=f"q_{agent.role}")
                if st.button("Lancer l'ordre", key=f"b_{agent.role}"):
                    res = executer_analyse(agent, nom_fichier_defaut, ordre)
                    st.info(res.raw)

# Rendu des onglets
rendu_onglet_agent(tab_mkt, ag.marketing, "mkt_data.xlsx")
rendu_onglet_agent(tab_dem, ag.demand_planner, "dem_data.xlsx")
rendu_onglet_agent(tab_prod, ag.production, "prod_data.xlsx")
rendu_onglet_agent(tab_fin, ag.finance, "fin_data.xlsx")

# --- DASHBOARD ---
with tab_dash:
    if os.path.exists("prod_data.xlsx"):
        df_p = pd.read_excel("prod_data.xlsx")
        df_numerique = df_p.set_index('Donnees').select_dtypes(include=['number'])
        fig = px.line(df_numerique.T, title="Comparaison Offre vs Demande")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("En attente de données pour le graphique.")

# --- ORCHESTRATEUR ---
with tab_orch:
    scenario = st.text_area("Entrez un scénario global :")
    if st.button("Lancer l'Orchestration"):
        equipe = Crew(
            agents=[ag.marketing, ag.demand_planner, ag.production, ag.finance],
            tasks=[Task(description=scenario, agent=ag.orchestrator, expected_output="Décision finale")],
            verbose=True
        )
        st.markdown(equipe.kickoff().raw)
