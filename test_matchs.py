"""Tests des parties PFC et Morpion : la valeur renvoyée par chaque partie."""
import contextlib
import io
import unittest
from unittest import mock

from match_morpion import jouer_partie_morpion
from match_ppc import jouer_partie_ppc
from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE

ALICE = {"nom": "Alice"}
BOB = {"nom": "Bob"}


def jouer_avec(partie, reponses_input=(), reponses_getpass=()):
    """Lance partie(ALICE, BOB) avec des saisies scriptées ; renvoie (résultat, texte affiché)."""
    sortie = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(reponses_input)), \
            mock.patch("getpass.getpass", side_effect=list(reponses_getpass)), \
            contextlib.redirect_stdout(sortie):
        resultat = partie(ALICE, BOB)
    return resultat, sortie.getvalue()


class TestPartiePpc(unittest.TestCase):

    def test_le_premier_gagne(self):
        resultat, sortie = jouer_avec(jouer_partie_ppc, reponses_getpass=["p", "c"])

        self.assertEqual(resultat, PREMIER_GAGNE)
        self.assertIn("Le gagnant est : Alice", sortie)

    def test_le_second_gagne(self):
        resultat, sortie = jouer_avec(jouer_partie_ppc, reponses_getpass=["p", "f"])

        self.assertEqual(resultat, SECOND_GAGNE)
        self.assertIn("Le gagnant est : Bob", sortie)

    def test_egalite(self):
        resultat, sortie = jouer_avec(jouer_partie_ppc, reponses_getpass=["f", "f"])

        self.assertEqual(resultat, EGALITE)
        self.assertIn("Égalité !", sortie)


class TestPartieMorpion(unittest.TestCase):

    def test_x_gagne(self):
        resultat, sortie = jouer_avec(jouer_partie_morpion, ["1", "4", "2", "5", "3"])

        self.assertEqual(resultat, PREMIER_GAGNE)
        self.assertIn("Le gagnant est : Alice", sortie)

    def test_o_gagne(self):
        resultat, sortie = jouer_avec(jouer_partie_morpion, ["1", "4", "2", "5", "9", "6"])

        self.assertEqual(resultat, SECOND_GAGNE)
        self.assertIn("Le gagnant est : Bob", sortie)

    def test_partie_nulle(self):
        coups = ["1", "2", "3", "5", "4", "6", "8", "7", "9"]

        resultat, sortie = jouer_avec(jouer_partie_morpion, coups)

        self.assertEqual(resultat, EGALITE)
        self.assertIn("Égalité !", sortie)


if __name__ == "__main__":
    unittest.main()
