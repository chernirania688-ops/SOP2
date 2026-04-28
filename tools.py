import pandas as pd
import os
from crewai.tools import tool

class SOPTools:
    @tool("analyser_et_corriger_excel")
    def analyser_et_corriger_excel(chemin_fichier: str, instruction: str):
        """Lit un fichier, applique une logique de correction (ex: plafonner la prod) et sauvegarde."""
        try:
            df = pd.read_excel(chemin_fichier)
            # Ici on peut ajouter une logique spécifique ou laisser le LLM proposer via un script
            # Pour l'exemple, on simule une correction de capacité
            if "plafonner" in instruction.lower():
                if "Capacity" in df.columns:
                    df["Production_Plan"] = df["Capacity"] # Exemple d'action
            
            df.to_excel(chemin_fichier, index=False)
            return f"Action réussie sur {chemin_fichier} : {instruction}"
        except Exception as e:
            return f"Erreur : {str(e)}"

    @tool("calculer_kpis")
    def calculer_kpis(chemin_fichier: str):
        """Calcule les indicateurs clés (Saturation, Marge) à partir d'un fichier."""
        df = pd.read_excel(chemin_fichier)
        summary = df.describe().to_string()
        return f"Résumé statistique du fichier :\n{summary}"