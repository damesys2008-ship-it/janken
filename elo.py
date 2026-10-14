from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE

POINTS_PAR_MATCH = 50
ELO_MINIMUM = 0

HISTORIQUE_VICTOIRE = "victoire"
HISTORIQUE_DEFAITE = "defaite"
HISTORIQUE_NUL = "nul"

RATIO_SANS_PARTIE = "N/A"
POURCENT = 100


def entree_historique(jeu, adversaire, issue):
    """Construit l'entrée d'historique d'une partie."""
    return {"jeu": jeu, "adversaire": adversaire["nom"], "resultat": issue}


def enregistrer_partie(joueur, entree):
    """Compte une partie jouée et la range dans l'historique du joueur."""
    joueur["joues"] += 1
    joueur["historique"].append(entree)


def enregistrer_victoire(joueur, jeu, adversaire):
    """Ajoute les points d'une victoire, compte la victoire et la partie."""
    joueur["elo"] += POINTS_PAR_MATCH
    joueur["victoires"] += 1
    enregistrer_partie(joueur, entree_historique(jeu, adversaire, HISTORIQUE_VICTOIRE))


def enregistrer_defaite(joueur, jeu, adversaire):
    """Retire les points d'une défaite (sans passer sous le plancher), compte la défaite et la partie."""
    joueur["elo"] = max(ELO_MINIMUM, joueur["elo"] - POINTS_PAR_MATCH)
    joueur["defaites"] += 1
    enregistrer_partie(joueur, entree_historique(jeu, adversaire, HISTORIQUE_DEFAITE))


def enregistrer_nul(joueur, jeu, adversaire):
    """Compte la partie sans changer l'ELO."""
    enregistrer_partie(joueur, entree_historique(jeu, adversaire, HISTORIQUE_NUL))


def appliquer_resultat(match, jeu):
    """Met à jour en place elo, compteurs et historique des deux joueurs du match.

    `match` contient "joueur1", "joueur2" et "resultat" (constante de resultats.py).
    Lève ValueError si le résultat n'est pas reconnu.
    """
    joueur1, joueur2, resultat = match["joueur1"], match["joueur2"], match["resultat"]

    if resultat == PREMIER_GAGNE:
        enregistrer_victoire(joueur1, jeu, joueur2)
        enregistrer_defaite(joueur2, jeu, joueur1)
    elif resultat == SECOND_GAGNE:
        enregistrer_defaite(joueur1, jeu, joueur2)
        enregistrer_victoire(joueur2, jeu, joueur1)
    elif resultat == EGALITE:
        enregistrer_nul(joueur1, jeu, joueur2)
        enregistrer_nul(joueur2, jeu, joueur1)
    else:
        raise ValueError(f"Résultat de match inconnu : {resultat!r}")


def texte_ratio(joueur):
    """Renvoie le pourcentage de victoires (ex. "50 %"), ou "N/A" sans partie jouée."""
    if joueur["joues"] == 0:
        return RATIO_SANS_PARTIE
    # Arrondi à l'entier le plus proche, les .5 vers le haut (12,5 % donne 13 %).
    pourcentage = (2 * POURCENT * joueur["victoires"] + joueur["joues"]) // (2 * joueur["joues"])
    return f"{pourcentage} %"
