from itertools import combinations

from elo import RESULTATS_VALIDES, appliquer_resultat
from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE
from tournoi import FORMAT_ELIMINATION, FORMAT_ROUND_ROBIN, PARTICIPANTS_MINIMUM, PREMIER_TOUR


def jouer_tournoi(tournoi, jouer_partie, apres_match):
    """Joue les matchs restants du tournoi, jusqu'au champion.

    Attention : `apres_match` est appelé AVANT que `termine` et `champion` soient renseignés,
    donc l'appelant doit sauvegarder une dernière fois quand cette fonction rend la main.

    - `jouer_partie(joueur1, joueur2)` joue une partie et renvoie une constante de resultats.py ;
    - `apres_match(tournoi)` est appelé après chaque match enregistré (par ex. pour sauvegarder).

    L'état se déduit des clés du tournoi : on peut relancer un tournoi interrompu,
    il reprend au premier match dont le résultat est None.
    Lève ValueError s'il y a moins de 2 participants ou si le format est inconnu.
    """
    if len(tournoi["participants"]) < PARTICIPANTS_MINIMUM:
        raise ValueError(
            f"Il faut au moins {PARTICIPANTS_MINIMUM} participants pour jouer un tournoi."
        )
    avancer = _choisir_avancement(tournoi)

    while not tournoi["termine"]:
        match = _prochain_match(tournoi)
        if match is None:
            avancer(tournoi)
            continue
        _jouer_un_match(match, jouer_partie, tournoi["jeu"])
        apres_match(tournoi)


def gagnant_du_match(match):
    """Renvoie le joueur gagnant du match, ou None s'il est nul ou pas encore joué."""
    if match["resultat"] == PREMIER_GAGNE:
        return match["joueur1"]
    if match["resultat"] == SECOND_GAGNE:
        return match["joueur2"]
    return None


# ------------------------------
# Déroulement d'un match       |
# ------------------------------

def _prochain_match(tournoi):
    for match in tournoi["matchs"]:
        if match["resultat"] is None:
            return match
    return None


def _jouer_un_match(match, jouer_partie, jeu):
    joueur1, joueur2 = match["joueur1"], match["joueur2"]
    print(f"{joueur1['nom']} contre {joueur2['nom']}")

    resultat = jouer_partie(joueur1, joueur2)
    if resultat not in RESULTATS_VALIDES:
        raise ValueError(f"Résultat de partie inconnu : {resultat!r}")
    match["resultat"] = resultat
    appliquer_resultat(match, jeu)


def _creer_match(joueur1, joueur2, tour):
    return {"joueur1": joueur1, "joueur2": joueur2, "resultat": None, "tour": tour}


def _terminer(tournoi, champion):
    tournoi["termine"] = True
    tournoi["champion"] = champion
    print(f"Champion : {champion['nom']}")


# ------------------------------
# Round-robin                  |
# ------------------------------

def _avancer_round_robin(tournoi):
    """Crée tous les matchs d'un coup, puis termine quand ils sont tous joués."""
    if not tournoi["matchs"]:
        for joueur1, joueur2 in combinations(tournoi["participants"], 2):
            tournoi["matchs"].append(_creer_match(joueur1, joueur2, PREMIER_TOUR))
        return
    _terminer(tournoi, _champion_round_robin(tournoi))


def _champion_round_robin(tournoi):
    """Le plus de victoires ; à égalité le plus d'ELO ; puis le premier inscrit.

    `max` garde le premier des ex aequo, donc l'ordre d'inscription départage.
    """
    victoires = {id(joueur): 0 for joueur in tournoi["participants"]}
    for match in tournoi["matchs"]:
        gagnant = gagnant_du_match(match)
        if gagnant is not None:
            victoires[id(gagnant)] += 1
    return max(
        tournoi["participants"],
        key=lambda joueur: (victoires[id(joueur)], joueur["elo"]),
    )


# ------------------------------
# Élimination par tours        |
# ------------------------------

def _avancer_elimination(tournoi):
    """Rejoue les nuls du dernier tour, sinon lance le tour suivant ou désigne le champion."""
    if not tournoi["matchs"]:
        _ajouter_tour(tournoi, PREMIER_TOUR, tournoi["participants"])
        return

    tour = tournoi["matchs"][-1]["tour"]
    derniers = derniers_matchs_du_tour(tournoi["matchs"], tour)
    nuls = [match for match in derniers if match["resultat"] == EGALITE]
    if nuls:
        print("Match nul : on rejoue.")
        for match in nuls:
            tournoi["matchs"].append(_creer_match(match["joueur1"], match["joueur2"], tour))
        return

    qualifies = _qualifies(_joueurs_en_lice(tournoi, tour), derniers)
    if len(qualifies) == 1:
        _terminer(tournoi, qualifies[0])
        return
    _ajouter_tour(tournoi, tour + 1, qualifies)


def _ajouter_tour(tournoi, tour, joueurs):
    print(f"Tour {tour}")
    # un nombre impair laisse le dernier sans adversaire : il est qualifié d'office
    for joueur1, joueur2 in zip(joueurs[0::2], joueurs[1::2]):
        tournoi["matchs"].append(_creer_match(joueur1, joueur2, tour))


def derniers_matchs_du_tour(matchs, tour):
    """Le dernier match de chaque paire du tour : un nul rejoué ne compte que par son rejeu."""
    derniers = {}
    for match in matchs:
        if match["tour"] == tour:
            derniers[(id(match["joueur1"]), id(match["joueur2"]))] = match
    return list(derniers.values())


def _joueurs_en_lice(tournoi, tour):
    """Les joueurs qui jouent ce tour, déduits des résultats des tours précédents."""
    en_lice = list(tournoi["participants"])
    for tour_precedent in range(PREMIER_TOUR, tour):
        derniers = derniers_matchs_du_tour(tournoi["matchs"], tour_precedent)
        en_lice = _qualifies(en_lice, derniers)
    return en_lice


def _qualifies(en_lice, derniers_matchs):
    """Les gagnants du tour, plus le dernier joueur s'il n'avait pas d'adversaire."""
    qualifies = [gagnant_du_match(match) for match in derniers_matchs]
    if len(en_lice) % 2 == 1:
        qualifies.append(en_lice[-1])
    return qualifies


AVANCEMENTS = {
    FORMAT_ROUND_ROBIN: _avancer_round_robin,
    FORMAT_ELIMINATION: _avancer_elimination,
}


def _choisir_avancement(tournoi):
    # le tournoi garde le format tel que l'utilisateur l'a saisi : on compare en minuscules
    format_tournoi = tournoi["format"].lower()
    if format_tournoi not in AVANCEMENTS:
        raise ValueError(f"Format de tournoi inconnu : {tournoi['format']!r}")
    return AVANCEMENTS[format_tournoi]
