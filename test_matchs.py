"""Tests des parties PFC et Morpion : la valeur renvoyée par chaque partie."""
import contextlib
import io
import unittest
from unittest import mock

from match_morpion import jouer_match_morpion, jouer_partie_morpion
from match_ppc import jouer_match_ppc, jouer_partie_ppc
from players import ELO_INITIAL, construire_joueur
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


def jouer_match(match, joueurs, reponses_input=(), reponses_getpass=()):
    """Lance match(joueurs) avec des saisies scriptées, le tirage au hasard étant fixé."""
    with mock.patch("builtins.input", side_effect=list(reponses_input)), \
            mock.patch("getpass.getpass", side_effect=list(reponses_getpass)), \
            mock.patch("random.sample", side_effect=lambda liste, nombre: liste[:nombre]), \
            contextlib.redirect_stdout(io.StringIO()):
        match(joueurs)


class TestStatistiquesApresMatch(unittest.TestCase):

    def setUp(self):
        self.alice = construire_joueur("Alice")
        self.bob = construire_joueur("Bob")

    def verifier_stats(self, joueur, elo, victoires, defaites):
        self.assertEqual(joueur["elo"], elo)
        self.assertEqual(joueur["victoires"], victoires)
        self.assertEqual(joueur["defaites"], defaites)
        self.assertEqual(joueur["joues"], 1)
        self.assertEqual(len(joueur["historique"]), 1)

    def test_ppc_victoire_met_a_jour_les_deux_joueurs(self):
        jouer_match(jouer_match_ppc, [self.alice, self.bob], reponses_getpass=["p", "c"])

        self.verifier_stats(self.alice, ELO_INITIAL + 50, 1, 0)
        self.verifier_stats(self.bob, ELO_INITIAL - 50, 0, 1)
        self.assertEqual(self.alice["historique"][0]["jeu"], "ppc")

    def test_ppc_egalite_ne_change_pas_l_elo(self):
        jouer_match(jouer_match_ppc, [self.alice, self.bob], reponses_getpass=["f", "f"])

        self.verifier_stats(self.alice, ELO_INITIAL, 0, 0)
        self.verifier_stats(self.bob, ELO_INITIAL, 0, 0)

    def test_ppc_un_seul_joueur_ne_change_rien(self):
        jouer_match(jouer_match_ppc, [self.alice])

        self.assertEqual(self.alice["joues"], 0)

    def test_morpion_victoire_du_premier(self):
        jouer_match(jouer_match_morpion, [self.alice, self.bob], ["1", "4", "2", "5", "3"])

        self.verifier_stats(self.alice, ELO_INITIAL + 50, 1, 0)
        self.verifier_stats(self.bob, ELO_INITIAL - 50, 0, 1)
        self.assertEqual(self.bob["historique"][0]["jeu"], "morpion")

    def test_morpion_partie_nulle(self):
        coups = ["1", "2", "3", "5", "4", "6", "8", "7", "9"]

        jouer_match(jouer_match_morpion, [self.alice, self.bob], coups)

        self.verifier_stats(self.alice, ELO_INITIAL, 0, 0)
        self.verifier_stats(self.bob, ELO_INITIAL, 0, 0)

    def test_morpion_un_seul_joueur_ne_change_rien(self):
        jouer_match(jouer_match_morpion, [self.alice])

        self.assertEqual(self.alice["joues"], 0)


if __name__ == "__main__":
    unittest.main()
