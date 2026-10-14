import contextlib
import io
import unittest
from unittest.mock import patch

from players import ELO_INITIAL, afficher_joueurs, creer_joueur


def creer_avec_saisies(joueurs, saisies):
    """Appelle creer_joueur avec des saisies simulées et renvoie ce qui est affiché."""
    sortie = io.StringIO()
    with patch("builtins.input", side_effect=saisies), contextlib.redirect_stdout(sortie):
        creer_joueur(joueurs)
    return sortie.getvalue()


class TestCreerJoueur(unittest.TestCase):
    def test_cree_un_joueur_avec_ses_valeurs_initiales(self):
        joueurs = []

        creer_avec_saisies(joueurs, ["Alice", "2"])

        self.assertEqual(
            joueurs,
            [{
                "nom": "Alice",
                "type": "humain",
                "elo": ELO_INITIAL,
                "joues": 0,
                "victoires": 0,
                "defaites": 0,
                "historique": [],
            }],
        )

    def test_cree_plusieurs_joueurs(self):
        joueurs = []

        creer_avec_saisies(joueurs, ["Alice", "1", "Bob", "2"])

        self.assertEqual([joueur["nom"] for joueur in joueurs], ["Alice", "Bob"])

    def test_reponse_invalide_puis_valide_ne_plante_pas(self):
        joueurs = []

        sortie = creer_avec_saisies(joueurs, ["Alice", "abc", "7", "2"])

        self.assertEqual(len(joueurs), 1)
        self.assertEqual(sortie.count("Choix invalide, réessaye"), 2)

    def test_ajoute_a_la_liste_recue(self):
        joueurs = [{"nom": "Existant"}]

        creer_avec_saisies(joueurs, ["Alice", "2"])

        self.assertEqual([joueur["nom"] for joueur in joueurs], ["Existant", "Alice"])


class TestAfficherJoueurs(unittest.TestCase):
    def test_liste_vide(self):
        sortie = io.StringIO()

        with contextlib.redirect_stdout(sortie):
            afficher_joueurs([])

        self.assertEqual(sortie.getvalue(), "Aucun joueur créé.\n")

    def test_affiche_les_statistiques(self):
        joueurs = [{"nom": "Alice", "victoires": 3, "defaites": 1, "joues": 4}]
        sortie = io.StringIO()

        with contextlib.redirect_stdout(sortie):
            afficher_joueurs(joueurs)

        self.assertIn(
            "1. Alice | Victoires : 3 | Défaites : 1 | Parties jouées : 4 | Ratio : 75 %",
            sortie.getvalue(),
        )

    def test_ratio_sans_partie_jouee(self):
        joueurs = [{"nom": "Alice", "victoires": 0, "defaites": 0, "joues": 0}]
        sortie = io.StringIO()

        with contextlib.redirect_stdout(sortie):
            afficher_joueurs(joueurs)

        self.assertIn("Parties jouées : 0 | Ratio : N/A", sortie.getvalue())

    def test_ratio_compte_les_nuls_comme_des_parties(self):
        joueurs = [{"nom": "Alice", "victoires": 1, "defaites": 0, "joues": 2}]
        sortie = io.StringIO()

        with contextlib.redirect_stdout(sortie):
            afficher_joueurs(joueurs)

        self.assertIn("Ratio : 50 %", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
