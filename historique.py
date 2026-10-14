"""Textes de l'historique des tournois : fonctions pures, l'appelant fait le print."""

from moteur_tournoi import derniers_matchs_du_tour
from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE
from tournoi import FORMAT_ELIMINATION, PREMIER_TOUR

AUCUN_TOURNOI = "Aucun tournoi terminé."
AUCUN_CHAMPION = "aucun"
# Les messages de l'arbre sont sans accent : ils s'affichent dans la console Windows.
PAS_ELIMINATION = "L'arbre n'est disponible que pour le format elimination directe."
AUCUN_MATCH = "Aucun match joue."

# Phrases pour un nul et pour un match pas encore joué : (nul, non joué).
PHRASES_DETAIL = ("égalité entre {premier} et {second}", "non joué")
PHRASES_ARBRE = ("{premier} contre {second} (egalite)", "{premier} contre {second} (non joue)")


def tournois_termines(tournois):
    """Renvoie seulement les tournois dont `termine` est vrai."""
    return [tournoi for tournoi in tournois if tournoi["termine"]]


def texte_liste_historique(tournois):
    """Une ligne numérotée par tournoi terminé, ou un message s'il n'y en a aucun."""
    termines = tournois_termines(tournois)
    if not termines:
        return AUCUN_TOURNOI

    lignes = []
    for position, tournoi in enumerate(termines, start=1):
        lignes.append(
            f"{position}. {tournoi['nom']} ({tournoi['jeu']} - {tournoi['format']})"
            f" - champion : {_nom_champion(tournoi)}"
        )
    return "\n".join(lignes)


def texte_detail_tournoi(tournoi):
    """Nom, jeu, format, participants, matchs par tour et champion."""
    noms_participants = ", ".join(joueur["nom"] for joueur in tournoi["participants"])
    lignes = [
        f"Tournoi : {tournoi['nom']}",
        f"Jeu : {tournoi['jeu']}",
        f"Format : {tournoi['format']}",
        f"Participants : {noms_participants}",
        "Matchs :",
    ]
    lignes += _lignes_matchs_par_tour(tournoi["matchs"])
    lignes.append(f"Champion : {_nom_champion(tournoi)}")
    return "\n".join(lignes)


def texte_arbre_elimination(tournoi):
    """Arbre ASCII de la finale vers le premier tour.

    Un tournoi non terminé peut avoir plusieurs matchs dans son dernier tour :
    on dessine alors un arbre par match, séparés par une ligne vide.
    """
    if tournoi["format"].lower() != FORMAT_ELIMINATION:
        return PAS_ELIMINATION
    matchs = tournoi["matchs"]
    if not matchs:
        return AUCUN_MATCH

    dernier_tour = max(match["tour"] for match in matchs)
    arbres = [
        "\n".join(_lignes_arbre_match(match, matchs))
        for match in derniers_matchs_du_tour(matchs, dernier_tour)
    ]
    return "\n\n".join(arbres)


def _nom_champion(tournoi):
    champion = tournoi.get("champion")
    if champion is None:
        return AUCUN_CHAMPION
    return champion["nom"]


def _texte_resultat(match, phrase_egalite, phrase_non_joue):
    """« A bat B » ; pour un nul ou un match pas joué, la phrase donnée."""
    premier = match["joueur1"]["nom"]
    second = match["joueur2"]["nom"]
    if match["resultat"] == PREMIER_GAGNE:
        return f"{premier} bat {second}"
    if match["resultat"] == SECOND_GAGNE:
        return f"{second} bat {premier}"
    phrase = phrase_egalite if match["resultat"] == EGALITE else phrase_non_joue
    return phrase.format(premier=premier, second=second)


def _lignes_matchs_par_tour(matchs):
    if not matchs:
        return ["  Aucun match."]

    lignes = []
    for tour in sorted({match["tour"] for match in matchs}):
        lignes.append(f"  Tour {tour} :")
        for match in matchs:
            if match["tour"] == tour:
                lignes.append(f"    - {_texte_resultat(match, *PHRASES_DETAIL)}")
    return lignes


def _lignes_arbre_match(match, matchs):
    """Première ligne : le match ; ensuite, l'arbre de chacun de ses deux joueurs."""
    tour = match["tour"]
    lignes = [f"Tour {tour} : {_texte_resultat(match, *PHRASES_ARBRE)}"]
    branches = [
        _lignes_arbre_joueur(match[cle_joueur], tour, matchs)
        for cle_joueur in ("joueur1", "joueur2")
    ]
    for numero, branche in enumerate(branches):
        est_derniere = numero == len(branches) - 1
        lignes.append(("`-- " if est_derniere else "|-- ") + branche[0])
        decalage = "    " if est_derniere else "|   "
        lignes += [decalage + ligne for ligne in branche[1:]]
    return lignes


def _lignes_arbre_joueur(joueur, tour, matchs):
    """Arbre du dernier match du joueur avant `tour`, ou le joueur seul s'il n'en a pas."""
    match_precedent = _dernier_match_avant(joueur, tour, matchs)
    if match_precedent is not None:
        return _lignes_arbre_match(match_precedent, matchs)
    if tour == PREMIER_TOUR:
        return [joueur["nom"]]
    return [f"{joueur['nom']} (qualifie d'office)"]


def _dernier_match_avant(joueur, tour, matchs):
    """Dernier match du joueur dans un tour antérieur (les matchs sont dans l'ordre joué).

    Les joueurs se comparent par identité (is) et non par nom : deux joueurs
    peuvent porter le même nom.
    """
    for match in reversed(matchs):
        joue_ce_match = joueur is match["joueur1"] or joueur is match["joueur2"]
        if match["tour"] < tour and joue_ce_match:
            return match
    return None
