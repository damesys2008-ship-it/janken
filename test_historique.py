import contextlib
import io
import unittest

from historique import (
    texte_arbre_elimination,
    texte_detail_tournoi,
    texte_liste_historique,
    tournois_termines,
)
from moteur_tournoi import jouer_tournoi
from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE
from tournoi import FORMAT_ELIMINATION, FORMAT_ROUND_ROBIN, JEU_PPC


def creer_joueur(nom):
    return {"nom": nom, "type": "humain", "elo": 1000, "joues": 0,
            "victoires": 0, "defaites": 0, "historique": []}


def creer_match(joueur1, joueur2, resultat, tour=1):
    return {"joueur1": joueur1, "joueur2": joueur2, "resultat": resultat, "tour": tour}


def creer_tournoi(participants, matchs, format_tournoi=FORMAT_ELIMINATION,
                  termine=True, champion=None):
    return {"nom": "Coupe", "jeu": JEU_PPC, "format": format_tournoi,
            "participants": participants, "matchs": matchs,
            "termine": termine, "champion": champion}


class TestListeHistorique(unittest.TestCase):
    def test_liste_vide(self):
        self.assertEqual(texte_liste_historique([]), "Aucun tournoi terminé.")

    def test_un_tournoi_termine(self):
        alice = creer_joueur("Alice")
        tournoi = creer_tournoi([alice], [], champion=alice)

        texte = texte_liste_historique([tournoi])

        self.assertEqual(texte, "1. Coupe (ppc - elimination directe) - champion : Alice")

    def test_tournoi_non_termine_ignore(self):
        alice = creer_joueur("Alice")
        termine = creer_tournoi([alice], [], champion=alice)
        en_cours = creer_tournoi([alice], [], termine=False)

        self.assertEqual(tournois_termines([en_cours, termine]), [termine])
        self.assertEqual(texte_liste_historique([en_cours, termine]).count("\n"), 0)

    def test_seulement_non_termines(self):
        en_cours = creer_tournoi([], [], termine=False)

        self.assertEqual(texte_liste_historique([en_cours]), "Aucun tournoi terminé.")

    def test_tournoi_sans_champion(self):
        tournoi = creer_tournoi([], [])

        self.assertTrue(texte_liste_historique([tournoi]).endswith("champion : aucun"))


class TestDetailTournoi(unittest.TestCase):
    def test_detail_avec_victoire_et_egalite(self):
        alice, bob, carla = creer_joueur("Alice"), creer_joueur("Bob"), creer_joueur("Carla")
        matchs = [
            creer_match(alice, bob, PREMIER_GAGNE, tour=1),
            creer_match(alice, carla, EGALITE, tour=2),
            creer_match(bob, carla, SECOND_GAGNE, tour=2),
        ]
        tournoi = creer_tournoi([alice, bob, carla], matchs, FORMAT_ROUND_ROBIN, champion=alice)

        texte = texte_detail_tournoi(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tournoi : Coupe",
            "Jeu : ppc",
            "Format : round-robin",
            "Participants : Alice, Bob, Carla",
            "Matchs :",
            "  Tour 1 :",
            "    - Alice bat Bob",
            "  Tour 2 :",
            "    - égalité entre Alice et Carla",
            "    - Carla bat Bob",
            "Champion : Alice",
        ]))

    def test_tournoi_non_termine_sans_match_joue(self):
        alice, bob = creer_joueur("Alice"), creer_joueur("Bob")
        tournoi = creer_tournoi([alice, bob], [creer_match(alice, bob, None)], termine=False)

        texte = texte_detail_tournoi(tournoi)

        self.assertIn("    - non joué", texte)
        self.assertTrue(texte.endswith("Champion : aucun"))

    def test_tournoi_sans_match(self):
        texte = texte_detail_tournoi(creer_tournoi([], [], termine=False))

        self.assertIn("  Aucun match.", texte)


class TestArbreElimination(unittest.TestCase):
    def test_arbre_a_quatre_joueurs(self):
        a, b, c, d = (creer_joueur(nom) for nom in "ABCD")
        matchs = [
            creer_match(a, b, PREMIER_GAGNE, tour=1),
            creer_match(c, d, PREMIER_GAGNE, tour=1),
            creer_match(a, c, PREMIER_GAGNE, tour=2),
        ]
        tournoi = creer_tournoi([a, b, c, d], matchs, champion=a)

        texte = texte_arbre_elimination(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tour 2 : A bat C",
            "|-- Tour 1 : A bat B",
            "|   |-- A",
            "|   `-- B",
            "`-- Tour 1 : C bat D",
            "    |-- C",
            "    `-- D",
        ]))

    def test_arbre_en_ascii_pur(self):
        a, b = creer_joueur("A"), creer_joueur("B")
        tournoi = creer_tournoi([a, b], [creer_match(a, b, None)], termine=False)

        texte = texte_arbre_elimination(tournoi)

        self.assertTrue(texte.isascii())
        self.assertIn("A contre B (non joue)", texte)

    def test_joueur_qualifie_d_office(self):
        a, b, c = creer_joueur("A"), creer_joueur("B"), creer_joueur("C")
        matchs = [
            creer_match(a, b, PREMIER_GAGNE, tour=1),
            creer_match(a, c, SECOND_GAGNE, tour=2),
        ]
        tournoi = creer_tournoi([a, b, c], matchs, champion=c)

        texte = texte_arbre_elimination(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tour 2 : C bat A",
            "|-- Tour 1 : A bat B",
            "|   |-- A",
            "|   `-- B",
            "`-- C (qualifie d'office)",
        ]))

    def test_joueurs_homonymes_restent_distincts(self):
        sam_1, sam_2 = creer_joueur("Sam"), creer_joueur("Sam")
        b, c = creer_joueur("B"), creer_joueur("C")
        matchs = [
            creer_match(sam_1, b, PREMIER_GAGNE, tour=1),
            creer_match(sam_2, c, SECOND_GAGNE, tour=1),
            creer_match(sam_1, c, PREMIER_GAGNE, tour=2),
        ]
        tournoi = creer_tournoi([sam_1, sam_2, b, c], matchs, champion=sam_1)

        texte = texte_arbre_elimination(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tour 2 : Sam bat C",
            "|-- Tour 1 : Sam bat B",
            "|   |-- Sam",
            "|   `-- B",
            "`-- Tour 1 : C bat Sam",
            "    |-- Sam",
            "    `-- C",
        ]))

    def test_nul_rejoue_garde_le_rejeu(self):
        a, b = creer_joueur("A"), creer_joueur("B")
        matchs = [
            creer_match(a, b, EGALITE, tour=1),
            creer_match(a, b, PREMIER_GAGNE, tour=1),
        ]
        tournoi = creer_tournoi([a, b], matchs, champion=a)

        texte = texte_arbre_elimination(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tour 1 : A bat B",
            "|-- A",
            "`-- B",
        ]))

    def test_qualifie_d_office_a_un_tour_intermediaire(self):
        a, b, c, d, e, f = (creer_joueur(nom) for nom in "ABCDEF")
        matchs = [
            creer_match(a, b, PREMIER_GAGNE, tour=1),
            creer_match(c, d, PREMIER_GAGNE, tour=1),
            creer_match(e, f, PREMIER_GAGNE, tour=1),
            creer_match(a, c, PREMIER_GAGNE, tour=2),
            creer_match(a, e, PREMIER_GAGNE, tour=3),
        ]
        tournoi = creer_tournoi([a, b, c, d, e, f], matchs, champion=a)

        texte = texte_arbre_elimination(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tour 3 : A bat E",
            "|-- Tour 2 : A bat C",
            "|   |-- Tour 1 : A bat B",
            "|   |   |-- A",
            "|   |   `-- B",
            "|   `-- Tour 1 : C bat D",
            "|       |-- C",
            "|       `-- D",
            "`-- Tour 1 : E bat F",
            "    |-- E",
            "    `-- F",
        ]))

    def test_cinq_joueurs(self):
        a, b, c, d, e = (creer_joueur(nom) for nom in "ABCDE")
        matchs = [
            creer_match(a, b, PREMIER_GAGNE, tour=1),
            creer_match(c, d, PREMIER_GAGNE, tour=1),
            creer_match(a, c, PREMIER_GAGNE, tour=2),
            creer_match(a, e, SECOND_GAGNE, tour=3),
        ]
        tournoi = creer_tournoi([a, b, c, d, e], matchs, champion=e)

        texte = texte_arbre_elimination(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tour 3 : E bat A",
            "|-- Tour 2 : A bat C",
            "|   |-- Tour 1 : A bat B",
            "|   |   |-- A",
            "|   |   `-- B",
            "|   `-- Tour 1 : C bat D",
            "|       |-- C",
            "|       `-- D",
            "`-- E (qualifie d'office)",
        ]))

    def test_tournoi_non_termine_dessine_chaque_match_du_dernier_tour(self):
        a, b, c, d = (creer_joueur(nom) for nom in "ABCD")
        matchs = [creer_match(a, b, None, tour=1), creer_match(c, d, None, tour=1)]
        tournoi = creer_tournoi([a, b, c, d], matchs, termine=False)

        texte = texte_arbre_elimination(tournoi)

        self.assertEqual(texte, "\n".join([
            "Tour 1 : A contre B (non joue)",
            "|-- A",
            "`-- B",
            "",
            "Tour 1 : C contre D (non joue)",
            "|-- C",
            "`-- D",
        ]))

    def test_format_round_robin_renvoie_un_message(self):
        a, b = creer_joueur("A"), creer_joueur("B")
        tournoi = creer_tournoi([a, b], [creer_match(a, b, PREMIER_GAGNE)], FORMAT_ROUND_ROBIN)

        texte = texte_arbre_elimination(tournoi)

        self.assertIn("elimination directe", texte)

    def test_format_saisi_en_majuscules(self):
        a, b = creer_joueur("A"), creer_joueur("B")
        tournoi = creer_tournoi([a, b], [creer_match(a, b, PREMIER_GAGNE)], "Elimination Directe")

        self.assertTrue(texte_arbre_elimination(tournoi).startswith("Tour 1 : A bat B"))

    def test_aucun_match(self):
        tournoi = creer_tournoi([], [], termine=False)

        self.assertEqual(texte_arbre_elimination(tournoi), "Aucun match joue.")


class TestAvecLeVraiMoteur(unittest.TestCase):
    def test_arbre_d_un_tournoi_joue_par_le_moteur(self):
        joueurs = [creer_joueur(nom) for nom in "ABCDEF"]
        tournoi = creer_tournoi(joueurs, [], termine=False)
        # ordre des parties : A-B (nul), C-D, E-F, rejeu A-B, A-C, A-E
        resultats = iter([EGALITE, PREMIER_GAGNE, PREMIER_GAGNE,
                          PREMIER_GAGNE, PREMIER_GAGNE, PREMIER_GAGNE])

        with contextlib.redirect_stdout(io.StringIO()):
            jouer_tournoi(tournoi, lambda joueur1, joueur2: next(resultats), lambda tournoi: None)

        self.assertEqual(texte_arbre_elimination(tournoi), "\n".join([
            "Tour 3 : A bat E",
            "|-- Tour 2 : A bat C",
            "|   |-- Tour 1 : A bat B",
            "|   |   |-- A",
            "|   |   `-- B",
            "|   `-- Tour 1 : C bat D",
            "|       |-- C",
            "|       `-- D",
            "`-- Tour 1 : E bat F",
            "    |-- E",
            "    `-- F",
        ]))


if __name__ == "__main__":
    unittest.main()
