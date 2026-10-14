JEUX_VALIDES = ["ppc", "morpion"]
FORMATS_VALIDES = ["round-robin", "elimination directe"]
PARTICIPANTS_MINIMUM = 2


class TournoiAnnule(Exception):
    """Levée quand la création du tournoi est annulée ; le message dit pourquoi."""


def creer_tournoi(joueurs):
    """Demande les infos au clavier et renvoie le tournoi créé."""
    if not joueurs:
        raise TournoiAnnule("Aucun joueur créé, créez des joueurs avant de lancer un tournoi.")

    print("\n===== Création d'un tournoi =====")
    nom = input("Nom du tournoi : ")
    jeu = demander_jeu()
    format_tournoi = demander_format()
    participants = choisir_participants(joueurs)

    print(f"\nTournoi '{nom}' créé avec {len(participants)} participants !\n")
    return {
        "nom": nom,
        "jeu": jeu,
        "format": format_tournoi,
        "participants": participants,
        "matchs": [],
        "termine": False,
    }


def demander_jeu():
    """Demande le jeu du tournoi et renvoie la saisie ; lève TournoiAnnule si inconnu."""
    jeu = input("Choisir le jeu (PPC/Morpion) : ").strip()
    if jeu.lower() not in JEUX_VALIDES:
        raise TournoiAnnule("Choix invalide, tournoi annulé.")
    return jeu


def demander_format():
    """Demande le format du tournoi ; lève TournoiAnnule s'il est inconnu."""
    format_tournoi = input("Format du tournoi (Round-Robin/Elimination directe) : ").strip()
    if format_tournoi.lower() not in FORMATS_VALIDES:
        raise TournoiAnnule("Format invalide, tournoi annulé.")
    return format_tournoi


def choisir_participants(joueurs):
    """Affiche les joueurs puis demande combien de participants et lesquels."""
    print("\nJoueurs disponibles :")
    for position, joueur in enumerate(joueurs, start=1):
        print(f"{position}. {joueur['nom']}")

    nombre = demander_nombre_participants(len(joueurs))

    participants = []
    for _ in range(nombre):
        ajouter_participant(joueurs, participants)
    return participants


def demander_nombre_participants(nombre_joueurs):
    """Demande combien de participants ; lève TournoiAnnule si le nombre est invalide."""
    try:
        nombre = int(input("Nombre de participants : "))
    except ValueError as erreur:
        raise TournoiAnnule("Nombre invalide") from erreur

    if nombre < PARTICIPANTS_MINIMUM or nombre > nombre_joueurs:
        raise TournoiAnnule("Nombre de participants invalide")
    return nombre


def ajouter_participant(joueurs, participants):
    """Demande un numéro de joueur et l'ajoute ; une saisie invalide consomme la tentative."""
    try:
        indice = int(input("Choisir le numéro d'un joueur : ")) - 1
    except ValueError:
        print("Numéro invalide")
        return

    if indice < 0 or indice >= len(joueurs) or joueurs[indice] in participants:
        print("Choix invalide, joueur déjà choisi ou numéro incorrect")
        return
    participants.append(joueurs[indice])
