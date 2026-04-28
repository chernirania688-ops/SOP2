import pandas as pd
import os
from crewai.tools import tool

class SOPTools:
    @tool("lire_donnees")
    def lire_donnees(chemin_fichier: str):
        """Lit un fichier Excel et retourne le contenu sous forme de texte pour analyse."""
        if not os.path.exists(chemin_fichier):
            return f"Erreur : Le fichier {chemin_fichier} est introuvable."
        df = pd.read_excel(chemin_fichier)
        return df.to_string()

    @tool("modifier_cellule")
    def modifier_cellule(chemin_fichier: str, ligne: int, colonne: str, valeur: float):
        """Modifie une cellule précise dans l'Excel. ligne: index (0,1..), colonne: nom (ex: 'W40 Y23')."""
        try:
            df = pd.read_excel(chemin_fichier)
            df.at[ligne, colonne] = valeur
            df.to_excel(chemin_fichier, index=False)
            return f"✅ Modification réussie dans {chemin_fichier} à la ligne {ligne}."
        except Exception as e:
            return f"❌ Erreur de modification : {str(e)}"
