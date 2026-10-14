# Tournoi.py

from players import joueurs

def creer_tournoi():
    if not joueurs:
        print("Aucun joueur créé, créez des joueurs avant de lancer un tournoi.")
        return

    print("\n===== Création d'un tournoi =====")
    nom = input("Nom du tournoi : ")

    # Choix du jeu
    jeu = input("Choisir le jeu (PPC/Morpion) : ").strip()
    if jeu.lower() not in ["ppc", "morpion"]:
        print("Choix invalide, tournoi annulé.")
        return

    # Choix du format
    format_tournoi = input("Format du tournoi (Round-Robin/Elimination directe) : ").strip()
    if format_tournoi.lower() not in ["round-robin", "elimination directe"]:
        print("Format invalide, tournoi annulé.")
        return

    # Choix des participants
    print("\nJoueurs disponibles :")
    for i, j in enumerate(joueurs):
        print(f"{i+1}. {j['nom']}")

    participants = []
    try:
        nb = int(input("Nombre de participants : "))
    except ValueError:
        print("Nombre invalide")
        return

    if nb < 2 or nb > len(joueurs):
        print("Nombre de participants invalide")
        return

    for _ in range(nb):
        try:
            i = int(input("Choisir le numéro d'un joueur : ")) - 1
        except ValueError:
            print("Numéro invalide")
            continue

        if i < 0 or i >= len(joueurs) or joueurs[i] in participants:
            print("Choix invalide, joueur déjà choisi ou numéro incorrect")
        else:
            participants.append(joueurs[i])

    # Créer le tournoi
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
