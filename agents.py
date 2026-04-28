import os
import streamlit as st
from crewai import Agent, LLM
from tools import SOPTools

# 1. Gestion de la clé API via les secrets Streamlit
api_key = st.secrets.get("GROQ_API_KEY", "")

# 2. Initialisation du LLM
cerveau = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=api_key
)

# 3. DÉFINITION DE LA FONCTION (Doit être AVANT les agents)
def creer_agent(role, goal, backstory, tools=[]):
    """Fonction helper pour créer un agent avec les paramètres optimisés."""
    return Agent(
        role=role, 
        goal=goal, 
        backstory=backstory,
        llm=cerveau, 
        verbose=True, 
        allow_delegation=True,
        max_rpm=1,      # Limite pour éviter le RateLimitError
        tools=tools, 
        max_iter=5      # Limite les boucles de réflexion
    )

# 4. CRÉATION DES AGENTS (Utilisent la fonction définie juste au-dessus)

marketing = creer_agent(
    "Directeur Marketing", 
    "Analyser l'image de marque et les promos.", 
    "Tu es expert en stratégie. Tu ne valides que ce qui booste la marque."
)

demand_planner = creer_agent(
    "Demand Planner", 
    "Prédire et corriger le forecast.", 
    "Expert en lissage (LES/HW). Tu dois utiliser 'modifier_cellule' pour corriger les erreurs.",
    tools=[SOPTools.lire_donnees, SOPTools.modifier_cellule]
)

production = creer_agent(
    "Chef de Production", 
    "Gérer la capacité et les surcharges.", 
    "Expert industriel. Ta limite est 3000 U/sem. Tu DOIS utiliser 'modifier_cellule' pour plafonner le plan.",
    tools=[SOPTools.lire_donnees, SOPTools.modifier_cellule]
)

finance = creer_agent(
    "CFO / Finance", 
    "Calculer le profit et la rentabilité.", 
    "Tu ne jures que par l'EBITDA. Tu calcules si produire plus est rentable."
)

orchestrator = creer_agent(
    "Directeur S&OP", 
    "Prendre la décision finale et arbitrer.", 
    "Tu es le chef d'orchestre. Tu synthétises les avis des experts pour décider."
)
