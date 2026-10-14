PREMIER_GAGNE = "premier_gagne"
SECOND_GAGNE = "second_gagne"
EGALITE = "egalite"


def texte_resultat(resultat, joueur1, joueur2):
    """Renvoie la phrase qui annonce l'égalité ou le gagnant d'une partie."""
    if resultat == EGALITE:
        return "Égalité !"
    if resultat == PREMIER_GAGNE:
        return f"Le gagnant est : {joueur1['nom']}"
    return f"Le gagnant est : {joueur2['nom']}"
