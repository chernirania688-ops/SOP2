import pandas as pd
import os
from crewai.tools import tool

class SOPTools:
    @tool("lire_donnees")
    def lire_donnees(chemin_fichier: str):
        """Lit un fichier Excel et retourne les 15 premières lignes pour analyse."""
        if not os.path.exists(chemin_fichier):
            return "Erreur : Le fichier est introuvable."
        df = pd.read_excel(chemin_fichier)
        return df.head(15).to_string()

    @tool("modifier_cellule")
    def modifier_cellule(chemin_fichier: str, ligne: int, colonne: str, valeur: float):
        """Modifie une cellule précise. ligne: index (0,1,2..), colonne: nom (ex: 'W40 Y23')."""
        try:
            df = pd.read_excel(chemin_fichier)
            df.at[ligne, colonne] = valeur
            df.to_excel(chemin_fichier, index=False)
            return f"✅ Modification réussie : {colonne} à la ligne {ligne} est maintenant à {valeur}."
        except Exception as e:
            return f"❌ Erreur : {str(e)}"
