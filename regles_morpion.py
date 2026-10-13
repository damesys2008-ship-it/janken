NOMBRE_DE_CASES = 9
CASE_VIDE = " "

LIGNES_GAGNANTES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def trouver_gagnant(grille):
    """Renvoie "X" ou "O" si une ligne est complète, sinon None"""
    if len(grille) != NOMBRE_DE_CASES:
        raise ValueError(
            f"La grille doit avoir {NOMBRE_DE_CASES} cases, elle en a {len(grille)}."
        )

    for premiere, deuxieme, troisieme in LIGNES_GAGNANTES:
        marque = grille[premiere]
        if marque != CASE_VIDE and marque == grille[deuxieme] == grille[troisieme]:
            return marque

    return None
