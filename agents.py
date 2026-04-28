import os
import streamlit as st
from crewai import Agent, LLM
from tools import SOPTools

# 1. Clé API
api_key = st.secrets.get("GROQ_API_KEY", "")

# 2. Cerveau IA
cerveau = LLM(model="groq/llama-3.1-8b-instant", api_key=api_key)

# 3. Fonction de création
def creer_agent(role, goal, backstory, tools_list=[]):
    return Agent(
        role=role, goal=goal, backstory=backstory,
        llm=cerveau, verbose=True, allow_delegation=True,
        max_rpm=1, tools=tools_list, max_iter=5
    )

# 4. Définition des agents (NOMS SYNCHRONISÉS AVEC TOOLS.PY)
marketing = creer_agent(
    "Directeur Marketing", 
    "Analyser l'image de marque.", 
    "Tu es expert en stratégie."
)

demand_planner = creer_agent(
    "Demand Planner", 
    "Prédire et corriger le forecast.", 
    "Expert en lissage. Tu DOIS utiliser 'lire_donnees' et 'modifier_cellule'.",
    tools_list=[SOPTools.lire_donnees, SOPTools.modifier_cellule]
)

production = creer_agent(
    "Chef de Production", 
    "Gérer la capacité.", 
    "Expert industriel. Tu DOIS utiliser 'lire_donnees' et 'modifier_cellule'.",
    tools_list=[SOPTools.lire_donnees, SOPTools.modifier_cellule]
)

finance = creer_agent(
    "CFO / Finance", 
    "Calculer la rentabilité.", 
    "Expert en profit."
)

orchestrator = creer_agent(
    "Directeur S&OP", 
    "Arbitrer le consensus final.", 
    "Tu es le chef d'orchestre."
)
