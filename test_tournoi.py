import contextlib
import io
import unittest
from unittest.mock import patch

from players import construire_joueur
from tournoi import TournoiAnnule, creer_tournoi


def creer_avec_saisies(joueurs, saisies):
    """Appelle creer_tournoi avec des saisies simulées ; renvoie (tournoi, texte affiché)."""
    sortie = io.StringIO()
    with patch("builtins.input", side_effect=saisies), contextlib.redirect_stdout(sortie):
        tournoi = creer_tournoi(joueurs)
    return tournoi, sortie.getvalue()


class TestSelectionDesParticipants(unittest.TestCase):
    def test_deux_joueurs_identiques_sont_tous_les_deux_selectionnes(self):
        alex_1, alex_2 = construire_joueur("Alex"), construire_joueur("Alex")

        tournoi, _ = creer_avec_saisies(
            [alex_1, alex_2], ["Coupe", "ppc", "round-robin", "2", "1", "2"]
        )

        self.assertIs(tournoi["participants"][0], alex_1)
        self.assertIs(tournoi["participants"][1], alex_2)

    def test_numero_refuse_puis_accepte_ne_consomme_pas_de_tentative(self):
        alice, bob = construire_joueur("Alice"), construire_joueur("Bob")

        tournoi, sortie = creer_avec_saisies(
            [alice, bob], ["Coupe", "ppc", "round-robin", "2", "1", "1", "9", "x", "2"]
        )

        self.assertEqual(tournoi["participants"], [alice, bob])
        self.assertEqual(sortie.count("Choix invalide, joueur déjà choisi ou numéro incorrect"), 2)
        self.assertEqual(sortie.count("Numéro invalide"), 1)

    def test_aucun_joueur_annule_le_tournoi(self):
        with self.assertRaises(TournoiAnnule):
            creer_avec_saisies([], [])


if __name__ == "__main__":
    unittest.main()
