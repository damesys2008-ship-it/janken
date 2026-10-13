import unittest

from regles_morpion import trouver_gagnant

LIGNES_ATTENDUES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def grille_avec(marque, cases):
    grille = [" "] * 9
    for case in cases:
        grille[case] = marque
    return grille


class TestTrouverGagnant(unittest.TestCase):
    def test_x_gagne_sur_chacune_des_huit_lignes(self):
        for ligne in LIGNES_ATTENDUES:
            with self.subTest(ligne=ligne):
                grille = grille_avec("X", ligne)

                gagnant = trouver_gagnant(grille)

                self.assertEqual(gagnant, "X")

    def test_o_gagne_sur_une_ligne(self):
        grille = grille_avec("O", (2, 4, 6))

        gagnant = trouver_gagnant(grille)

        self.assertEqual(gagnant, "O")

    def test_grille_vide_n_a_pas_de_gagnant(self):
        grille = [" "] * 9

        gagnant = trouver_gagnant(grille)

        self.assertIsNone(gagnant)

    def test_partie_en_cours_n_a_pas_de_gagnant(self):
        grille = ["X", "O", "X",
                  " ", "O", " ",
                  " ", " ", " "]

        gagnant = trouver_gagnant(grille)

        self.assertIsNone(gagnant)

    def test_grille_pleine_sans_ligne_est_une_egalite(self):
        grille = ["X", "O", "X",
                  "X", "O", "O",
                  "O", "X", "X"]

        gagnant = trouver_gagnant(grille)

        self.assertIsNone(gagnant)

    def test_trois_cases_vides_alignees_ne_sont_pas_un_gagnant(self):
        grille = ["X", "O", "X",
                  " ", " ", " ",
                  "O", "X", "O"]

        gagnant = trouver_gagnant(grille)

        self.assertIsNone(gagnant)

    def test_grille_trop_courte_leve_une_erreur(self):
        grille = [" "] * 8

        with self.assertRaises(ValueError) as contexte:
            trouver_gagnant(grille)

        self.assertIn("9", str(contexte.exception))

    def test_grille_trop_longue_leve_une_erreur(self):
        grille = [" "] * 10

        with self.assertRaises(ValueError) as contexte:
            trouver_gagnant(grille)

        self.assertIn("9", str(contexte.exception))


if __name__ == "__main__":
    unittest.main()
