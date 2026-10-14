import json
import os
import tempfile
import unittest

from stockage import DonneesIllisibles, charger_session, sauvegarder_session


def creer_joueur(nom):
    return {
        "nom": nom,
        "type": "humain",
        "elo": 1000,
        "joues": 0,
        "victoires": 0,
        "defaites": 0,
        "historique": [],
    }


def creer_tournoi(participants, matchs=None, champion=None):
    return {
        "nom": "Coupe",
        "jeu": "PPC",
        "format": "Round-Robin",
        "participants": participants,
        "matchs": matchs if matchs is not None else [],
        "termine": champion is not None,
        "champion": champion,
    }


class TestStockage(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.addCleanup(self.dossier.cleanup)
        self.chemin = os.path.join(self.dossier.name, "session.json")

    def ecrire_brut(self, contenu):
        with open(self.chemin, "w", encoding="utf-8") as fichier:
            fichier.write(contenu)

    def ecrire_session(self, session):
        self.ecrire_brut(json.dumps(session))

    def session_valide(self):
        return {"joueurs": [creer_joueur("Alice"), creer_joueur("Bob")], "tournois": []}

    def tournoi_valide(self):
        return {
            "nom": "Coupe", "jeu": "PPC", "format": "Round-Robin",
            "participants": [0, 1], "matchs": [], "termine": False, "champion": None,
        }

    def test_aller_retour_conserve_les_donnees_et_l_identite_des_objets(self):
        alice, bob = creer_joueur("Alice"), creer_joueur("Bob")
        match = {"joueur1": alice, "joueur2": bob, "resultat": "premier_gagne", "tour": 1}
        tournoi = creer_tournoi([alice, bob], [match], champion=alice)

        sauvegarder_session(self.chemin, [alice, bob], [tournoi])
        joueurs, tournois = charger_session(self.chemin)

        self.assertEqual(joueurs, [alice, bob])
        tournoi_recharge = tournois[0]
        self.assertIs(tournoi_recharge["participants"][0], joueurs[0])
        self.assertIs(tournoi_recharge["participants"][1], joueurs[1])
        self.assertIs(tournoi_recharge["matchs"][0]["joueur1"], joueurs[0])
        self.assertIs(tournoi_recharge["matchs"][0]["joueur2"], joueurs[1])
        self.assertIs(tournoi_recharge["champion"], joueurs[0])
        self.assertEqual(tournoi_recharge["matchs"][0]["resultat"], "premier_gagne")
        self.assertEqual(tournoi_recharge["matchs"][0]["tour"], 1)

    def test_fichier_absent_donne_des_listes_vides(self):
        self.assertEqual(charger_session(self.chemin), ([], []))

    def test_tournoi_sans_champion_et_match_non_joue(self):
        alice, bob = creer_joueur("Alice"), creer_joueur("Bob")
        match = {"joueur1": alice, "joueur2": bob, "resultat": None, "tour": 1}
        tournoi = creer_tournoi([alice, bob], [match])

        sauvegarder_session(self.chemin, [alice, bob], [tournoi])
        _, tournois = charger_session(self.chemin)

        self.assertIsNone(tournois[0]["champion"])
        self.assertIsNone(tournois[0]["matchs"][0]["resultat"])
        self.assertFalse(tournois[0]["termine"])

    def test_deux_joueurs_egaux_restent_distincts(self):
        premier, second = creer_joueur("Alex"), creer_joueur("Alex")
        tournoi = creer_tournoi([second], champion=second)

        sauvegarder_session(self.chemin, [premier, second], [tournoi])
        joueurs, tournois = charger_session(self.chemin)

        self.assertIs(tournois[0]["participants"][0], joueurs[1])
        self.assertIs(tournois[0]["champion"], joueurs[1])

    def test_accents_conserves_dans_le_fichier(self):
        joueur = creer_joueur("Éléonore")

        sauvegarder_session(self.chemin, [joueur], [])

        with open(self.chemin, encoding="utf-8") as fichier:
            self.assertIn("Éléonore", fichier.read())
        self.assertEqual(charger_session(self.chemin)[0][0]["nom"], "Éléonore")

    def test_cle_supplementaire_json_simple_conservee(self):
        alice = creer_joueur("Alice")
        tournoi = creer_tournoi([alice])
        tournoi["tour_actuel"] = 2
        tournoi["notes"] = {"organisateur": "Dan", "tags": ["été", None, 1.5, True]}

        sauvegarder_session(self.chemin, [alice], [tournoi])
        _, tournois = charger_session(self.chemin)

        self.assertEqual(tournois[0]["tour_actuel"], 2)
        self.assertEqual(tournois[0]["notes"], tournoi["notes"])

    def test_cle_supplementaire_non_json_leve_valueerror(self):
        alice = creer_joueur("Alice")
        tournoi = creer_tournoi([alice])
        tournoi["ensemble"] = {1, 2}

        with self.assertRaises(ValueError) as contexte:
            sauvegarder_session(self.chemin, [alice], [tournoi])

        self.assertIn("ensemble", str(contexte.exception))
        self.assertFalse(os.path.exists(self.chemin))

    def test_joueur_absent_de_la_liste_leve_valueerror(self):
        alice, inconnu = creer_joueur("Alice"), creer_joueur("Inconnu")
        tournoi = creer_tournoi([alice, inconnu])

        with self.assertRaises(ValueError):
            sauvegarder_session(self.chemin, [alice], [tournoi])

    def test_champion_absent_de_la_liste_leve_valueerror(self):
        alice, inconnu = creer_joueur("Alice"), creer_joueur("Inconnu")
        tournoi = creer_tournoi([alice], champion=inconnu)

        with self.assertRaises(ValueError):
            sauvegarder_session(self.chemin, [alice], [tournoi])

    def test_aucun_fichier_temporaire_laisse(self):
        alice = creer_joueur("Alice")
        sauvegarder_session(self.chemin, [alice], [])
        tournoi_invalide = creer_tournoi([creer_joueur("Inconnu")])

        with self.assertRaises(ValueError):
            sauvegarder_session(self.chemin, [alice], [tournoi_invalide])

        self.assertEqual(os.listdir(self.dossier.name), ["session.json"])

    def test_echec_ne_detruit_pas_la_sauvegarde_precedente(self):
        alice = creer_joueur("Alice")
        sauvegarder_session(self.chemin, [alice], [])
        tournoi = creer_tournoi([alice])
        tournoi["ensemble"] = {1}

        with self.assertRaises(ValueError):
            sauvegarder_session(self.chemin, [alice], [tournoi])

        self.assertEqual(charger_session(self.chemin)[0], [alice])

    def test_json_corrompu_leve_donnees_illisibles(self):
        self.ecrire_brut('{"joueurs": [')

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_racine_pas_un_objet_leve_donnees_illisibles(self):
        self.ecrire_brut("[]")

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_cle_racine_manquante(self):
        self.ecrire_session({"joueurs": []})

        with self.assertRaises(DonneesIllisibles) as contexte:
            charger_session(self.chemin)

        self.assertIn("tournois", str(contexte.exception))

    def test_joueur_sans_une_de_ses_cles(self):
        session = self.session_valide()
        del session["joueurs"][1]["elo"]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles) as contexte:
            charger_session(self.chemin)

        self.assertIn("elo", str(contexte.exception))

    def test_champs_de_joueur_de_mauvais_type(self):
        modifications = {
            "elo": "abc",
            "joues": None,
            "nom": 12,
            "historique": None,
            "victoires": True,
        }
        for cle, valeur in modifications.items():
            with self.subTest(cle=cle):
                session = self.session_valide()
                session["joueurs"][0][cle] = valeur
                self.ecrire_session(session)

                with self.assertRaises(DonneesIllisibles) as contexte:
                    charger_session(self.chemin)

                self.assertIn(cle, str(contexte.exception))

    def test_resultat_de_match_de_mauvais_type(self):
        session = self.session_valide()
        tournoi = self.tournoi_valide()
        tournoi["matchs"] = [{"joueur1": 0, "joueur2": 1, "resultat": 3, "tour": 1}]
        session["tournois"] = [tournoi]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles) as contexte:
            charger_session(self.chemin)

        self.assertIn("resultat", str(contexte.exception))

    def test_joueur_incomplet_refuse_a_la_sauvegarde(self):
        incomplet = creer_joueur("Alice")
        del incomplet["elo"]

        with self.assertRaises(ValueError):
            sauvegarder_session(self.chemin, [incomplet], [])

        self.assertFalse(os.path.exists(self.chemin))

    def test_joueur_non_json_refuse_a_la_sauvegarde(self):
        joueur = creer_joueur("Alice")
        joueur["surnoms"] = {"Al"}

        with self.assertRaises(ValueError):
            sauvegarder_session(self.chemin, [joueur], [])

    def test_mauvais_type_de_joueurs(self):
        self.ecrire_session({"joueurs": {}, "tournois": []})

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_tournoi_sans_une_de_ses_cles(self):
        session = self.session_valide()
        tournoi = self.tournoi_valide()
        del tournoi["participants"]
        session["tournois"] = [tournoi]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles) as contexte:
            charger_session(self.chemin)

        self.assertIn("participants", str(contexte.exception))

    def test_indice_de_participant_hors_limites(self):
        session = self.session_valide()
        tournoi = self.tournoi_valide()
        tournoi["participants"] = [0, 2]
        session["tournois"] = [tournoi]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_indice_negatif_refuse(self):
        session = self.session_valide()
        tournoi = self.tournoi_valide()
        tournoi["participants"] = [-1]
        session["tournois"] = [tournoi]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_indice_de_match_hors_limites(self):
        session = self.session_valide()
        tournoi = self.tournoi_valide()
        tournoi["matchs"] = [{"joueur1": 0, "joueur2": 5, "resultat": None, "tour": 1}]
        session["tournois"] = [tournoi]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_indice_de_champion_hors_limites(self):
        session = self.session_valide()
        tournoi = self.tournoi_valide()
        tournoi["champion"] = 9
        session["tournois"] = [tournoi]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_indice_booleen_refuse(self):
        session = self.session_valide()
        tournoi = self.tournoi_valide()
        tournoi["participants"] = [True]
        session["tournois"] = [tournoi]
        self.ecrire_session(session)

        with self.assertRaises(DonneesIllisibles):
            charger_session(self.chemin)

    def test_chemin_qui_est_un_dossier_leve_donnees_illisibles(self):
        with self.assertRaises(DonneesIllisibles):
            charger_session(self.dossier.name)


if __name__ == "__main__":
    unittest.main()
