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
marketing = creer_agent("Directeur Marketing", "Analyser l'image de marque et les promos.", 
    "Tu es expert en stratégie. Tu ne valides que ce qui booste la marque.")

demand_planner = creer_agent("Demand Planner", "Prédire et corriger le forecast.", 
    "Expert en lissage (LES/HW). Tu dois utiliser 'modifier_cellule' pour corriger les erreurs de prévision.", [SOPTools.lire_donnees, SOPTools.modifier_cellule])

production = creer_agent("Chef de Production", "Gérer la capacité et les surcharges.", 
    "Expert industriel. Ta limite est 3000 U/sem. Tu DOIS utiliser 'modifier_cellule' pour plafonner le plan de prod.", [SOPTools.lire_donnees, SOPTools.modifier_cellule])

finance = creer_agent("CFO / Finance", "Calculer le profit et la rentabilité.", 
    "Tu ne jures que par l'EBITDA. Tu calcules si produire plus est rentable ou non.")

orchestrator = creer_agent("Directeur S&OP", "Prendre la décision finale et arbitrer.", 
    "Tu es le chef d'orchestre. Tu synthétises les avis des 4 autres experts pour donner un ordre final.")
