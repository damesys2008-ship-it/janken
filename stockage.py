import json
import os
import tempfile

CLE_JOUEURS = "joueurs"
CLE_TOURNOIS = "tournois"
CLES_JOUEUR = ("nom", "type", "elo", "joues", "victoires", "defaites", "historique")
TYPES_JOUEUR = {
    "nom": str,
    "type": str,
    "elo": int,
    "joues": int,
    "victoires": int,
    "defaites": int,
    "historique": list,
}
CLES_TOURNOI = ("nom", "jeu", "format", "participants", "matchs", "termine", "champion")
CLES_MATCH = ("joueur1", "joueur2", "resultat", "tour")


class DonneesIllisibles(Exception):
    """Levée quand le fichier de session existe mais ne peut pas être relu ; le message dit pourquoi."""


# ------------------------------
# Sauvegarde                   |
# ------------------------------

def sauvegarder_session(chemin, joueurs, tournois):
    """Écrit joueurs et tournois dans un seul fichier JSON, de façon atomique.

    Dans le fichier, un tournoi désigne ses joueurs par leur indice dans `joueurs`.
    Lève ValueError si un joueur est incomplet ou non écrivable en JSON, si un tournoi
    référence un joueur absent de `joueurs` ou porte une clé non écrivable en JSON.
    """
    _verifier_joueurs_a_ecrire(joueurs)
    donnees = {
        CLE_JOUEURS: joueurs,
        CLE_TOURNOIS: [_tournoi_vers_donnees(tournoi, joueurs) for tournoi in tournois],
    }
    _ecrire_json_atomique(chemin, donnees)


def _verifier_joueurs_a_ecrire(joueurs):
    """Refuse d'écrire un joueur que le chargement refuserait ensuite."""
    for position, joueur in enumerate(joueurs, start=1):
        try:
            _lire_joueur(joueur, position)
        except DonneesIllisibles as erreur:
            raise ValueError(str(erreur)) from erreur
        if not _est_json_simple(joueur):
            raise ValueError(f"Joueur n°{position} : une valeur n'est pas écrivable en JSON.")


def _tournoi_vers_donnees(tournoi, joueurs):
    donnees = _cles_supplementaires(tournoi)
    donnees.update({
        "nom": tournoi["nom"],
        "jeu": tournoi["jeu"],
        "format": tournoi["format"],
        "participants": [_indice_du_joueur(joueur, joueurs) for joueur in tournoi["participants"]],
        "matchs": [_match_vers_donnees(match, joueurs) for match in tournoi["matchs"]],
        "termine": tournoi["termine"],
        "champion": _champion_vers_indice(tournoi, joueurs),
    })
    return donnees


def _match_vers_donnees(match, joueurs):
    return {
        "joueur1": _indice_du_joueur(match["joueur1"], joueurs),
        "joueur2": _indice_du_joueur(match["joueur2"], joueurs),
        "resultat": match["resultat"],
        "tour": match["tour"],
    }


def _champion_vers_indice(tournoi, joueurs):
    champion = tournoi.get("champion")
    if champion is None:
        return None
    return _indice_du_joueur(champion, joueurs)


def _indice_du_joueur(joueur, joueurs):
    """Cherche le joueur par identité : deux joueurs peuvent être égaux sans être le même."""
    for indice, candidat in enumerate(joueurs):
        if candidat is joueur:
            return indice
    raise ValueError(f"Le joueur {joueur!r} n'est pas dans la liste des joueurs à sauvegarder.")


def _cles_supplementaires(tournoi):
    """Copie les clés que le module ne connaît pas, si elles s'écrivent en JSON."""
    supplementaires = {}
    for cle, valeur in tournoi.items():
        if cle in CLES_TOURNOI:
            continue
        if not _est_json_simple(valeur):
            raise ValueError(
                f"La clé '{cle}' du tournoi '{tournoi['nom']}' n'est pas écrivable en JSON."
            )
        supplementaires[cle] = valeur
    return supplementaires


def _est_json_simple(valeur):
    if valeur is None or isinstance(valeur, (str, int, float, bool)):
        return True
    if isinstance(valeur, list):
        return all(_est_json_simple(element) for element in valeur)
    if isinstance(valeur, dict):
        return all(
            isinstance(cle, str) and _est_json_simple(element)
            for cle, element in valeur.items()
        )
    return False


def _ecrire_json_atomique(chemin, donnees):
    """Écrit dans un fichier temporaire voisin puis le renomme : jamais de fichier à moitié écrit."""
    dossier = os.path.dirname(os.path.abspath(chemin))
    descripteur, chemin_temporaire = tempfile.mkstemp(dir=dossier, suffix=".tmp")
    try:
        with os.fdopen(descripteur, "w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=2)
        os.replace(chemin_temporaire, chemin)
    except BaseException:
        # BaseException : on nettoie aussi sur Ctrl+C, puis on relance l'erreur telle quelle
        if os.path.exists(chemin_temporaire):
            os.remove(chemin_temporaire)
        raise


# ------------------------------
# Chargement                   |
# ------------------------------

def charger_session(chemin):
    """Renvoie (joueurs, tournois) ; un fichier absent donne deux listes vides.

    Les participants, matchs et champions des tournois sont les mêmes objets
    que les joueurs renvoyés. Lève DonneesIllisibles si le fichier est inutilisable.
    """
    try:
        with open(chemin, encoding="utf-8") as fichier:
            donnees = json.load(fichier)
    except FileNotFoundError:
        return [], []
    except OSError as erreur:
        raise DonneesIllisibles(f"Impossible de lire '{chemin}' : {erreur}") from erreur
    except (json.JSONDecodeError, UnicodeDecodeError) as erreur:
        raise DonneesIllisibles(f"'{chemin}' n'est pas un JSON valide : {erreur}") from erreur
    return _lire_session(donnees)


def _lire_session(donnees):
    _exiger_cles(donnees, (CLE_JOUEURS, CLE_TOURNOIS), "Fichier de session")
    _exiger_type(donnees[CLE_JOUEURS], list, f"Fichier de session : '{CLE_JOUEURS}'")
    _exiger_type(donnees[CLE_TOURNOIS], list, f"Fichier de session : '{CLE_TOURNOIS}'")

    joueurs = [
        _lire_joueur(donnees_joueur, position)
        for position, donnees_joueur in enumerate(donnees[CLE_JOUEURS], start=1)
    ]
    tournois = [
        _lire_tournoi(donnees_tournoi, position, joueurs)
        for position, donnees_tournoi in enumerate(donnees[CLE_TOURNOIS], start=1)
    ]
    return joueurs, tournois


def _lire_joueur(donnees, position):
    contexte = f"Joueur n°{position}"
    _exiger_cles(donnees, CLES_JOUEUR, contexte)
    for cle, type_attendu in TYPES_JOUEUR.items():
        _exiger_type(donnees[cle], type_attendu, f"{contexte} : '{cle}'")
    return dict(donnees)


def _lire_tournoi(donnees, position, joueurs):
    contexte = f"Tournoi n°{position}"
    _exiger_cles(donnees, CLES_TOURNOI, contexte)
    for cle in ("nom", "jeu", "format"):
        _exiger_type(donnees[cle], str, f"{contexte} : '{cle}'")
    _exiger_type(donnees["termine"], bool, f"{contexte} : 'termine'")
    _exiger_type(donnees["participants"], list, f"{contexte} : 'participants'")
    _exiger_type(donnees["matchs"], list, f"{contexte} : 'matchs'")

    tournoi = dict(donnees)
    tournoi["participants"] = [
        _lire_joueur_par_indice(indice, joueurs, f"{contexte}, participant")
        for indice in donnees["participants"]
    ]
    tournoi["matchs"] = [_lire_match(match, joueurs, contexte) for match in donnees["matchs"]]
    tournoi["champion"] = _lire_champion(donnees["champion"], joueurs, contexte)
    return tournoi


def _lire_match(donnees, joueurs, contexte):
    contexte_match = f"{contexte}, match"
    _exiger_cles(donnees, CLES_MATCH, contexte_match)
    _exiger_type(donnees["tour"], int, f"{contexte_match} : 'tour'")
    if donnees["resultat"] is not None:
        _exiger_type(donnees["resultat"], str, f"{contexte_match} : 'resultat'")
    match = dict(donnees)
    match["joueur1"] = _lire_joueur_par_indice(donnees["joueur1"], joueurs, contexte_match)
    match["joueur2"] = _lire_joueur_par_indice(donnees["joueur2"], joueurs, contexte_match)
    return match


def _lire_champion(indice, joueurs, contexte):
    if indice is None:
        return None
    return _lire_joueur_par_indice(indice, joueurs, f"{contexte}, champion")


def _lire_joueur_par_indice(indice, joueurs, contexte):
    est_entier = isinstance(indice, int) and not isinstance(indice, bool)
    if not est_entier or not 0 <= indice < len(joueurs):
        raise DonneesIllisibles(f"{contexte} : indice de joueur invalide ({indice!r}).")
    return joueurs[indice]


def _exiger_cles(donnees, cles, contexte):
    _exiger_type(donnees, dict, contexte)
    for cle in cles:
        if cle not in donnees:
            raise DonneesIllisibles(f"{contexte} : clé manquante '{cle}'.")


def _exiger_type(valeur, type_attendu, contexte):
    # bool est un sous-type de int en Python : on le refuse quand on attend un entier
    mauvais_bool = type_attendu is int and isinstance(valeur, bool)
    if not isinstance(valeur, type_attendu) or mauvais_bool:
        raise DonneesIllisibles(
            f"{contexte} : {type_attendu.__name__} attendu, reçu {type(valeur).__name__}."
        )
