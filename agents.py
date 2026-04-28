import streamlit as st
import os
from crewai import Agent, LLM

# --- GESTION DE LA CLÉ API ---
# On essaie de récupérer la clé dans les secrets de Streamlit (pour le Cloud)
# Si elle n'existe pas, on regarde dans l'environnement
api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

# On n'initialise le LLM QUE si on a une clé
if api_key:
    os.environ["GROQ_API_KEY"] = api_key
    cerveau = LLM(model="groq/llama-3.1-8b-instant", api_key=api_key)
else:
    cerveau = None # On gérera l'erreur dans l'interface
def creer_agent_sop(role, goal, backstory):
    return Agent(
        role=role, 
        goal=goal, 
        backstory=backstory,
        llm=cerveau, 
        verbose=True, 
        allow_delegation=True,
        max_rpm=2, # <--- AJOUTÉ : limite pour ne pas saturer ton compte gratuit Groq
        tools=[SOPTools.analyser_et_corriger_excel, SOPTools.calculer_kpis]
    )

# --- DÉFINITION DES AGENTS (Noms synchronisés avec app.py) ---

marketing = creer_agent_sop("Directeur Marketing", "Analyser l'image et booster les ventes", "Tu es expert en tendances et promotions.")

# Changement du nom ici : 'demande' devient 'demand_planner'
demand_planner = creer_agent_sop("Demand Planner", "Prédire la demande via lissage", "Tu lis l'historique et tu corriges les forecasts selon l'historique.")

production = creer_agent_sop("Chef de Production", "Gérer la capacité Fill-L1", "Tu calcules la surcharge et lisses la production.")

finance = creer_agent_sop("CFO", "Garantir la rentabilité", "Tu analyses si les modifications sont profitables.")

orchestrator = creer_agent_sop("Directeur S&OP", "Orchestrer le consensus final", "Tu es le chef d'orchestre qui appelle les autres agents.")
