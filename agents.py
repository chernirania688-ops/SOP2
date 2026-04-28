import os
import streamlit as st
from crewai import Agent, LLM
from tools import SOPTools  # <--- CETTE LIGNE EST INDISPENSABLE

# Configuration de la clé API (via les secrets Streamlit)
api_key = st.secrets.get("GROQ_API_KEY", "")

if not api_key:
    st.error("La clé API Groq est manquante dans les Secrets Streamlit.")

# Initialisation du cerveau
cerveau = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=api_key
)

def creer_agent_sop(role, goal, backstory):
    return Agent(
        role=role, 
        goal=goal, 
        backstory=backstory,
        llm=cerveau, 
        verbose=True, 
        allow_delegation=False, # Désactivez la délégation pour économiser des jetons
        max_rpm=1,             # <--- FORCE 1 requête par minute maximum
        max_iter=3,            # <--- LIMITE à 3 réflexions maximum par tâche
        tools=[SOPTools.analyser_et_corriger_excel, SOPTools.calculer_kpis]
    )
# --- DÉFINITION DES AGENTS ---
marketing = creer_agent_sop("Directeur Marketing", "Analyser l'image et booster les ventes", "Tu es expert en tendances.")
demand_planner = creer_agent_sop("Demand Planner", "Prédire la demande via lissage", "Tu corriges les forecasts.")
production = creer_agent_sop("Chef de Production", "Gérer la capacité Fill-L1", "Tu calcules la surcharge.")
finance = creer_agent_sop("CFO", "Garantir la rentabilité", "Tu analyses le profit.")
orchestrator = creer_agent_sop("Directeur S&OP", "Orchestrer le consensus", "Tu es le chef d'orchestre.")
