import os

import match_morpion
import match_ppc
from historique import (
    texte_arbre_elimination,
    texte_detail_tournoi,
    texte_liste_historique,
    tournois_termines,
)
from moteur_tournoi import jouer_tournoi
from players import afficher_joueurs, creer_joueur
from stockage import DonneesIllisibles, charger_session, sauvegarder_session
from tournoi import FORMAT_ELIMINATION, JEU_MORPION, JEU_PPC, TournoiAnnule, creer_tournoi

CHEMIN_DONNEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "donnees.json")
SUFFIXE_FICHIER_ILLISIBLE = ".illisible"

PARTIE_PAR_JEU = {
    JEU_PPC: match_ppc.jouer_partie_ppc,
    JEU_MORPION: match_morpion.jouer_partie_morpion,
}

LARGEUR_MENU = 40
LARGEUR_BANDEAU = 30
DECALAGE_TITRE_MENU = 15


# ------------------------------
# Affichage                    |
# ------------------------------

def afficher_debut_bandeau(titre):
    """Affiche le haut d'un bandeau avec son titre."""
    print("\n" + "=" * LARGEUR_BANDEAU)
    print(titre)
    print("=" * LARGEUR_BANDEAU)


def afficher_fin_bandeau():
    """Affiche le bas d'un bandeau."""
    print("=" * LARGEUR_BANDEAU + "\n")


# ------------------------------
# Session et sauvegarde        |
# ------------------------------
# La session est un dict {"joueurs": [...], "tournois": [...], "chemin": str}
# créé par main() et passé aux actions du menu.

def sauvegarder(session):
    """Écrit la session sur disque ; une erreur d'écriture est affichée, le jeu continue."""
    try:
        sauvegarder_session(session["chemin"], session["joueurs"], session["tournois"])
    except OSError as erreur:
        print(f"Sauvegarde impossible : {erreur}")


def mettre_de_cote_fichier_illisible(chemin):
    """Renomme le fichier fautif (sans écraser un fichier déjà mis de côté)."""
    chemin_cote = chemin + SUFFIXE_FICHIER_ILLISIBLE
    numero = 1
    while os.path.exists(chemin_cote):
        numero += 1
        chemin_cote = f"{chemin}{SUFFIXE_FICHIER_ILLISIBLE}{numero}"
    try:
        os.replace(chemin, chemin_cote)
    except OSError as erreur:
        print(f"Impossible de mettre le fichier de côté : {erreur}")
        return
    print(f"Le fichier a été conservé sous '{chemin_cote}'.")


def charger_ou_demarrer_a_vide(chemin):
    """Renvoie (joueurs, tournois) ; un fichier illisible est mis de côté, on repart à vide."""
    try:
        return charger_session(chemin)
    except DonneesIllisibles as erreur:
        print(f"Données illisibles, démarrage à vide : {erreur}")
        mettre_de_cote_fichier_illisible(chemin)
        return [], []


# ------------------------------
# Actions du menu              |
# ------------------------------

def sur_les_joueurs(action):
    """Adapte une action qui ne connaît que la liste des joueurs à une action de session."""
    return lambda session: action(session["joueurs"])


def lancer_creation_tournoi(session):
    """Crée un tournoi et le range dans la session, ou affiche pourquoi il est annulé."""
    try:
        tournoi = creer_tournoi(session["joueurs"])
    except TournoiAnnule as annulation:
        print(annulation)
        return
    session["tournois"].append(tournoi)
    print(f"Tournoi '{tournoi['nom']}' créé et prêt pour le tournoi !")


def texte_tournoi_en_cours(numero, tournoi):
    """Ligne de la liste des tournois à reprendre, avec les matchs joués sur le total."""
    joues = sum(1 for match in tournoi["matchs"] if match["resultat"] is not None)
    return (
        f"{numero}. {tournoi['nom']} ({tournoi['jeu']} - {tournoi['format']})"
        f" [{joues}/{len(tournoi['matchs'])}]"
    )


def choisir_dans(elements, invite):
    """Demande un numéro (à partir de 1) et renvoie l'élément ; None si la saisie est invalide."""
    try:
        numero = int(input(invite))
    except ValueError:
        return None
    if numero < 1 or numero > len(elements):
        return None
    return elements[numero - 1]


def reprendre_tournoi(session):
    """Liste les tournois non terminés puis rejoue celui que choisit l'utilisateur."""
    en_cours = [tournoi for tournoi in session["tournois"] if not tournoi["termine"]]
    if not en_cours:
        print("Aucun tournoi en cours.")
        return
    for numero, tournoi in enumerate(en_cours, start=1):
        print(texte_tournoi_en_cours(numero, tournoi))

    tournoi = choisir_dans(en_cours, "Numéro du tournoi à reprendre : ")
    if tournoi is None:
        print("Choix invalide.")
        return
    jouer_partie = PARTIE_PAR_JEU.get(tournoi["jeu"].lower())
    if jouer_partie is None:
        print(f"Jeu inconnu : {tournoi['jeu']!r}")
        return
    try:
        jouer_tournoi(tournoi, jouer_partie, lambda _: sauvegarder(session))
    except ValueError as erreur:
        print(erreur)


def afficher_historique(session):
    """Liste les tournois terminés, puis le détail de celui que choisit l'utilisateur."""
    print(texte_liste_historique(session["tournois"]))
    termines = tournois_termines(session["tournois"])
    if not termines:
        return

    tournoi = choisir_dans(termines, "Numéro du tournoi à détailler (vide pour revenir) : ")
    if tournoi is None:
        return
    print(texte_detail_tournoi(tournoi))
    if tournoi["format"].lower() == FORMAT_ELIMINATION:
        print(texte_arbre_elimination(tournoi))


def classement_elo(joueurs):
    """Affiche les joueurs classés par ELO décroissant."""
    if not joueurs:
        print("Aucun joueur créé.")
        return
    joueurs_tries = sorted(joueurs, key=lambda joueur: joueur['elo'], reverse=True)
    afficher_debut_bandeau("        CLASSEMENT ELO")
    print(f"{'Nom':<15} {'ELO':<6} {'Victoires':<9} {'Défaites':<8}")
    print("-" * LARGEUR_BANDEAU)
    for joueur in joueurs_tries:
        print(
            f"{joueur['nom']:<15} {joueur['elo']:<6}"
            f" {joueur['victoires']:<9} {joueur['defaites']:<8}"
        )
    afficher_fin_bandeau()


def afficher_regles(joueurs):
    """Affiche les règles du jeu."""
    afficher_debut_bandeau("          RÈGLES DU JEU")
    print("Le joueur doit effectuer des parties stratégiques liées au principe du jeu.")
    print("Il se doit de remporter trois manches pour gagner le match.")
    print("Chaque action peut avoir un impact positif ou négatif sur le déroulement de la partie.")
    print("Le match se terminera lorsque les conditions de victoires ou défaites ont été atteintes.")
    afficher_fin_bandeau()


# ------------------------------
# Menu principal               |
# ------------------------------

# Chaque option : (libellé affiché, action qui reçoit la session, modifie_la_session).
# Le numéro affiché est la position dans cette liste, en partant de 1 ;
# la session est sauvegardée après les actions qui la modifient.
OPTIONS_MENU = [
    ("Creer un joueur", sur_les_joueurs(creer_joueur), True),
    ("Creer un tournoi", lancer_creation_tournoi, True),
    ("Reprendre un tournoi", reprendre_tournoi, True),
    ("Historique", afficher_historique, False),
    ("Classement ELO", sur_les_joueurs(classement_elo), False),
    ("Statistiques joueur", sur_les_joueurs(afficher_joueurs), False),
    ("Regles", sur_les_joueurs(afficher_regles), False),
    ("Jouer PPC", sur_les_joueurs(match_ppc.jouer_match_ppc), True),
    ("Jouer Morpion", sur_les_joueurs(match_morpion.jouer_match_morpion), True),
]
LIBELLE_QUITTER = "Quitter"
CHOIX_QUITTER = str(len(OPTIONS_MENU) + 1)
OPTIONS_PAR_CHOIX = {
    str(numero): option
    for numero, option in enumerate(OPTIONS_MENU, start=1)
}


def afficher_menu():
    """Affiche le menu principal numéroté."""
    print("\n" + "=" * LARGEUR_MENU)
    print(" " * DECALAGE_TITRE_MENU + "JANKEN")
    print("=" * LARGEUR_MENU)
    for numero, (libelle, _, _) in enumerate(OPTIONS_MENU, start=1):
        print(f"{numero}. {libelle}")
    print(f"{CHOIX_QUITTER}. {LIBELLE_QUITTER}")


def lancer_option(choix, session):
    """Exécute l'option du menu choisie, puis sauvegarde si elle modifie la session."""
    _, action, modifie_la_session = OPTIONS_PAR_CHOIX[choix]
    action(session)
    if modifie_la_session:
        sauvegarder(session)


def main(chemin_donnees=CHEMIN_DONNEES):
    """Boucle du menu principal, jusqu'à ce que l'utilisateur quitte."""
    joueurs, tournois = charger_ou_demarrer_a_vide(chemin_donnees)
    session = {"joueurs": joueurs, "tournois": tournois, "chemin": chemin_donnees}
    while True:
        afficher_menu()
        choix = input("Votre choix : ")

        if choix == CHOIX_QUITTER:
            print("Au revoir ")
            return
        if choix not in OPTIONS_PAR_CHOIX:
            print("Choix invalide, réessaye")
            continue
        lancer_option(choix, session)


if __name__ == "__main__":
    main()
