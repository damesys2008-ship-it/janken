PREMIER_GAGNE = "premier_gagne"
SECOND_GAGNE = "second_gagne"
EGALITE = "egalite"

# Chaque choix est associé au choix qu'il bat
CHOIX_QUE_BAT = {
    "pierre": "ciseaux",
    "ciseaux": "feuille",
    "feuille": "pierre",
}


def verifier_choix(choix):
    """Lève ValueError si le choix n'est pas pierre, feuille ou ciseaux"""
    if choix not in CHOIX_QUE_BAT:
        raise ValueError(f"Choix inconnu : {choix!r} (attendu : {', '.join(CHOIX_QUE_BAT)})")


def determiner_gagnant(choix_premier, choix_second):
    """Renvoie PREMIER_GAGNE, SECOND_GAGNE ou EGALITE pour deux choix"""
    verifier_choix(choix_premier)
    verifier_choix(choix_second)

    if choix_premier == choix_second:
        return EGALITE
    if CHOIX_QUE_BAT[choix_premier] == choix_second:
        return PREMIER_GAGNE
    return SECOND_GAGNE
