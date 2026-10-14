"""Tests de caractérisation : ils figent le comportement du jeu vu par le joueur.

Tout passe par main.main(). Les réponses du joueur sont fournies par un script ;
le texte complet affiché (invites comprises) est comparé à la sortie attendue.
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

MODULES_DU_JEU = [
    "main", "players", "Tournoi", "tournoi",
    "match_ppc", "match_morpion", "regles_ppc", "regles_morpion",
    "resultats", "elo", "moteur_tournoi", "stockage", "historique",
]

# ------------------------------
# Textes attendus              |
# ------------------------------

MENU = (
    "\n" + "=" * 40 + "\n"
    + " " * 15 + "JANKEN\n"
    + "=" * 40 + "\n"
    "1. Creer un joueur\n"
    "2. Creer un tournoi\n"
    "3. Reprendre un tournoi\n"
    "4. Historique\n"
    "5. Classement ELO\n"
    "6. Statistiques joueur\n"
    "7. Regles\n"
    "8. Jouer PPC\n"
    "9. Jouer Morpion\n"
    "10. Quitter\n"
)
AU_REVOIR = "Au revoir \n"
AUCUN_JOUEUR = "Aucun joueur créé.\n"

REGLES = (
    "\n==============================\n"
    "          RÈGLES DU JEU\n"
    "==============================\n"
    "Le joueur doit effectuer des parties stratégiques liées au principe du jeu.\n"
    "Il se doit de remporter trois manches pour gagner le match.\n"
    "Chaque action peut avoir un impact positif ou négatif sur le déroulement de la partie.\n"
    "Le match se terminera lorsque les conditions de victoires ou défaites ont été atteintes.\n"
    "==============================\n\n"
)

CLASSEMENT_ALICE_BOB = (
    "\n==============================\n"
    "        CLASSEMENT ELO\n"
    "==============================\n"
    "Nom             ELO    Victoires Défaites\n"
    "------------------------------\n"
    "Alice           1000   0         0       \n"
    "Bob             1000   0         0       \n"
    "==============================\n\n"
)

STATISTIQUES_ALICE_BOB = (
    "\nListe des joueurs :\n"
    "1. Alice | Victoires : 0 | Défaites : 0 | Parties jouées : 0 | Ratio : N/A\n"
    "2. Bob | Victoires : 0 | Défaites : 0 | Parties jouées : 0 | Ratio : N/A\n"
)

BANDEAU_FIN_MORPION = (
    "\n==============================\n"
    "          GREAT GAME\n"
    "==============================\n"
)

# Réponses qui créent Alice puis Bob, et ce que le jeu affiche alors.
REPONSES_ALICE_BOB = ["1", "Alice", "1", "Bob", "2"]


def choix_menu(choix):
    """Menu affiché suivi de la réponse du joueur."""
    return MENU + f"Votre choix : {choix}\n"


def sortie_creation(nom, ajouter_un_autre):
    return (
        f"Nom du joueur : {nom}\n"
        f"Joueur {nom} créé avec succès.\n"
        "Ajouter un autre joueur ?\n1. Oui\n2. Non\n"
        f"{ajouter_un_autre}\n"
    )


SORTIE_ALICE_BOB = (
    choix_menu("1") + sortie_creation("Alice", "1") + sortie_creation("Bob", "2")
)


def grille_affichee(cases):
    """Texte de afficher_grille pour 9 caractères (espace = case vide)."""
    c = cases
    return (
        "\n\n"
        f" {c[0]} | {c[1]} | {c[2]} \n"
        "---|---|---\n"
        f" {c[3]} | {c[4]} | {c[5]} \n"
        "---|---|---\n"
        f" {c[6]} | {c[7]} | {c[8]} \n"
        "\n\n"
    )


def tour_morpion(cases, nom, reponse):
    return grille_affichee(cases) + f"{nom}, choisis une case (1-9) : {reponse}\n"


def fin_morpion(cases, resultat):
    return grille_affichee(cases) + BANDEAU_FIN_MORPION + resultat + "\n==============================\n\n"


def tournoi_jusqu_aux_participants(nb):
    """Création du tournoi 'Coupe' (PPC, Round-Robin) avec Alice et Bob, jusqu'au nombre saisi."""
    return (
        choix_menu("2")
        + "\n===== Création d'un tournoi =====\n"
        "Nom du tournoi : Coupe\n"
        "Choisir le jeu (PPC/Morpion) : ppc\n"
        "Format du tournoi (Round-Robin/Elimination directe) : Round-Robin\n"
        "\nJoueurs disponibles :\n1. Alice\n2. Bob\n"
        f"Nombre de participants : {nb}\n"
    )


class TestParcours(unittest.TestCase):

    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.chemin_donnees = os.path.join(dossier.name, "donnees.json")

    def lancer_le_jeu(self, reponses, secrets=()):
        """Joue un parcours complet et renvoie tout le texte affiché.

        Les données sont écrites dans un dossier temporaire, jamais dans le dépôt.
        Plusieurs appels d'un même test partagent ce fichier (reprise de session).
        """
        reponses = iter(reponses)
        secrets = iter(secrets)
        texte = io.StringIO()

        def fausse_saisie(source, nom_source, reponse_visible):
            def saisir(invite=""):
                try:
                    reponse = next(source)
                except StopIteration:
                    self.fail(f"Le jeu attend une réponse de plus ({nom_source}) : {invite!r}")
                affichee = reponse if reponse_visible else ""
                texte.write(f"{invite}{affichee}\n")
                return reponse
            return saisir

        for nom_module in MODULES_DU_JEU:
            sys.modules.pop(nom_module, None)

        with mock.patch("builtins.input", fausse_saisie(reponses, "input", True)), \
                mock.patch("getpass.getpass", fausse_saisie(secrets, "getpass", False)), \
                mock.patch("random.sample", lambda population, k: list(population)[:k]), \
                contextlib.redirect_stdout(texte):
            import main
            main.main(self.chemin_donnees)

        self.assertEqual(list(reponses), [], "Des réponses n'ont pas été utilisées")
        self.assertEqual(list(secrets), [], "Des choix cachés n'ont pas été utilisés")
        return texte.getvalue()

    # ------------------------------
    # Menu                         |
    # ------------------------------

    def test_quitter_directement(self):
        sortie = self.lancer_le_jeu(["10"])

        self.assertEqual(sortie, choix_menu("10") + AU_REVOIR)

    def test_choix_de_menu_invalide_puis_quitter(self):
        sortie = self.lancer_le_jeu(["abc", "10"])

        attendu = choix_menu("abc") + "Choix invalide, réessaye\n" + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    # ------------------------------
    # Sans joueur                  |
    # ------------------------------

    def test_classement_sans_joueur(self):
        sortie = self.lancer_le_jeu(["5", "10"])

        self.assertEqual(sortie, choix_menu("5") + AUCUN_JOUEUR + choix_menu("10") + AU_REVOIR)

    def test_statistiques_sans_joueur(self):
        sortie = self.lancer_le_jeu(["6", "10"])

        self.assertEqual(sortie, choix_menu("6") + AUCUN_JOUEUR + choix_menu("10") + AU_REVOIR)

    def test_regles(self):
        sortie = self.lancer_le_jeu(["7", "10"])

        self.assertEqual(sortie, choix_menu("7") + REGLES + choix_menu("10") + AU_REVOIR)

    def test_reprendre_un_tournoi_sans_tournoi(self):
        sortie = self.lancer_le_jeu(["3", "10"])

        attendu = choix_menu("3") + "Aucun tournoi en cours.\n" + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    def test_historique_sans_tournoi(self):
        sortie = self.lancer_le_jeu(["4", "10"])

        attendu = choix_menu("4") + "Aucun tournoi terminé.\n" + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    # ------------------------------
    # Création de joueurs          |
    # ------------------------------

    def test_creer_deux_joueurs_puis_classement(self):
        sortie = self.lancer_le_jeu(REPONSES_ALICE_BOB + ["5", "10"])

        attendu = SORTIE_ALICE_BOB + choix_menu("5") + CLASSEMENT_ALICE_BOB + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    def test_creer_deux_joueurs_puis_statistiques(self):
        sortie = self.lancer_le_jeu(REPONSES_ALICE_BOB + ["6", "10"])

        attendu = SORTIE_ALICE_BOB + choix_menu("6") + STATISTIQUES_ALICE_BOB + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    def test_creer_deux_joueurs_puis_regles(self):
        sortie = self.lancer_le_jeu(REPONSES_ALICE_BOB + ["7", "10"])

        attendu = SORTIE_ALICE_BOB + choix_menu("7") + REGLES + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    # ------------------------------
    # Pierre-feuille-ciseaux       |
    # ------------------------------

    def test_ppc_avec_moins_de_deux_joueurs(self):
        sortie = self.lancer_le_jeu(["8", "10"])

        attendu = choix_menu("8") + "Il faut au moins 2 joueurs pour jouer.\n" + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    def jouer_ppc(self, secrets):
        """Deux joueurs, une partie de PPC, puis quitter. Renvoie la sortie."""
        return self.lancer_le_jeu(REPONSES_ALICE_BOB + ["8", "10"], secrets)

    def test_ppc_victoire_du_premier(self):
        sortie = self.jouer_ppc(["p", "c"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("8")
            + "Alice affronte Bob !\n"
            "Alice, choisis [p] / [f] / [c] : \n"
            "Bob, choisis [p] / [f] / [c] : \n"
            "Alice a choisi pierre\n"
            "Bob a choisi ciseaux\n"
            "Le gagnant est : Alice\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_ppc_victoire_du_second(self):
        sortie = self.jouer_ppc(["p", "f"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("8")
            + "Alice affronte Bob !\n"
            "Alice, choisis [p] / [f] / [c] : \n"
            "Bob, choisis [p] / [f] / [c] : \n"
            "Alice a choisi pierre\n"
            "Bob a choisi feuille\n"
            "Le gagnant est : Bob\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_ppc_egalite(self):
        sortie = self.jouer_ppc(["f", "f"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("8")
            + "Alice affronte Bob !\n"
            "Alice, choisis [p] / [f] / [c] : \n"
            "Bob, choisis [p] / [f] / [c] : \n"
            "Alice a choisi feuille\n"
            "Bob a choisi feuille\n"
            "Égalité !\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_ppc_saisie_invalide_puis_valide(self):
        sortie = self.jouer_ppc(["x", "P", "c"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("8")
            + "Alice affronte Bob !\n"
            "Alice, choisis [p] / [f] / [c] : \n"
            "Choix invalide. Tape p, f ou c.\n"
            "Alice, choisis [p] / [f] / [c] : \n"
            "Bob, choisis [p] / [f] / [c] : \n"
            "Alice a choisi pierre\n"
            "Bob a choisi ciseaux\n"
            "Le gagnant est : Alice\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    # ------------------------------
    # Morpion                      |
    # ------------------------------

    def jouer_morpion(self, coups):
        """Deux joueurs, une partie de morpion avec ces saisies, puis quitter."""
        return self.lancer_le_jeu(REPONSES_ALICE_BOB + ["9"] + coups + ["10"])

    def test_morpion_avec_moins_de_deux_joueurs(self):
        sortie = self.lancer_le_jeu(["9", "10"])

        attendu = choix_menu("9") + "Il faut au moins 2 joueurs.\n" + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    def test_morpion_victoire_de_x_en_ligne(self):
        sortie = self.jouer_morpion(["1", "4", "2", "5", "3"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("9")
            + tour_morpion("         ", "Alice", "1")
            + tour_morpion("X        ", "Bob", "4")
            + tour_morpion("X  O     ", "Alice", "2")
            + tour_morpion("XX O     ", "Bob", "5")
            + tour_morpion("XX OO    ", "Alice", "3")
            + fin_morpion("XXXOO    ", "Le gagnant est : Alice")
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_morpion_victoire_de_o(self):
        sortie = self.jouer_morpion(["1", "4", "2", "5", "9", "6"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("9")
            + tour_morpion("         ", "Alice", "1")
            + tour_morpion("X        ", "Bob", "4")
            + tour_morpion("X  O     ", "Alice", "2")
            + tour_morpion("XX O     ", "Bob", "5")
            + tour_morpion("XX OO    ", "Alice", "9")
            + tour_morpion("XX OO   X", "Bob", "6")
            + fin_morpion("XX OOO  X", "Le gagnant est : Bob")
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_morpion_partie_nulle(self):
        sortie = self.jouer_morpion(["1", "2", "3", "5", "4", "6", "8", "7", "9"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("9")
            + tour_morpion("         ", "Alice", "1")
            + tour_morpion("X        ", "Bob", "2")
            + tour_morpion("XO       ", "Alice", "3")
            + tour_morpion("XOX      ", "Bob", "5")
            + tour_morpion("XOX O    ", "Alice", "4")
            + tour_morpion("XOXXO    ", "Bob", "6")
            + tour_morpion("XOXXOO   ", "Alice", "8")
            + tour_morpion("XOXXOO X ", "Bob", "7")
            + tour_morpion("XOXXOOOX ", "Alice", "9")
            + fin_morpion("XOXXOOOXX", "Égalité !")
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def verifier_coup_refuse(self, saisie_refusee, message):
        """Alice joue 1, Bob tente une saisie refusée, puis la partie se termine."""
        sortie = self.jouer_morpion(["1", saisie_refusee, "4", "2", "5", "3"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("9")
            + tour_morpion("         ", "Alice", "1")
            + tour_morpion("X        ", "Bob", saisie_refusee) + message
            + tour_morpion("X        ", "Bob", "4")
            + tour_morpion("X  O     ", "Alice", "2")
            + tour_morpion("XX O     ", "Bob", "5")
            + tour_morpion("XX OO    ", "Alice", "3")
            + fin_morpion("XXXOO    ", "Le gagnant est : Alice")
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_morpion_case_deja_prise(self):
        self.verifier_coup_refuse("1", "Case invalide ou déjà prise.\n")

    def test_morpion_saisie_non_numerique(self):
        self.verifier_coup_refuse("abc", "Choix invalide.\n")

    def test_morpion_case_zero_hors_grille(self):
        self.verifier_coup_refuse("0", "Case invalide ou déjà prise.\n")

    def test_morpion_case_dix_hors_grille(self):
        self.verifier_coup_refuse("10", "Case invalide ou déjà prise.\n")

    # ------------------------------
    # Tournoi                      |
    # ------------------------------

    def test_tournoi_sans_joueur(self):
        sortie = self.lancer_le_jeu(["2", "10"])

        attendu = (
            choix_menu("2")
            + "Aucun joueur créé, créez des joueurs avant de lancer un tournoi.\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_tournoi_jeu_invalide(self):
        sortie = self.lancer_le_jeu(REPONSES_ALICE_BOB + ["2", "Coupe", "dames", "10"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("2")
            + "\n===== Création d'un tournoi =====\n"
            "Nom du tournoi : Coupe\n"
            "Choisir le jeu (PPC/Morpion) : dames\n"
            "Choix invalide, tournoi annulé.\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_tournoi_format_invalide(self):
        sortie = self.lancer_le_jeu(REPONSES_ALICE_BOB + ["2", "Coupe", "PPC", "suisse", "10"])

        attendu = (
            SORTIE_ALICE_BOB + choix_menu("2")
            + "\n===== Création d'un tournoi =====\n"
            "Nom du tournoi : Coupe\n"
            "Choisir le jeu (PPC/Morpion) : PPC\n"
            "Format du tournoi (Round-Robin/Elimination directe) : suisse\n"
            "Format invalide, tournoi annulé.\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def verifier_nombre_refuse(self, saisie, message):
        sortie = self.lancer_le_jeu(
            REPONSES_ALICE_BOB + ["2", "Coupe", "ppc", "Round-Robin", saisie, "10"]
        )

        attendu = (
            SORTIE_ALICE_BOB
            + tournoi_jusqu_aux_participants(saisie)
            + message
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_tournoi_nombre_de_participants_non_numerique(self):
        self.verifier_nombre_refuse("deux", "Nombre invalide\n")

    def test_tournoi_nombre_de_participants_trop_petit(self):
        self.verifier_nombre_refuse("1", "Nombre de participants invalide\n")

    def test_tournoi_nombre_de_participants_trop_grand(self):
        self.verifier_nombre_refuse("3", "Nombre de participants invalide\n")

    def verifier_tournoi_cree(self, numeros_saisis, messages, nb_participants):
        """Crée un tournoi à 2 participants demandés avec ces numéros de joueur."""
        sortie = self.lancer_le_jeu(
            REPONSES_ALICE_BOB
            + ["2", "Coupe", "ppc", "Round-Robin", "2"] + numeros_saisis + ["10"]
        )

        attendu = (
            SORTIE_ALICE_BOB
            + tournoi_jusqu_aux_participants("2")
            + messages
            + f"\nTournoi 'Coupe' créé avec {nb_participants} participants !\n\n"
            "Tournoi 'Coupe' créé et prêt pour le tournoi !\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertEqual(sortie, attendu)

    def test_tournoi_cree_avec_deux_joueurs(self):
        self.verifier_tournoi_cree(
            ["1", "2"],
            "Choisir le numéro d'un joueur : 1\nChoisir le numéro d'un joueur : 2\n",
            2,
        )

    def test_tournoi_numero_de_joueur_non_numerique(self):
        self.verifier_tournoi_cree(
            ["x", "1", "2"],
            "Choisir le numéro d'un joueur : x\nNuméro invalide\n"
            "Choisir le numéro d'un joueur : 1\n"
            "Choisir le numéro d'un joueur : 2\n",
            2,
        )

    def test_tournoi_numero_de_joueur_hors_liste(self):
        self.verifier_tournoi_cree(
            ["5", "1", "2"],
            "Choisir le numéro d'un joueur : 5\n"
            "Choix invalide, joueur déjà choisi ou numéro incorrect\n"
            "Choisir le numéro d'un joueur : 1\n"
            "Choisir le numéro d'un joueur : 2\n",
            2,
        )

    def test_tournoi_joueur_deja_choisi(self):
        self.verifier_tournoi_cree(
            ["1", "1", "2"],
            "Choisir le numéro d'un joueur : 1\n"
            "Choisir le numéro d'un joueur : 1\n"
            "Choix invalide, joueur déjà choisi ou numéro incorrect\n"
            "Choisir le numéro d'un joueur : 2\n",
            2,
        )

    # ------------------------------
    # ELO après une partie         |
    # ------------------------------

    def test_partie_ppc_puis_classement(self):
        sortie = self.lancer_le_jeu(REPONSES_ALICE_BOB + ["8", "5", "10"], ["p", "c"])

        classement = (
            "\n==============================\n"
            "        CLASSEMENT ELO\n"
            "==============================\n"
            "Nom             ELO    Victoires Défaites\n"
            "------------------------------\n"
            "Alice           1050   1         0       \n"
            "Bob             950    0         1       \n"
            "==============================\n\n"
        )
        self.assertIn("Le gagnant est : Alice\n" + choix_menu("5") + classement, sortie)

    # ------------------------------
    # Tournois : création, reprise |
    # ------------------------------

    REPONSES_TOURNOI_PPC = ["2", "Coupe", "ppc", "Round-Robin", "2", "1", "2"]

    def test_tournoi_cree_puis_repris_jusqu_au_champion(self):
        reponses = REPONSES_ALICE_BOB + self.REPONSES_TOURNOI_PPC + ["3", "1", "10"]

        sortie = self.lancer_le_jeu(reponses, ["p", "c"])

        self.assertIn("1. Coupe (ppc - Round-Robin) [0/0]\n", sortie)
        self.assertIn("Alice contre Bob\n", sortie)
        self.assertIn("Alice a choisi pierre\nBob a choisi ciseaux\n", sortie)
        self.assertTrue(sortie.endswith("Champion : Alice\n" + choix_menu("10") + AU_REVOIR))

    def test_tournoi_termine_n_est_plus_a_reprendre(self):
        reponses = REPONSES_ALICE_BOB + self.REPONSES_TOURNOI_PPC + ["3", "1", "3", "10"]

        sortie = self.lancer_le_jeu(reponses, ["p", "c"])

        attendu_fin = "Aucun tournoi en cours.\n" + choix_menu("10") + AU_REVOIR
        self.assertTrue(sortie.endswith(attendu_fin))

    def test_reprendre_avec_un_numero_invalide(self):
        reponses = REPONSES_ALICE_BOB + self.REPONSES_TOURNOI_PPC + ["3", "9", "10"]

        sortie = self.lancer_le_jeu(reponses)

        attendu_fin = (
            choix_menu("3") + "1. Coupe (ppc - Round-Robin) [0/0]\n"
            "Numéro du tournoi à reprendre : 9\n"
            "Choix invalide.\n" + choix_menu("10") + AU_REVOIR
        )
        self.assertTrue(sortie.endswith(attendu_fin))

    def test_historique_avec_detail_d_un_tournoi(self):
        reponses = REPONSES_ALICE_BOB + self.REPONSES_TOURNOI_PPC + ["3", "1", "4", "1", "10"]

        sortie = self.lancer_le_jeu(reponses, ["p", "c"])

        attendu_fin = (
            choix_menu("4")
            + "1. Coupe (ppc - Round-Robin) - champion : Alice\n"
            "Numéro du tournoi à détailler (vide pour revenir) : 1\n"
            "Tournoi : Coupe\n"
            "Jeu : ppc\n"
            "Format : Round-Robin\n"
            "Participants : Alice, Bob\n"
            "Matchs :\n"
            "  Tour 1 :\n"
            "    - Alice bat Bob\n"
            "Champion : Alice\n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertTrue(sortie.endswith(attendu_fin))

    def test_historique_detail_vide_revient_au_menu(self):
        reponses = REPONSES_ALICE_BOB + self.REPONSES_TOURNOI_PPC + ["3", "1", "4", "", "10"]

        sortie = self.lancer_le_jeu(reponses, ["p", "c"])

        attendu_fin = (
            "Numéro du tournoi à détailler (vide pour revenir) : \n"
            + choix_menu("10") + AU_REVOIR
        )
        self.assertTrue(sortie.endswith(attendu_fin))

    def test_elimination_a_trois_joueurs_au_morpion(self):
        victoire_de_x = ["1", "4", "2", "5", "3"]
        reponses = (
            ["1", "Alice", "1", "Bob", "1", "Carl", "2"]
            + ["2", "Coupe", "morpion", "Elimination directe", "3", "1", "2", "3"]
            + ["3", "1"] + victoire_de_x + victoire_de_x
            + ["4", "1", "10"]
        )

        sortie = self.lancer_le_jeu(reponses)

        self.assertIn("Alice contre Bob\n", sortie)
        self.assertIn("Alice contre Carl\n", sortie)
        self.assertIn("Champion : Alice\n", sortie)
        self.assertIn("    - Alice bat Carl\n", sortie)
        self.assertIn("Tour 2 : Alice bat Carl\n", sortie)
        self.assertTrue(sortie.endswith(choix_menu("10") + AU_REVOIR))

    # ------------------------------
    # Persistance                  |
    # ------------------------------

    def test_les_joueurs_sont_retrouves_au_lancement_suivant(self):
        self.lancer_le_jeu(REPONSES_ALICE_BOB + ["10"])

        sortie = self.lancer_le_jeu(["6", "10"])

        attendu = choix_menu("6") + STATISTIQUES_ALICE_BOB + choix_menu("10") + AU_REVOIR
        self.assertEqual(sortie, attendu)

    def test_elo_et_tournoi_sont_retrouves_au_lancement_suivant(self):
        reponses = REPONSES_ALICE_BOB + self.REPONSES_TOURNOI_PPC + ["3", "1", "10"]
        self.lancer_le_jeu(reponses, ["p", "c"])

        sortie = self.lancer_le_jeu(["4", "", "5", "10"])

        self.assertIn("1. Coupe (ppc - Round-Robin) - champion : Alice\n", sortie)
        self.assertIn("Alice           1050   1         0", sortie)

    def test_fichier_illisible_est_mis_de_cote_et_le_jeu_repart_a_vide(self):
        with open(self.chemin_donnees, "w", encoding="utf-8") as fichier:
            fichier.write("ceci n'est pas du json")

        sortie = self.lancer_le_jeu(["6", "10"])

        self.assertIn("Données illisibles, démarrage à vide : ", sortie)
        self.assertIn(AUCUN_JOUEUR + choix_menu("10"), sortie)
        self.assertFalse(os.path.exists(self.chemin_donnees))
        with open(self.chemin_donnees + ".illisible", encoding="utf-8") as fichier:
            self.assertEqual(fichier.read(), "ceci n'est pas du json")

    def test_fichier_illisible_ne_remplace_pas_un_fichier_deja_mis_de_cote(self):
        for contenu in ("premier", "second"):
            with open(self.chemin_donnees, "w", encoding="utf-8") as fichier:
                fichier.write(contenu)
            self.lancer_le_jeu(["10"])

        for suffixe, contenu in ((".illisible", "premier"), (".illisible2", "second")):
            with open(self.chemin_donnees + suffixe, encoding="utf-8") as fichier:
                self.assertEqual(fichier.read(), contenu)

    def test_tournoi_d_un_jeu_inconnu_dans_le_fichier_ne_plante_pas(self):
        joueur = {"nom": "Alice", "type": "humain", "elo": 1000, "joues": 0,
                  "victoires": 0, "defaites": 0, "historique": []}
        tournoi = {"nom": "Coupe", "jeu": "dames", "format": "round-robin", "participants": [0, 0],
                   "matchs": [], "termine": False, "champion": None}
        with open(self.chemin_donnees, "w", encoding="utf-8") as fichier:
            json.dump({"joueurs": [joueur], "tournois": [tournoi]}, fichier)

        sortie = self.lancer_le_jeu(["3", "1", "10"])

        self.assertIn("Jeu inconnu : 'dames'\n" + choix_menu("10") + AU_REVOIR, sortie)

    def test_echec_de_sauvegarde_n_arrete_pas_le_jeu(self):
        dossier_absent = os.path.join(os.path.dirname(self.chemin_donnees), "absent")
        self.chemin_donnees = os.path.join(dossier_absent, "donnees.json")

        sortie = self.lancer_le_jeu(REPONSES_ALICE_BOB + ["6", "10"])

        self.assertIn("Sauvegarde impossible : ", sortie)
        self.assertIn(STATISTIQUES_ALICE_BOB, sortie)
        self.assertTrue(sortie.endswith(AU_REVOIR))


if __name__ == "__main__":
    unittest.main()
