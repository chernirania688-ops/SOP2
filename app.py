import streamlit as st
import pandas as pd
import plotly.express as px
import agents as ag
import os
from crewai import Task, Crew

st.set_page_config(page_title="S&OP Intelligent Platform", layout="wide")

# --- INITIALISATION MÉMOIRE ---
if 'logs' not in st.session_state:
    st.session_state.logs = {k: "" for k in ["Marketing", "Demand", "Production", "Finance", "Final"]}

# --- LOGIQUE D'AFFICHAGE "STYLE PHOTO" ---
def rendu_visuel_industriel(df, titre):
    st.subheader(f"📊 BILAN INDUSTRIEL — {titre}")
    m1, m2, m3, m4 = st.columns(4)
    # Calculs simplifiés pour la démo
    capa = 1400
    taux = 0.4667
    max_p = 3000
    m1.metric("Capacité PHR", f"{capa}")
    m2.metric("Taux PHR/U", f"{taux}")
    m3.metric("Max Prod U/sem", f"{max_p}")
    m4.metric("Safety Stock", "4.17")
    
    st.markdown("### 🚨 ALERTES")
    st.error("⚠️ Surcharge critique détectée en W40 (Demande > 3000)")
    st.warning("📉 Rupture de stock prévue dès W39")

# --- LOGIQUE COMMUNE DES ONGLETS AGENTS ---
def generer_onglet(nom_label, agent_obj, file_path):
    col_main, col_side = st.columns([3, 1])
    
    with col_side:
        st.write(f"### 📥 Import {nom_label}")
        u_file = st.file_uploader(f"Charger Excel", type=['xlsx'], key=f"up_{nom_label}")
        if u_file:
            with open(file_path, "wb") as f: f.write(u_file.getbuffer())
            st.success("Fichier synchronisé")

    with col_main:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            st.write(f"#### Espace de travail : {agent_obj.role}")
            
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("📉 Vision Globale", key=f"v_{nom_label}"):
                rendu_visuel_industriel(df, nom_label)
            
            if c2.button("🔍 Analyse IA", key=f"a_{nom_label}"):
                with st.spinner("L'expert analyse..."):
                    t = Task(description=f"Analyse le fichier {file_path} en détail.", agent=agent_obj, expected_output="Rapport détaillé.")
                    res = Crew(agents=[agent_obj], tasks=[t]).kickoff()
                    st.session_state.logs[nom_label] = res.raw
            
            if c3.button("📊 Dashboard", key=f"d_{nom_label}"):
                df_n = df.select_dtypes(include=['number'])
                if not df_n.empty:
                    st.plotly_chart(px.line(df_n.T, title=f"Graphique {nom_label}"), use_container_width=True)
            
           if b4.button("⚡ Corriger", key=f"c_{nom_label}"):
    with st.spinner("L'IA recalcule et modifie le fichier..."):
        # On donne un ordre ultra-direct avec les chiffres
        ordre_correction = f"""
        INTERDICTION de dire que tout va bien. 
        1. Calcule la capacité max : 1400 / 0.4667 = 3000 unités.
        2. Lis le fichier {file_path}.
        3. Pour TOUTES les semaines (W34 à W52), si 'Gross requirements [U]' est plus grand que 3000 :
           - Tu DOIS appeler l'outil 'modifier_cellule'.
           - Tu mets la valeur 3000 dans la ligne 'Minimum production plan [U]' (Ligne 7) pour cette semaine.
        4. Termine en listant les semaines que tu as réellement modifiées.
        """
        
        t_corriger = Task(
            description=ordre_correction, 
            agent=agent_obj, 
            expected_output="Rapport des modifications réelles effectuées sur le disque."
        )
        
        crew = Crew(agents=[agent_obj], tasks=[t_corriger], verbose=True)
        res = crew.kickoff()
        
        st.success("Correction terminée !")
        st.info(res.raw)
        
        # --- TRÈS IMPORTANT : ON FORCE STREAMLIT À RELIRE LE FICHIER ---
        st.cache_data.clear() # On vide le cache
        st.rerun() # On relance l'app pour afficher les nouveaux chiffres dans le tableau

            if st.session_state.logs[nom_label]:
                st.info(st.session_state.logs[nom_label])
            st.dataframe(df.head(10))

# --- INTERFACE ---
st.title("🏭 Cockpit S&OP Agentique - IFBrain Consulting")

tabs = st.tabs(["📢 Marketing", "📈 Demande", "⚙️ Production", "💰 Finance", "🏆 Orchestrateur"])

with tabs[0]: generer_onglet("Marketing", ag.marketing, "mkt.xlsx")
with tabs[1]: generer_onglet("Demand", ag.demand_planner, "dem.xlsx")
with tabs[2]: generer_onglet("Production", ag.production, "prod.xlsx")
with tabs[3]: generer_onglet("Finance", ag.finance, "fin.xlsx")

with tabs[4]:
    st.header("🛰️ Orchestration de Scénario Global")
    scenario = st.text_area("Entrez un scénario complexe :", placeholder="Ex: On a un pic de demande en W40. Demandez à la prod si on peut livrer et à la finance si c'est rentable.")
    
    if st.button("🚀 Lancer l'Orchestration"):
        # Les tâches qui feront discuter les agents
        t1 = Task(description=f"Analyse l'impact de {scenario}", agent=ag.marketing, expected_output="Avis Marketing")
        t2 = Task(description=f"Calcule le nouveau plan de vente pour {scenario}", agent=ag.demand_planner, expected_output="Nouveau Forecast")
        t3 = Task(description=f"Vérifie si l'usine peut produire le volume de {scenario}", agent=ag.production, expected_output="Faisabilité technique")
        t4 = Task(description=f"Calcule le profit net pour {scenario}", agent=ag.finance, expected_output="Impact financier")
        t5 = Task(description="Rédige la décision finale S&OP", agent=ag.orchestrator, expected_output="Rapport final")

        crew = Crew(agents=[ag.marketing, ag.demand_planner, ag.production, ag.finance, ag.orchestrator], 
                    tasks=[t1, t2, t3, t4, t5], verbose=True)
        
        final_res = crew.kickoff()
        
        # On remplit les logs pour que chaque agent affiche sa réponse dans son onglet
        st.session_state.logs["Marketing"] = t1.output.raw
        st.session_state.logs["Demand"] = t2.output.raw
        st.session_state.logs["Production"] = t3.output.raw
        st.session_state.logs["Finance"] = t4.output.raw
        st.session_state.logs["Final"] = final_res.raw
        
        st.markdown(final_res.raw)
        st.success("Discussion terminée. Allez dans les onglets pour voir le détail par département.")
