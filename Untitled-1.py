# ------------------------------
# IMPORTS
# ------------------------------
import random
import getpass
from regles_ppc import PREMIER_GAGNE, determiner_gagnant

# ------------------------------
# PLAYERS
# ------------------------------
joueurs = []

def creer_joueur():
    stop = 1
    while stop != 2:
        print("\n===== Création d'un joueur =====")
        nom = input("Nom du joueur : ").strip()
        joueur = {
            "nom": nom,
            "type": "humain",
            "elo": 1000,
            "joues": 0,
            "victoires": 0,
            "defaites": 0,
            "historique": []
        }
        joueurs.append(joueur)
        print(f"Joueur {nom} créé avec succès !")
        print("Ajouter un autre joueur ? (1: Oui, 2: Non)")
        try:
            stop = int(input())
        except ValueError:
            stop = 2

def afficher_joueurs():
    if not joueurs:
        print("Aucun joueur créé.")
        return
    print("\nListe des joueurs :")
    print(f"{'Nom':<15} {'Victoires':<9} {'Défaites':<8} {'Parties jouées':<14}")
    print("-"*50)
    for j in joueurs:
        print(f"{j['nom']:<15} {j['victoires']:<9} {j['defaites']:<8} {j['joues']:<14}")

# ------------------------------
# TOURNOI
# ------------------------------
def creer_tournoi():
    if not joueurs:
        print("Aucun joueur créé, créez des joueurs avant de lancer un tournoi.")
        return

    print("\n===== Création d'un tournoi =====")
    nom = input("Nom du tournoi : ").strip()

    jeu = input("Choisir le jeu (PPC/Morpion) : ").strip()
    if jeu.lower() not in ["ppc", "morpion"]:
        print("Choix invalide, tournoi annulé.")
        return

    format_tournoi = input("Format du tournoi (Round-Robin/Elimination directe) : ").strip()
    if format_tournoi.lower() not in ["round-robin", "elimination directe"]:
        print("Format invalide, tournoi annulé.")
        return

    participants = random.sample(joueurs, k=min(4, len(joueurs)))  # Exemple : 4 participants max aléatoires

    tournoi = {
        "nom": nom,
        "jeu": jeu,
        "format": format_tournoi,
        "participants": participants,
        "matchs": [],
        "termine": False
    }

    print(f"\nTournoi '{nom}' créé avec {len(participants)} participants !\n")
    return tournoi

# ------------------------------
# MATCH PPC
# ------------------------------
def demander_choix(nom_joueur):
    correspondance = {"p": "pierre", "f": "feuille", "c": "ciseaux"}
    while True:
        choix = getpass.getpass(f"{nom_joueur}, choisis [p] / [f] / [c] : ").lower()
        if choix in correspondance:
            return correspondance[choix]
        print("Choix invalide. Tape p, f ou c.")

def jouer_match_ppc():
    if len(joueurs) < 2:
        print("Il faut au moins 2 joueurs pour jouer.")
        return

    # Choisir deux joueurs aléatoires
    joueur1, joueur2 = random.sample(joueurs, 2)

    # Afficher tableau des joueurs
    print("\n===== Joueurs disponibles =====")
    print(f"{'Nom':<15} {'Victoires':<9} {'Défaites':<8} {'Parties jouées':<14}")
    print("-"*50)
    for j in joueurs:
        print(f"{j['nom']:<15} {j['victoires']:<9} {j['defaites']:<8} {j['joues']:<14}")
    print("-"*50)

    # Choix aléatoire de qui commence
    premier = random.choice([joueur1, joueur2])
    second = joueur2 if premier == joueur1 else joueur1
    print(f"\n{premier['nom']} commence le match !\n")

    # Demande choix des symboles
    c_premier = demander_choix(premier['nom'])
    c_second = demander_choix(second['nom'])

    print(f"{premier['nom']} a choisi {c_premier}")
    print(f"{second['nom']} a choisi {c_second}")

    # Mise à jour des parties jouées
    joueur1["joues"] += 1
    joueur2["joues"] += 1

    # Vérification égalité
    if c_premier == c_second:
        print("\n==============================")
        print("          GREAT GAME")
        print("==============================")
        print("Égalité !")
        print("==============================\n")
        return

    # Détermination du gagnant
    gagne = determiner_gagnant(c_premier, c_second) == PREMIER_GAGNE

    if gagne:
        premier["victoires"] += 1
        second["defaites"] += 1
        gagnant = premier
    else:
        second["victoires"] += 1
        premier["defaites"] += 1
        gagnant = second

    print("\n==============================")
    print("          GREAT GAME")
    print("==============================")
    print(f"Le gagnant est : {gagnant['nom']}")
    print("==============================\n")

# ------------------------------
# MATCH MORPION
# ------------------------------
def jouer_match_morpion():
    if len(joueurs) < 2:
        print("Il faut au moins 2 joueurs.")
        return

    grille = [" "] * 9
    joueur_actuel = "X"
    noms = [joueurs[0]["nom"], joueurs[1]["nom"]]

    def afficher_grille():
        print("\n")
        print(f" {grille[0]} | {grille[1]} | {grille[2]} ")
        print("---|---|---")
        print(f" {grille[3]} | {grille[4]} | {grille[5]} ")
        print("---|---|---")
        print(f" {grille[6]} | {grille[7]} | {grille[8]} ")
        print("\n")

    while True:
        afficher_grille()
        try:
            case = int(input(f"{noms[0 if joueur_actuel=='X' else 1]}, choisis une case (1-9) : ")) - 1
        except ValueError:
            print("Choix invalide.")
            continue

        if case < 0 or case > 8 or grille[case] != " ":
            print("Case invalide ou déjà prise.")
            continue

        grille[case] = joueur_actuel

        lignes = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ]

        victoire = False
        for l in lignes:
            if grille[l[0]] == grille[l[1]] == grille[l[2]] != " ":
                afficher_grille()
                print("\n==============================")
                print("          GREAT GAME")
                print("==============================")
                print(f"Le gagnant est : {noms[0 if joueur_actuel=='X' else 1]}")
                print("==============================\n")
                victoire = True
                break

        if victoire:
            return

        if " " not in grille:
            afficher_grille()
            print("\n==============================")
            print("          GREAT GAME")
            print("==============================")
            print("Égalité !")
            print("==============================\n")
            return

        joueur_actuel = "O" if joueur_actuel=="X" else "X"

# ------------------------------
# STATS ET REGLES
# ------------------------------
def reprendre_tournoi():
    print("Reprendre tournoi (squelette)")

def historique_tournoi():
    print("Historique tournoi (squelette)")

def classement_elo():
    if not joueurs:
        print("Aucun joueur créé.")
        return
    joueurs_tries = sorted(joueurs, key=lambda j: j['elo'], reverse=True)
    print("\n==============================")
    print("        CLASSEMENT ELO")
    print("==============================")
    print(f"{'Nom':<15} {'ELO':<6} {'Victoires':<9} {'Défaites':<8}")
    print("------------------------------")
    for j in joueurs_tries:
        print(f"{j['nom']:<15} {j['elo']:<6} {j['victoires']:<9} {j['defaites']:<8}")
    print("==============================\n")

def stats_joueur():
    afficher_joueurs()

def afficher_regles():
    print("\n==============================")
    print("          RÈGLES DU JEU")
    print("==============================")
    print("Le joueur doit effectuer des parties stratégiques liées au principe du jeu.")
    print("Il se doit de remporter trois manches pour gagner le match.")
    print("Chaque action peut avoir un impact positif ou négatif sur le déroulement de la partie.")
    print("Le match se terminera lorsque les conditions de victoires ou défaites ont été atteintes.")
    print("==============================\n")

# ------------------------------
# MENU PRINCIPAL
# ------------------------------
def afficher_menu():
    print("\n" + "="*40)
    print(" " * 15 + "JARKAN")
    print("="*40)
    print("1. Creer un joueur")
    print("2. Creer un tournoi")
    print("3. Reprendre un tournoi")
    print("4. Historique")
    print("5. Classement ELO")
    print("6. Statistiques joueur")
    print("7. Regles")
    print("8. Jouer PPC")
    print("9. Jouer Morpion")
    print("10. Quitter") 

def main():
    while True:
        afficher_menu()
        choix = input("Votre choix : ")

        if choix == "1":
            creer_joueur()
        elif choix == "2":
            tournoi = creer_tournoi()
            if tournoi:
                print(f"Tournoi '{tournoi['nom']}' créé et prêt pour le tournoi !")
        elif choix == "3":
            reprendre_tournoi()
        elif choix == "4":
            historique_tournoi()
        elif choix == "5":
            classement_elo()
        elif choix == "6":
            stats_joueur()
        elif choix == "7":
            afficher_regles()
        elif choix == "8":
            jouer_match_ppc()
        elif choix == "9":
            jouer_match_morpion()
        elif choix == "10":
            print("Au revoir ")
            break
        else:
            print("Choix invalide, réessaye")

if __name__ == "__main__":
    main()
