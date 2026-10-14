import unittest

from elo import appliquer_resultat, texte_ratio
from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE


def nouveau_joueur(nom, elo=1000):
    return {
        "nom": nom, "type": "humain", "elo": elo,
        "joues": 0, "victoires": 0, "defaites": 0, "historique": [],
    }


def jouer(resultat, elo_alice=1000, elo_bob=1000):
    """Applique un résultat entre Alice et Bob ; renvoie (alice, bob)."""
    alice = nouveau_joueur("Alice", elo_alice)
    bob = nouveau_joueur("Bob", elo_bob)
    appliquer_resultat({"joueur1": alice, "joueur2": bob, "resultat": resultat}, "ppc")
    return alice, bob


class TestAppliquerResultat(unittest.TestCase):

    def test_victoire_du_premier(self):
        alice, bob = jouer(PREMIER_GAGNE)

        self.assertEqual((alice["elo"], alice["victoires"], alice["defaites"]), (1050, 1, 0))
        self.assertEqual((bob["elo"], bob["victoires"], bob["defaites"]), (950, 0, 1))

    def test_victoire_du_second(self):
        alice, bob = jouer(SECOND_GAGNE)

        self.assertEqual((alice["elo"], alice["victoires"], alice["defaites"]), (950, 0, 1))
        self.assertEqual((bob["elo"], bob["victoires"], bob["defaites"]), (1050, 1, 0))

    def test_egalite_ne_change_pas_l_elo(self):
        alice, bob = jouer(EGALITE)

        self.assertEqual((alice["elo"], alice["victoires"], alice["defaites"]), (1000, 0, 0))
        self.assertEqual((bob["elo"], bob["victoires"], bob["defaites"]), (1000, 0, 0))

    def test_l_elo_ne_descend_pas_sous_zero(self):
        _, bob = jouer(PREMIER_GAGNE, elo_bob=30)

        self.assertEqual(bob["elo"], 0)

    def test_l_elo_egal_aux_points_perdus_tombe_a_zero(self):
        _, bob = jouer(PREMIER_GAGNE, elo_bob=50)

        self.assertEqual(bob["elo"], 0)

    def test_deux_victoires_de_suite_accumulent_elo_et_historique(self):
        alice = nouveau_joueur("Alice")
        bob = nouveau_joueur("Bob")
        match = {"joueur1": alice, "joueur2": bob, "resultat": PREMIER_GAGNE}

        appliquer_resultat(match, "ppc")
        appliquer_resultat(match, "ppc")

        self.assertEqual((alice["elo"], alice["victoires"], alice["joues"]), (1100, 2, 2))
        self.assertEqual(len(alice["historique"]), 2)

    def test_l_elo_a_zero_reste_a_zero(self):
        _, bob = jouer(PREMIER_GAGNE, elo_bob=0)

        self.assertEqual(bob["elo"], 0)

    def test_parties_jouees_comptees_dans_tous_les_cas(self):
        for resultat in (PREMIER_GAGNE, SECOND_GAGNE, EGALITE):
            with self.subTest(resultat=resultat):
                alice, bob = jouer(resultat)

                self.assertEqual((alice["joues"], bob["joues"]), (1, 1))

    def test_entree_d_historique_de_chaque_joueur(self):
        alice, bob = jouer(PREMIER_GAGNE)

        self.assertEqual(
            alice["historique"],
            [{"jeu": "ppc", "adversaire": "Bob", "resultat": "victoire"}],
        )
        self.assertEqual(
            bob["historique"],
            [{"jeu": "ppc", "adversaire": "Alice", "resultat": "defaite"}],
        )

    def test_historique_d_une_egalite(self):
        alice, bob = jouer(EGALITE)

        self.assertEqual(alice["historique"][0]["resultat"], "nul")
        self.assertEqual(bob["historique"][0]["resultat"], "nul")

    def test_resultat_invalide_leve_une_erreur_sans_rien_modifier(self):
        alice = nouveau_joueur("Alice")
        bob = nouveau_joueur("Bob")

        with self.assertRaises(ValueError):
            appliquer_resultat({"joueur1": alice, "joueur2": bob, "resultat": "inconnu"}, "ppc")

        self.assertEqual(alice, nouveau_joueur("Alice"))
        self.assertEqual(bob, nouveau_joueur("Bob"))

    def test_resultat_none_leve_une_erreur(self):
        alice = nouveau_joueur("Alice")
        bob = nouveau_joueur("Bob")

        with self.assertRaises(ValueError):
            appliquer_resultat({"joueur1": alice, "joueur2": bob, "resultat": None}, "ppc")


class TestTexteRatio(unittest.TestCase):

    def test_sans_partie(self):
        self.assertEqual(texte_ratio(nouveau_joueur("Alice")), "N/A")

    def test_une_partie_gagnee(self):
        joueur = nouveau_joueur("Alice")
        joueur.update(joues=1, victoires=1)

        self.assertEqual(texte_ratio(joueur), "100 %")

    def test_une_victoire_sur_deux_parties(self):
        joueur = nouveau_joueur("Alice")
        joueur.update(joues=2, victoires=1, defaites=1)

        self.assertEqual(texte_ratio(joueur), "50 %")

    def test_les_nuls_comptent_comme_parties_jouees(self):
        joueur = nouveau_joueur("Alice")
        joueur.update(joues=2, victoires=1)

        self.assertEqual(texte_ratio(joueur), "50 %")

    def test_arrondi_au_pourcent(self):
        joueur = nouveau_joueur("Alice")
        joueur.update(joues=3, victoires=1)

        self.assertEqual(texte_ratio(joueur), "33 %")

    def test_arrondi_de_la_demi_vers_le_haut(self):
        joueur = nouveau_joueur("Alice")
        joueur.update(joues=8, victoires=1)

        self.assertEqual(texte_ratio(joueur), "13 %")


if __name__ == "__main__":
    unittest.main()
