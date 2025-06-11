# -*- coding: utf-8 -*-
"""
Simulation.py
=============

Module principal pour la gestion de la simulation ferroviaire :
- Définit la classe Train et la classe Simulation.
- Gère l’ajout, la suppression, le placement et le transfert des trains sur les voies des dépôts.
- Prend en compte la longueur des trains, les conflits d’occupation, la priorité pour les trains électriques, etc.

Auteur : andre
Date de création : 02/05/2025
"""

from datetime import datetime, timedelta
from UTILES import verifier_conflit

class Train:
    """
    Représente un train dans la simulation.

    Attributs :
        id (int) : Identifiant unique du train.
        nom (str) : Nom du train.
        wagons (int) : Nombre de wagons.
        locomotives (int) : Nombre de locomotives.
        longueur (int) : Longueur totale du train (calculée automatiquement).
        arrivee (datetime) : Heure d'arrivée prévue.
        depart (datetime) : Heure de départ prévue.
        en_attente (bool) : Indique si le train est en attente de placement.
        debut_attente (datetime) : Heure de début d'attente.
        fin_attente (datetime) : Heure de fin d'attente (si applicable).
        voie (int) : Index de la voie attribuée.
        electrique (bool) : Indique si le train est électrique.
        depot (str) : Nom du dépôt d'origine.
        type (str) : Type de train ("Storage", "testing", "pit", etc.).
        locomotive_cote (str) : Côté de la locomotive (optionnel).
        type_wagon (str) : Type de wagon (optionnel).
    """
    def __init__(self, id, nom, wagons, locomotives, arrivee, depart, depot, type="Storage"):
        """
        Initialise un train.

        Args:
            id: Identifiant unique du train.
            nom: Nom du train.
            wagons: Nombre de wagons.
            locomotives: Nombre de locomotives.
            arrivee: Heure d'arrivée.
            depart: Heure de départ.
            depot: Dépôt d'origine.
            type: Type de train (par défaut "Storage").
        """
        self.id = id
        self.nom = nom
        self.wagons = wagons
        self.locomotives = locomotives
        self.longueur = self.calculer_longueur()  # Calcul automatique de la longueur
        self.arrivee = arrivee
        self.depart = depart
        self.en_attente = False
        self.debut_attente = None
        self.fin_attente = None
        self.voie = None
        self.electrique = False  # Par défaut
        self.depot = depot
        self.type = type
        self.locomotive_cote = None
        self.type_wagon = None

    def calculer_longueur(self):
        """
        Calcule la longueur totale du train en fonction des wagons et des locomotives.

        Returns:
            int: Longueur totale du train (en mètres).
        """
        longueur_wagon = 14  # Longueur d'un wagon en mètres
        longueur_locomotive = 19  # Longueur d'une locomotive en mètres
        return self.wagons * longueur_wagon + self.locomotives * longueur_locomotive

class Simulation:
    """
    Gère l'ensemble de la simulation ferroviaire :
    - Stocke les trains, les occupations de voies, les longueurs de voies, etc.
    - Permet d'ajouter, de recalculer, de transférer ou de réinitialiser les trains et occupations.
    """

    def __init__(self, depots_config=None):
        """
        Initialise la simulation avec une structure multi-dépôts.
        depots_config : dict du type
            {
                "Glostrup": {"numeros_voies": [7,8,9,11], "longueurs_voies": [290,340,400,300]},
                "Naestved": {"numeros_voies": [1,2,3,4], "longueurs_voies": [250,300,350,280]},
                ...
            }
        """
        if depots_config is None:
            depots_config = {
                "Glostrup": {"numeros_voies": [7,8,9,11], "longueurs_voies": [290,340,400,300]},
                "Naestved": {"numeros_voies": [1,2,3,4], "longueurs_voies": [250,300,350,280]}
            }
        self.depots = {}
        for nom, conf in depots_config.items():
            self.depots[nom] = {
                "numeros_voies": conf["numeros_voies"],
                "longueurs_voies": conf["longueurs_voies"],
                "occupation": []  # Liste des tuples (voie_idx, debut, fin, train)
            }

        self.trains = []  # Liste de tous les trains
        self.delai_securite = 10  # Délai de sécurité en minutes
        self.historique = []  # Liste des actions (ajout, suppression, modification)
        
    @property
    def occupation_a(self):
        return self.depots["Glostrup"]["occupation"]

    @property
    def occupation_b(self):
        return self.depots["Naestved"]["occupation"]

    @property
    def numeros_voies_a(self):
        return self.depots["Glostrup"]["numeros_voies"]

    @property
    def numeros_voies_b(self):
        return self.depots["Naestved"]["numeros_voies"]

    @property
    def longueurs_voies_a(self):
        return self.depots["Glostrup"]["longueurs_voies"]

    @property
    def longueurs_voies_b(self):
        return self.depots["Naestved"]["longueurs_voies"]
    
    # --- Ajout d'un dépôt dynamiquement ---
    def ajouter_depot(self, nom, numeros_voies, longueurs_voies):
       if nom in self.depots:
           return "Ce dépôt existe déjà."
       self.depots[nom] = {
           "numeros_voies": numeros_voies,
           "longueurs_voies": longueurs_voies,
           "occupation": []
       }

    def ajouter_train(self, train, depot, optimiser=False, ajouter_a_liste=True):
        """
        Tente d'ajouter un train dans le dépôt spécifié, en respectant les contraintes de longueur,
        de conflits d'occupation et de priorité pour les trains électriques.

        Args:
            train (Train): Le train à ajouter.
            depot (str): "Glostrup" ou "Naestved".
            optimiser (bool): Si True, cherche le meilleur créneau possible.
            ajouter_a_liste (bool): Si True, ajoute le train à self.trains.

        Returns:
            str|None: Message d'erreur si échec, sinon None.
        """
        if train.arrivee >= train.depart:
            return "L'heure d'arrivée doit être antérieure à l'heure de départ."
        if train.longueur <= 0:
            return "La longueur du train doit être positive."
        if depot not in self.depots:
            return f"Dépôt {depot} inconnu."
    
        train.en_attente = False
        train.debut_attente = train.arrivee
    
        depot_data = self.depots[depot]
        occupation = depot_data["occupation"]
        numeros_voies = depot_data["numeros_voies"]
        longueurs_voies = depot_data["longueurs_voies"]

        # Priorité pour la voie 9 si le train est électrique
        if train.electrique and 9 in numeros_voies:
            voie9_idx = numeros_voies.index(9)
            if longueurs_voies[voie9_idx] >= train.longueur:
                # Chercher la première disponibilité sur la voie 9
                debut_possible = train.arrivee
                while True:
                    conflit = verifier_conflit(voie9_idx, debut_possible, train.depart, occupation, self.delai_securite)
                    if not conflit:
                        break
                    # Décaler le début à la fin du conflit + délai de sécurité
                    conflits = [occ for occ in occupation if occ[0] == voie9_idx and not (train.depart + timedelta(minutes=self.delai_securite) <= occ[1] or debut_possible - timedelta(minutes=self.delai_securite) >= occ[2])]
                    if conflits:
                        debut_possible = max(occ[2] for occ in conflits) + timedelta(minutes=self.delai_securite)
                    else:
                        break
                if debut_possible > train.arrivee:
                    train.en_attente = True
                    train.debut_attente = train.arrivee
                    train.fin_attente = debut_possible
                else:
                    train.en_attente = False
                    train.debut_attente = train.arrivee
                    train.fin_attente = debut_possible
                train.voie = voie9_idx
                occupation.append((voie9_idx, debut_possible, train.depart, train))
                if ajouter_a_liste:
                    self.trains.append(train)
                    self.trains.sort(key=lambda t: t.arrivee)
                    self.historique.append({
                        "action": "ajout",
                        "train_id": train.id,
                        "etat_avant": None,
                        "etat_apres": train.__dict__.copy()
                    })
                return

        # Sinon, chercher la meilleure voie et le meilleur créneau
        meilleure_voie, meilleur_debut = self.chercher_voie_disponible(
            train, train.arrivee, occupation, longueurs_voies, optimiser
        )
        if meilleure_voie is not None:
            if meilleur_debut > train.arrivee:
                train.en_attente = True
                train.debut_attente = train.arrivee
                train.fin_attente = meilleur_debut
            else:
                train.en_attente = False
                train.debut_attente = train.arrivee
                train.fin_attente = meilleur_debut
            train.voie = meilleure_voie
            occupation.append((meilleure_voie, meilleur_debut, train.depart, train))
            if ajouter_a_liste:
                self.trains.append(train)
                self.trains.sort(key=lambda t: t.arrivee)
                self.historique.append({
                    "action": "ajout",
                    "train_id": train.id,
                    "etat_avant": None,
                    "etat_apres": train.__dict__.copy()
                })
                self.recalculer()
            return
        # Si aucune voie n'est disponible du tout
        train.en_attente = True
        train.debut_attente = train.arrivee
        train.fin_attente = None
        if ajouter_a_liste:
            self.trains.append(train)
            self.trains.sort(key=lambda t: t.arrivee)
            self.historique.append({
                                "action": "ajout",
                                "train_id": train.id,
                                "etat_avant": None,
                                "etat_apres": train.__dict__.copy()
                            })
            self.recalculer()
        return "Le train n'a pas pu être placé dans le dépôt."
    
    def gerer_voie_9(self, train, occupation, numeros_voies, longueurs_voies):
        """
        Gère le placement d'un train électrique sur la voie 9 (Glostrup).

        Args:
            train (Train): Le train à placer.
            occupation (list): Occupations actuelles.
            numeros_voies (list): Numéros des voies.
            longueurs_voies (list): Longueurs des voies.

        Returns:
            bool: True si placement réussi, False sinon.
        """
        voie9_idx = numeros_voies.index(9)
        if longueurs_voies[voie9_idx] < train.longueur:
            return False

        debut = train.arrivee
        while True:
            conflit = False
            for v, occ_debut, occ_fin, _ in occupation:
                if v == voie9_idx and (debut - timedelta(minutes=self.delai_securite) < occ_fin and train.depart + timedelta(minutes=self.delai_securite) > occ_debut):
                    conflit = True
                    debut = occ_fin + timedelta(minutes=self.delai_securite)
                    break
            if not conflit:
                break

        duree = (train.depart - train.arrivee)
        if debut + duree <= train.depart:
            train.en_attente = (debut != train.arrivee)
            train.fin_attente = debut
            train.voie = voie9_idx
            occupation.append((voie9_idx, debut, train.depart, train))
            self.trains.append(train)
            return True
        return False

    def chercher_voie_disponible(self, train, ref, occupation, longueurs_voies, optimiser):
        """
        Cherche la meilleure voie disponible pour placer le train.

        Args:
            train (Train): Le train à placer.
            ref (datetime): Heure de référence pour le placement.
            occupation (list): Occupations actuelles.
            longueurs_voies (list): Longueurs des voies.
            optimiser (bool): Si True, cherche le meilleur créneau.

        Returns:
            tuple: (index_voie, heure_debut) ou (None, None) si aucune voie.
        """
        occupation_par_voie = {i: [] for i in range(len(longueurs_voies))}
        for v, occ_debut, occ_fin, _ in occupation:
            occupation_par_voie[v].append((occ_debut, occ_fin))
            
        for voie, occs in occupation_par_voie.items():
            occupation_par_voie[voie] = sorted(occs, key=lambda x: x[0])  # Tri par heure de début
    
        meilleure_voie = None
        meilleur_debut = None
        for i, longueur in enumerate(longueurs_voies):
            if longueur < train.longueur:
                continue
            debut = ref
            for occ_debut, occ_fin in sorted(occupation_par_voie[i]):
                if debut - timedelta(minutes=self.delai_securite) < occ_fin and train.depart + timedelta(minutes=self.delai_securite) > occ_debut:
                    debut = occ_fin + timedelta(minutes=self.delai_securite)
            if debut is not None and (meilleur_debut is None or debut < meilleur_debut):
                meilleure_voie = i
                meilleur_debut = debut
        return meilleure_voie, meilleur_debut

    def reset(self):
        """
        Réinitialise la simulation : efface toutes les occupations et tous les trains.
        """
        for depot in self.depots.values():
            depot["occupation"].clear()
        self.trains.clear()

    def recalculer(self, optimiser=False):
        """
        Recalcule les occupations des voies après une modification ou suppression de train.
        Les trains restent dans leur dépôt d'origine et les duplications sont évitées.

        Args:
            optimiser (bool): Si True, cherche le meilleur créneau possible.
        """
        # Réinitialiser les occupations
        for depot in self.depots.values():
            depot["occupation"].clear()

        # Réinitialiser les voies des trains
        for train in self.trains:
            train.voie = None
            train.en_attente = False
            train.debut_attente = train.arrivee
            train.fin_attente = None

        # Replacer les trains dans chaque dépôt
        for depot_nom in self.depots:
            trains_depot = [train for train in self.trains if train.depot == depot_nom]
            # Priorité aux trains électriques sur la voie 9 si elle existe
            trains_elec = [t for t in trains_depot if t.electrique and 9 in self.depots[depot_nom]["numeros_voies"]]
            for train in sorted(trains_elec, key=lambda t: t.arrivee):
                self.ajouter_train_sans_ajout_liste(train, depot_nom, optimiser=optimiser, priorite_voie_9=True)
            # Les autres trains
            autres_trains = [t for t in trains_depot if not (t.electrique and 9 in self.depots[depot_nom]["numeros_voies"])]
            for train in sorted(autres_trains, key=lambda t: t.arrivee):
                self.ajouter_train_sans_ajout_liste(train, depot_nom, optimiser=optimiser)
    
        print(f"Occupation Glostrup après recalcul : {self.occupation_a}")
        print(f"Occupation Naestved après recalcul : {self.occupation_b}")
        print(f"Trains après recalcul : {[t.nom for t in self.trains]}")

    def ajouter_train_sans_ajout_liste(self, train, depot, optimiser=False, priorite_voie_9=False):
        """
        Ajoute un train à une voie sans l'ajouter à la liste self.trains.
        Utilisé uniquement pour recalculer les occupations.

        Args:
            train (Train): Le train à placer.
            depot (str): "Glostrup" ou "Naestved".
            optimiser (bool): Si True, cherche le meilleur créneau.
            priorite_voie_9 (bool): Si True, tente la voie 9 en priorité.
        """
        depot_data = self.depots[depot]
        occupation = depot_data["occupation"]
        numeros_voies = depot_data["numeros_voies"]
        longueurs_voies = depot_data["longueurs_voies"]
    
        # Priorité pour la voie 9 si spécifié
        if priorite_voie_9 and 9 in numeros_voies:
            voie9_idx = numeros_voies.index(9)
            if longueurs_voies[voie9_idx] >= train.longueur:
                if not verifier_conflit(voie9_idx, train.arrivee, train.depart, occupation, self.delai_securite):
                    train.voie = voie9_idx
                    train.fin_attente = train.arrivee
                    occupation.append((voie9_idx, train.arrivee, train.depart, train))
                    return
    
        # Sinon, chercher une autre voie disponible
        meilleure_voie, meilleur_debut = self.chercher_voie_disponible(train, train.arrivee, occupation, longueurs_voies, optimiser)
        if meilleure_voie is not None:
            train.voie = meilleure_voie
            train.fin_attente = meilleur_debut
            occupation.append((meilleure_voie, meilleur_debut, train.depart, train))
        else:
            train.en_attente = True

    def ajouter_train_multi_depot(self, train, optimiser=False):
        # Essaye d'abord dans le dépôt d'origine
        erreur = self.ajouter_train(train, train.depot, optimiser=optimiser)
        if not erreur:
            return None
        # Sinon, tente dans les autres dépôts
        for depot in self.depots:
            if depot != train.depot:
                erreur2 = self.ajouter_train(train, depot, optimiser=optimiser)
                if not erreur2:
                    train.depot = depot
                    return None
        return "Aucun dépôt ne peut accueillir ce train."
    def undo(self):
        if not self.historique:
            return "Aucune action à annuler."
        last = self.historique.pop()
        if last["action"] == "ajout":
            # Supprimer le train ajouté
            self.trains = [t for t in self.trains if t.id != last["train_id"]]
        elif last["action"] == "suppression":
            # Restaurer le train supprimé
            from copy import deepcopy
            train = Train(**{k: v for k, v in last["etat_avant"].items() if k in Train.__init__.__code__.co_varnames})
            for k, v in last["etat_avant"].items():
                setattr(train, k, v)
            self.trains.append(train)
        elif last["action"] == "modification":
            # Restaurer l'état avant modification
            train = next((t for t in self.trains if t.id == last["train_id"]), None)
            if train:
                for k, v in last["etat_avant"].items():
                    setattr(train, k, v)
        self.recalculer()
        return None