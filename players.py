ELO_INITIAL = 1000
JOUEURS_MINIMUM_PAR_MATCH = 2

TYPE_HUMAIN = "humain"
REPONSE_OUI = 1
REPONSE_NON = 2


def construire_joueur(nom):
    """Renvoie un joueur humain neuf, avec ses statistiques à zéro."""
    return {
        "nom": nom,
        "type": TYPE_HUMAIN,
        "elo": ELO_INITIAL,
        "joues": 0,
        "victoires": 0,
        "defaites": 0,
        "historique": [],
    }


def demander_autre_joueur():
    """Demande s'il faut ajouter un joueur ; répète tant que la réponse est invalide."""
    while True:
        print("Ajouter un autre joueur ?")
        print(f"{REPONSE_OUI}. Oui")
        print(f"{REPONSE_NON}. Non")
        try:
            reponse = int(input())
        except ValueError:
            print("Choix invalide, réessaye")
            continue

        if reponse == REPONSE_OUI:
            return True
        if reponse == REPONSE_NON:
            return False
        print("Choix invalide, réessaye")


def creer_joueur(joueurs):
    """Crée des joueurs humains et les ajoute à la liste, tant que l'utilisateur en veut."""
    veut_ajouter_un_joueur = True
    while veut_ajouter_un_joueur:
        nom = input("Nom du joueur : ")
        joueurs.append(construire_joueur(nom))
        print(f"Joueur {nom} créé avec succès.")
        veut_ajouter_un_joueur = demander_autre_joueur()


def afficher_joueurs(joueurs):
    """Affiche la liste numérotée des joueurs avec leurs statistiques."""
    if not joueurs:
        print("Aucun joueur créé.")
        return
    print("\nListe des joueurs :")
    for numero, joueur in enumerate(joueurs, start=1):
        print(
            f"{numero}. {joueur['nom']} | Victoires : {joueur['victoires']}"
            f" | Défaites : {joueur['defaites']} | Parties jouées : {joueur['joues']}"
        )
