import match_morpion
import match_ppc
from players import afficher_joueurs, creer_joueur
from tournoi import TournoiAnnule, creer_tournoi

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
# Actions du menu              |
# ------------------------------

def lancer_creation_tournoi(joueurs):
    """Crée un tournoi, ou affiche pourquoi il est annulé."""
    try:
        tournoi = creer_tournoi(joueurs)
    except TournoiAnnule as annulation:
        print(annulation)
        return
    print(f"Tournoi '{tournoi['nom']}' créé et prêt pour le tournoi !")


def reprendre_tournoi(joueurs):
    """Squelette : reprendre un tournoi n'est pas encore disponible."""
    print("Reprendre tournoi (squelette)")


def historique_tournoi(joueurs):
    """Squelette : l'historique des tournois n'est pas encore disponible."""
    print("Historique tournoi (squelette)")


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

# Chaque option : (libellé affiché, action qui reçoit la liste des joueurs).
# Le numéro affiché est la position dans cette liste, en partant de 1.
OPTIONS_MENU = [
    ("Creer un joueur", creer_joueur),
    ("Creer un tournoi", lancer_creation_tournoi),
    ("Reprendre un tournoi", reprendre_tournoi),
    ("Historique", historique_tournoi),
    ("Classement ELO", classement_elo),
    ("Statistiques joueur", afficher_joueurs),
    ("Regles", afficher_regles),
    ("Jouer PPC", match_ppc.jouer_match_ppc),
    ("Jouer Morpion", match_morpion.jouer_match_morpion),
]
LIBELLE_QUITTER = "Quitter"
CHOIX_QUITTER = str(len(OPTIONS_MENU) + 1)
ACTIONS_PAR_CHOIX = {
    str(numero): action
    for numero, (_, action) in enumerate(OPTIONS_MENU, start=1)
}


def afficher_menu():
    """Affiche le menu principal numéroté."""
    print("\n" + "=" * LARGEUR_MENU)
    print(" " * DECALAGE_TITRE_MENU + "JANKEN")
    print("=" * LARGEUR_MENU)
    for numero, (libelle, _) in enumerate(OPTIONS_MENU, start=1):
        print(f"{numero}. {libelle}")
    print(f"{CHOIX_QUITTER}. {LIBELLE_QUITTER}")


def main():
    """Boucle du menu principal, jusqu'à ce que l'utilisateur quitte."""
    joueurs = []
    while True:
        afficher_menu()
        choix = input("Votre choix : ")

        if choix == CHOIX_QUITTER:
            print("Au revoir ")
            return
        if choix not in ACTIONS_PAR_CHOIX:
            print("Choix invalide, réessaye")
            continue
        ACTIONS_PAR_CHOIX[choix](joueurs)


if __name__ == "__main__":
    main()
