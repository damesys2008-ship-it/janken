import contextlib
import io
import unittest

from moteur_tournoi import gagnant_du_match, jouer_tournoi
from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE


def creer_joueur(nom, elo=1000):
    return {
        "nom": nom,
        "type": "humain",
        "elo": elo,
        "joues": 0,
        "victoires": 0,
        "defaites": 0,
        "historique": [],
    }


def creer_tournoi(joueurs, format_tournoi):
    return {
        "nom": "Coupe",
        "jeu": "PPC",
        "format": format_tournoi,
        "participants": list(joueurs),
        "matchs": [],
        "termine": False,
        "champion": None,
    }


def creer_joueurs(noms):
    return [creer_joueur(nom) for nom in noms]


def premier_gagne(joueur1, joueur2):
    return PREMIER_GAGNE


def toujours_nul(joueur1, joueur2):
    return EGALITE


def resultats_scriptes(resultats):
    """Renvoie une fonction jouer_partie qui donne les résultats dans l'ordre."""
    suite = iter(resultats)

    def jouer_partie(joueur1, joueur2):
        return next(suite)

    return jouer_partie


def ne_rien_faire(tournoi):
    pass


def jouer(tournoi, jouer_partie=premier_gagne, apres_match=ne_rien_faire):
    with contextlib.redirect_stdout(io.StringIO()):
        jouer_tournoi(tournoi, jouer_partie, apres_match)


def noms_du_match(match):
    return match["joueur1"]["nom"], match["joueur2"]["nom"]


class TestRoundRobin(unittest.TestCase):
    def test_chaque_paire_joue_une_fois(self):
        tournoi = creer_tournoi(creer_joueurs("ABCD"), "round-robin")

        jouer(tournoi)

        self.assertEqual(len(tournoi["matchs"]), 6)
        paires = {frozenset(noms_du_match(match)) for match in tournoi["matchs"]}
        self.assertEqual(len(paires), 6)
        self.assertTrue(all(match["resultat"] is not None for match in tournoi["matchs"]))

    def test_deux_joueurs_un_seul_match(self):
        tournoi = creer_tournoi(creer_joueurs("AB"), "round-robin")

        jouer(tournoi)

        self.assertEqual(len(tournoi["matchs"]), 1)

    def test_format_saisi_avec_majuscules(self):
        tournoi = creer_tournoi(creer_joueurs("ABC"), "Round-Robin")

        jouer(tournoi)

        self.assertEqual(len(tournoi["matchs"]), 3)

    def test_champion_est_celui_qui_a_le_plus_de_victoires(self):
        joueurs = creer_joueurs("ABC")
        tournoi = creer_tournoi(joueurs, "round-robin")

        jouer(tournoi)  # le premier de chaque match gagne : A bat B et C, B bat C

        self.assertIs(tournoi["champion"], joueurs[0])
        self.assertTrue(tournoi["termine"])

    def test_nul_reste_un_nul(self):
        tournoi = creer_tournoi(creer_joueurs("ABC"), "round-robin")

        jouer(tournoi, toujours_nul)

        self.assertEqual(len(tournoi["matchs"]), 3)
        self.assertTrue(all(match["resultat"] == EGALITE for match in tournoi["matchs"]))

    def test_egalite_de_victoires_departagee_par_l_elo(self):
        joueurs = [creer_joueur("A", elo=1000), creer_joueur("B", elo=1200)]
        tournoi = creer_tournoi(joueurs, "round-robin")

        jouer(tournoi, toujours_nul)

        self.assertIs(tournoi["champion"], joueurs[1])

    def test_egalite_totale_departagee_par_l_ordre_d_inscription(self):
        joueurs = creer_joueurs("ABC")
        tournoi = creer_tournoi(joueurs, "round-robin")

        jouer(tournoi, toujours_nul)

        self.assertIs(tournoi["champion"], joueurs[0])


class TestElimination(unittest.TestCase):
    def test_quatre_joueurs(self):
        joueurs = creer_joueurs("ABCD")
        tournoi = creer_tournoi(joueurs, "elimination directe")

        jouer(tournoi)

        self.assertEqual([match["tour"] for match in tournoi["matchs"]], [1, 1, 2])
        self.assertEqual(noms_du_match(tournoi["matchs"][2]), ("A", "C"))
        self.assertIs(tournoi["champion"], joueurs[0])
        self.assertTrue(tournoi["termine"])

    def test_trois_joueurs_le_dernier_est_qualifie_d_office(self):
        joueurs = creer_joueurs("ABC")
        tournoi = creer_tournoi(joueurs, "elimination directe")

        jouer(tournoi)

        self.assertEqual([match["tour"] for match in tournoi["matchs"]], [1, 2])
        self.assertEqual(noms_du_match(tournoi["matchs"][1]), ("A", "C"))
        self.assertIs(tournoi["champion"], joueurs[0])

    def test_cinq_joueurs(self):
        joueurs = creer_joueurs("ABCDE")
        tournoi = creer_tournoi(joueurs, "elimination directe")

        jouer(tournoi)

        self.assertEqual([match["tour"] for match in tournoi["matchs"]], [1, 1, 2, 3])
        self.assertEqual(noms_du_match(tournoi["matchs"][2]), ("A", "C"))
        self.assertEqual(noms_du_match(tournoi["matchs"][3]), ("A", "E"))
        self.assertIs(tournoi["champion"], joueurs[0])

    def test_le_dernier_qualifie_d_office_peut_gagner(self):
        joueurs = creer_joueurs("ABC")
        tournoi = creer_tournoi(joueurs, "elimination directe")

        jouer(tournoi, resultats_scriptes([PREMIER_GAGNE, SECOND_GAGNE]))

        self.assertIs(tournoi["champion"], joueurs[2])

    def test_deux_joueurs_une_finale(self):
        tournoi = creer_tournoi(creer_joueurs("AB"), "elimination directe")

        jouer(tournoi)

        self.assertEqual(len(tournoi["matchs"]), 1)

    def test_nul_rejoue_seul_sans_perdre_les_autres_resultats(self):
        joueurs = creer_joueurs("ABCD")
        tournoi = creer_tournoi(joueurs, "elimination directe")
        # A bat B, C et D font nul, puis D bat C au rejeu, puis D bat A en finale
        scenario = [PREMIER_GAGNE, EGALITE, SECOND_GAGNE, SECOND_GAGNE]

        jouer(tournoi, resultats_scriptes(scenario))

        matchs = tournoi["matchs"]
        self.assertEqual([match["tour"] for match in matchs], [1, 1, 1, 2])
        self.assertEqual(matchs[0]["resultat"], PREMIER_GAGNE)
        self.assertEqual(matchs[1]["resultat"], EGALITE)
        self.assertEqual(noms_du_match(matchs[2]), noms_du_match(matchs[1]))
        self.assertEqual(noms_du_match(matchs[3]), ("A", "D"))
        self.assertIs(tournoi["champion"], joueurs[3])

    def test_plusieurs_nuls_de_suite_sont_rejoues(self):
        joueurs = creer_joueurs("AB")
        tournoi = creer_tournoi(joueurs, "elimination directe")

        jouer(tournoi, resultats_scriptes([EGALITE, EGALITE, SECOND_GAGNE]))

        self.assertEqual(len(tournoi["matchs"]), 3)
        self.assertIs(tournoi["champion"], joueurs[1])


class TestReprise(unittest.TestCase):
    def test_reprise_apres_une_interruption(self):
        joueurs = creer_joueurs("ABCD")
        tournoi = creer_tournoi(joueurs, "round-robin")
        parties_jouees = []

        def jouer_partie(joueur1, joueur2):
            parties_jouees.append((joueur1["nom"], joueur2["nom"]))
            return PREMIER_GAGNE

        appels = []

        def interrompre_au_deuxieme_match(tournoi):
            appels.append(1)
            if len(appels) == 2:
                raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            jouer(tournoi, jouer_partie, interrompre_au_deuxieme_match)
        resultats = [match["resultat"] for match in tournoi["matchs"]]
        self.assertEqual(len([r for r in resultats if r is not None]), 2)

        jouer(tournoi, jouer_partie)

        self.assertEqual(len(parties_jouees), 6)
        self.assertEqual(len(set(parties_jouees)), 6)
        self.assertTrue(tournoi["termine"])
        self.assertEqual(sum(joueur["joues"] for joueur in joueurs), 12)

    def test_reprise_en_elimination(self):
        joueurs = creer_joueurs("ABCD")
        tournoi = creer_tournoi(joueurs, "elimination directe")
        appels = []

        def interrompre_au_deuxieme_match(tournoi):
            appels.append(1)
            if len(appels) == 2:
                raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            jouer(tournoi, premier_gagne, interrompre_au_deuxieme_match)
        self.assertEqual(len(tournoi["matchs"]), 2)

        jouer(tournoi)

        self.assertEqual(len(tournoi["matchs"]), 3)
        self.assertIs(tournoi["champion"], joueurs[0])

    def test_tournoi_termine_ne_rejoue_rien(self):
        tournoi = creer_tournoi(creer_joueurs("AB"), "round-robin")
        jouer(tournoi)
        parties = []

        def jouer_partie(joueur1, joueur2):
            parties.append(1)
            return PREMIER_GAGNE

        jouer(tournoi, jouer_partie)

        self.assertEqual(parties, [])


class TestEffets(unittest.TestCase):
    def test_elo_et_statistiques_mis_a_jour(self):
        alice, bob = creer_joueur("Alice"), creer_joueur("Bob")
        tournoi = creer_tournoi([alice, bob], "round-robin")

        jouer(tournoi)

        self.assertEqual((alice["elo"], bob["elo"]), (1050, 950))
        self.assertEqual((alice["victoires"], bob["defaites"]), (1, 1))
        self.assertEqual((alice["joues"], bob["joues"]), (1, 1))

    def test_apres_match_appele_une_fois_par_match(self):
        tournoi = creer_tournoi(creer_joueurs("ABCD"), "round-robin")
        recus = []

        jouer(tournoi, premier_gagne, recus.append)

        self.assertEqual(len(recus), 6)
        self.assertTrue(all(recu is tournoi for recu in recus))

    def test_aucune_cle_ajoutee_au_tournoi(self):
        tournoi = creer_tournoi(creer_joueurs("ABCD"), "elimination directe")
        cles_avant = set(tournoi)

        jouer(tournoi)

        self.assertEqual(set(tournoi), cles_avant)

    def test_gagnant_du_match(self):
        alice, bob = creer_joueur("Alice"), creer_joueur("Bob")
        match = {"joueur1": alice, "joueur2": bob, "resultat": None, "tour": 1}

        self.assertIsNone(gagnant_du_match(match))
        match["resultat"] = PREMIER_GAGNE
        self.assertIs(gagnant_du_match(match), alice)
        match["resultat"] = SECOND_GAGNE
        self.assertIs(gagnant_du_match(match), bob)
        match["resultat"] = EGALITE
        self.assertIsNone(gagnant_du_match(match))


class TestErreurs(unittest.TestCase):
    def test_moins_de_deux_participants(self):
        for noms in ("", "A"):
            with self.subTest(participants=len(noms)):
                tournoi = creer_tournoi(creer_joueurs(noms), "round-robin")

                with self.assertRaises(ValueError):
                    jouer(tournoi)

    def test_format_inconnu(self):
        tournoi = creer_tournoi(creer_joueurs("AB"), "ligue")

        with self.assertRaises(ValueError):
            jouer(tournoi)

    def test_resultat_de_partie_inconnu_laisse_le_match_a_rejouer(self):
        tournoi = creer_tournoi(creer_joueurs("AB"), "round-robin")

        with self.assertRaises(ValueError):
            jouer(tournoi, resultats_scriptes(["n'importe quoi"]))

        self.assertIsNone(tournoi["matchs"][0]["resultat"])


if __name__ == "__main__":
    unittest.main()
