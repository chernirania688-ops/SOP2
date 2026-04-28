import streamlit as st
from crewai import Agent, LLM
from tools import SOPTools

# Récupération sécurisée de la clé
api_key = st.secrets.get("GROQ_API_KEY", "")

# Utilisation du modèle 8b (plus robuste aux quotas gratuits)
cerveau = LLM(model="groq/llama3-8b-8192", api_key=api_key)

def creer_expert(role, goal, backstory, tools_list=[]):
    return Agent(
        role=role, goal=goal, backstory=backstory,
        llm=cerveau, verbose=True, allow_delegation=False,
        max_rpm=1, max_iter=1, tools=tools_list
    )

marketing = creer_expert("Directeur Marketing", "Analyser les parts de marché", 
    "Tu es expert en stratégie commerciale. Ton but est de maximiser la croissance.")

demand_planner = creer_expert("Demand Planner", "Calculer les prévisions", 
    "Tu es un expert statisticien. Tu utilises le lissage pour fiabiliser le forecast.", [SOPTools.lire_donnees, SOPTools.modifier_cellule])

production = creer_expert("Chef de Production", "Gérer la capacité industrielle", 
    "Tu es un ingénieur pragmatique. Ta limite est 3000 U/sem. Tu corriges les surcharges.", [SOPTools.lire_donnees, SOPTools.modifier_cellule])

finance = creer_expert("CFO / Finance", "Garantir la rentabilité du plan", 
    "Tu ne valides que les plans profitables. Tu calcules le ROI et l'impact financier.")

orchestrator = creer_expert("Directeur S&OP", "Arbitrer et finaliser", 
    "Tu es le chef d'orchestre. Tu synthétises les avis des experts pour donner l'ordre final.")
