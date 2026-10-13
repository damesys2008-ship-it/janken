import unittest

from regles_ppc import EGALITE, PREMIER_GAGNE, SECOND_GAGNE, determiner_gagnant


class TestDeterminerGagnant(unittest.TestCase):
    def verifier_resultat(self, choix_premier, choix_second, resultat_attendu):
        resultat = determiner_gagnant(choix_premier, choix_second)

        self.assertEqual(resultat, resultat_attendu)

    def test_pierre_bat_ciseaux(self):
        self.verifier_resultat("pierre", "ciseaux", PREMIER_GAGNE)

    def test_ciseaux_bat_feuille(self):
        self.verifier_resultat("ciseaux", "feuille", PREMIER_GAGNE)

    def test_feuille_bat_pierre(self):
        self.verifier_resultat("feuille", "pierre", PREMIER_GAGNE)

    def test_second_gagne_avec_ciseaux_contre_pierre(self):
        self.verifier_resultat("ciseaux", "pierre", SECOND_GAGNE)

    def test_second_gagne_avec_feuille_contre_ciseaux(self):
        self.verifier_resultat("feuille", "ciseaux", SECOND_GAGNE)

    def test_second_gagne_avec_pierre_contre_feuille(self):
        self.verifier_resultat("pierre", "feuille", SECOND_GAGNE)

    def test_egalite_avec_pierre(self):
        self.verifier_resultat("pierre", "pierre", EGALITE)

    def test_egalite_avec_feuille(self):
        self.verifier_resultat("feuille", "feuille", EGALITE)

    def test_egalite_avec_ciseaux(self):
        self.verifier_resultat("ciseaux", "ciseaux", EGALITE)

    def test_choix_invalide_en_premiere_position(self):
        with self.assertRaises(ValueError) as contexte:
            determiner_gagnant("puits", "pierre")

        self.assertIn("puits", str(contexte.exception))

    def test_choix_invalide_en_seconde_position(self):
        with self.assertRaises(ValueError) as contexte:
            determiner_gagnant("pierre", "puits")

        self.assertIn("puits", str(contexte.exception))


if __name__ == "__main__":
    unittest.main()
