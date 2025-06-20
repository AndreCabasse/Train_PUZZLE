# -*- coding: utf-8 -*-
"""
Simulation.py
=============

Module principal pour la gestion de la simulation ferroviaire :
FR: Définit la classe Train et la classe Simulation.
EN: Defines the Train and Simulation classes.
FR: Gère l’ajout, la suppression, le placement et le transfert des trains sur les voies des dépôts.
EN: Manages adding, removing, placing, and transferring trains on depot tracks.
FR: Prend en compte la longueur des trains, les conflits d’occupation, la priorité pour les trains électriques, etc.
EN: Takes into account train length, occupation conflicts, electric train priority, etc.

Auteur : andre
Date de création : 02/05/2025
"""

from datetime import datetime, timedelta
from UTILES import verifier_conflit

class Train:
    """
    FR: Représente un train dans la simulation.
    EN: Represents a train in the simulation.

    Attributs / Attributes :
        id (int) : FR: Identifiant unique du train. / EN: Unique train identifier.
        nom (str) : FR: Nom du train. / EN: Train name.
        wagons (int) : FR: Nombre de wagons. / EN: Number of wagons.
        locomotives (int) : FR: Nombre de locomotives. / EN: Number of locomotives.
        longueur (int) : FR: Longueur totale du train (calculée automatiquement). / EN: Total train length (auto-calculated).
        arrivee (datetime) : FR: Heure d'arrivée prévue. / EN: Planned arrival time.
        depart (datetime) : FR: Heure de départ prévue. / EN: Planned departure time.
        en_attente (bool) : FR: Indique si le train est en attente de placement. / EN: Waiting for placement.
        debut_attente (datetime) : FR: Heure de début d'attente. / EN: Start of waiting time.
        fin_attente (datetime) : FR: Heure de fin d'attente (si applicable). / EN: End of waiting time (if applicable).
        voie (int) : FR: Index de la voie attribuée. / EN: Assigned track index.
        electrique (bool) : FR: Indique si le train est électrique. / EN: Is the train electric.
        depot (str) : FR: Nom du dépôt d'origine. / EN: Depot name.
        type (str) : FR: Type de train ("Storage", "testing", "pit", etc.). / EN: Train type.
        locomotive_cote (str) : FR: Côté de la locomotive (optionnel). / EN: Locomotive side (optional).
        type_wagon (str) : FR: Type de wagon (optionnel). / EN: Wagon type (optional).
    """
    def __init__(self, id, nom, wagons, locomotives, arrivee, depart, depot, type="Storage"):
        """
        FR: Initialise un train.
        EN: Initialize a train.

        Args:
            id: FR: Identifiant unique du train. / EN: Unique train identifier.
            nom: FR: Nom du train. / EN: Train name.
            wagons: FR: Nombre de wagons. / EN: Number of wagons.
            locomotives: FR: Nombre de locomotives. / EN: Number of locomotives.
            arrivee: FR: Heure d'arrivée. / EN: Arrival time.
            depart: FR: Heure de départ. / EN: Departure time.
            depot: FR: Dépôt d'origine. / EN: Depot name.
            type: FR: Type de train (par défaut "Storage"). / EN: Train type (default "Storage").
        """
        self.id = id
        self.nom = nom
        self.wagons = wagons
        self.locomotives = locomotives
        self.longueur = self.calculer_longueur()  # FR: Calcul automatique de la longueur / EN: Auto-calculate length
        self.arrivee = arrivee
        self.depart = depart
        self.en_attente = False
        self.debut_attente = None
        self.fin_attente = None
        self.voie = None
        self.electrique = False  # FR: Par défaut / EN: Default
        self.depot = depot
        self.type = type
        self.locomotive_cote = None
        self.type_wagon = None

    def calculer_longueur(self):
        """
        FR: Calcule la longueur totale du train en fonction des wagons et des locomotives.
        EN: Compute total train length based on wagons and locomotives.

        Returns:
            int: FR: Longueur totale du train (en mètres). / EN: Total train length (meters).
        """
        longueur_wagon = 14  # FR: Longueur d'un wagon en mètres / EN: Wagon length in meters
        longueur_locomotive = 19  # FR: Longueur d'une locomotive en mètres / EN: Locomotive length in meters
        return self.wagons * longueur_wagon + self.locomotives * longueur_locomotive

class Simulation:
    """
    FR: Gère l'ensemble de la simulation ferroviaire.
    EN: Manages the entire railway simulation.

    FR: Stocke les trains, les occupations de voies, les longueurs de voies, etc.
    EN: Stores trains, track occupations, track lengths, etc.
    FR: Permet d'ajouter, de recalculer, de transférer ou de réinitialiser les trains et occupations.
    EN: Allows adding, recalculating, transferring, or resetting trains and occupations.
    """

    def __init__(self, depots_config=None):
        """
        FR: Initialise la simulation avec une structure multi-dépôts.
        EN: Initialize the simulation with a multi-depot structure.

        depots_config : 
            FR: Dictionnaire de configuration des dépôts.
            EN: Depot configuration dictionary.
        """
        if depots_config is None:
            depots_config = {
                "Glostrup": {"numeros_voies": [7,8,9,11], "longueurs_voies": [290,340,400,300], "lat": 55.662194, "lon": 12.393508},
                "Naestved": {"numeros_voies": [1,2,3,4], "longueurs_voies": [250,300,350,280], "lat": 55.194538, "lon": 11.822616},
                "Taulov": {"numeros_voies": [21], "longueurs_voies": [280], "lat": 55.546012, "lon": 9.632929},
                "KAC": {"numeros_voies": [22], "longueurs_voies": [280], "lat": 55.624757, "lon": 12.680361},
                "Helgoland": {"numeros_voies": [23], "longueurs_voies": [280], "lat": 55.714857, "lon": 12.582771},
                "Padborg": {"numeros_voies": [24], "longueurs_voies": [280], "lat": 54.824899, "lon": 9.357716},
                "Langenfelde": {"numeros_voies": [25], "longueurs_voies": [280], "lat": 53.581551, "lon": 9.924246},
            }
        self.depots = {}
        for nom, conf in depots_config.items():
            self.depots[nom] = {
                "numeros_voies": conf["numeros_voies"],
                "longueurs_voies": conf["longueurs_voies"],
                "occupation": [],  # FR: Liste des tuples (voie_idx, debut, fin, train) / EN: List of tuples (track_idx, start, end, train)
                "lat": conf.get("lat"),
                "lon": conf.get("lon"),
            }

        self.trains = []  # FR: Liste de tous les trains / EN: List of all trains
        self.delai_securite = 10  # FR: Délai de sécurité en minutes / EN: Safety margin in minutes
        self.historique = []  # FR: Liste des actions (ajout, suppression, modification) / EN: List of actions (add, remove, modify)
        
    # --- Propriétés pratiques pour accès rapide aux données des dépôts ---
    # --- Handy properties for quick depot data access ---
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
    # --- Dynamically add a depot ---
    def ajouter_depot(self, nom, numeros_voies, longueurs_voies):
       if nom in self.depots:
           return "Ce dépôt existe déjà."  # FR: Le dépôt existe déjà / EN: Depot already exists
       self.depots[nom] = {
           "numeros_voies": numeros_voies,
           "longueurs_voies": longueurs_voies,
           "occupation": []
       }

    def ajouter_train(self, train, depot, optimiser=False, ajouter_a_liste=True):
        """
        FR: Tente d'ajouter un train dans le dépôt spécifié, en respectant les contraintes de longueur,
        de conflits d’occupation et de priorité pour les trains électriques.
        EN: Try to add a train to the specified depot, respecting length, occupation conflicts, and electric train priority.

        Args:
            train (Train): FR: Le train à ajouter. / EN: Train to add.
            depot (str): FR: "Glostrup" ou "Naestved". / EN: "Glostrup" or "Naestved".
            optimiser (bool): FR: Si True, cherche le meilleur créneau possible. / EN: If True, search for best slot.
            ajouter_a_liste (bool): FR: Si True, ajoute le train à self.trains. / EN: If True, add train to self.trains.

        Returns:
            str|None: FR: Message d'erreur si échec, sinon None. / EN: Error message if failed, else None.
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

        # FR: Priorité pour la voie 9 si le train est électrique
        # EN: Priority for track 9 if the train is electric
        if train.electrique and 9 in numeros_voies:
            voie9_idx = numeros_voies.index(9)
            if longueurs_voies[voie9_idx] >= train.longueur:
                # FR: Chercher la première disponibilité sur la voie 9
                # EN: Find first availability on track 9
                debut_possible = train.arrivee
                while True:
                    conflit = verifier_conflit(voie9_idx, debut_possible, train.depart, occupation, self.delai_securite)
                    if not conflit:
                        break
                    # FR: Décaler le début à la fin du conflit + délai de sécurité
                    # EN: Shift start to end of conflict + safety margin
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

        # FR: Sinon, chercher la meilleure voie et le meilleur créneau
        # EN: Otherwise, find the best track and slot
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
        # FR: Si aucune voie n'est disponible du tout
        # EN: If no track is available at all
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
        FR: Gère le placement d'un train électrique sur la voie 9 (Glostrup).
        EN: Handle placement of an electric train on track 9 (Glostrup).

        Args:
            train (Train): FR: Le train à placer. / EN: Train to place.
            occupation (list): FR: Occupations actuelles. / EN: Current occupations.
            numeros_voies (list): FR: Numéros des voies. / EN: Track numbers.
            longueurs_voies (list): FR: Longueurs des voies. / EN: Track lengths.

        Returns:
            bool: FR: True si placement réussi, False sinon. / EN: True if placed, False otherwise.
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
        FR: Cherche la meilleure voie disponible pour placer le train.
        EN: Find the best available track to place the train.

        Args:
            train (Train): FR: Le train à placer. / EN: Train to place.
            ref (datetime): FR: Heure de référence pour le placement. / EN: Reference time for placement.
            occupation (list): FR: Occupations actuelles. / EN: Current occupations.
            longueurs_voies (list): FR: Longueurs des voies. / EN: Track lengths.
            optimiser (bool): FR: Si True, cherche le meilleur créneau. / EN: If True, search for best slot.

        Returns:
            tuple: (index_voie, heure_debut) ou (None, None) si aucune voie.
            tuple: (track_index, start_time) or (None, None) if no track.
        """
        occupation_par_voie = {i: [] for i in range(len(longueurs_voies))}
        for v, occ_debut, occ_fin, _ in occupation:
            occupation_par_voie[v].append((occ_debut, occ_fin))
            
        for voie, occs in occupation_par_voie.items():
            occupation_par_voie[voie] = sorted(occs, key=lambda x: x[0])  # FR: Tri par heure de début / EN: Sort by start time
    
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
        FR: Réinitialise la simulation : efface toutes les occupations et tous les trains.
        EN: Reset the simulation: clear all occupations and trains.
        """
        for depot in self.depots.values():
            depot["occupation"].clear()
        self.trains.clear()

    def recalculer(self, optimiser=False):
        """
        FR: Recalcule les occupations des voies après une modification ou suppression de train.
        EN: Recalculate track occupations after a train modification or removal.
        FR: Les trains restent dans leur dépôt d'origine et les duplications sont évitées.
        EN: Trains remain in their original depot and duplications are avoided.

        Args:
            optimiser (bool): FR: Si True, cherche le meilleur créneau possible. / EN: If True, search for best slot.
        """
        # FR: Réinitialiser les occupations / EN: Reset occupations
        for depot in self.depots.values():
            depot["occupation"].clear()

        # FR: Réinitialiser les voies des trains / EN: Reset train tracks
        for train in self.trains:
            train.voie = None
            train.en_attente = False
            train.debut_attente = train.arrivee
            train.fin_attente = None

        # FR: Replacer les trains dans chaque dépôt / EN: Re-place trains in each depot
        for depot_nom in self.depots:
            trains_depot = [train for train in self.trains if train.depot == depot_nom]
            # FR: Priorité aux trains électriques sur la voie 9 si elle existe / EN: Priority to electric trains on track 9 if exists
            trains_elec = [t for t in trains_depot if t.electrique and 9 in self.depots[depot_nom]["numeros_voies"]]
            for train in sorted(trains_elec, key=lambda t: t.arrivee):
                self.ajouter_train_sans_ajout_liste(train, depot_nom, optimiser=optimiser, priorite_voie_9=True)
            # FR: Les autres trains / EN: Other trains
            autres_trains = [t for t in trains_depot if not (t.electrique and 9 in self.depots[depot_nom]["numeros_voies"])]
            for train in sorted(autres_trains, key=lambda t: t.arrivee):
                self.ajouter_train_sans_ajout_liste(train, depot_nom, optimiser=optimiser)
    
        print(f"Occupation Glostrup après recalcul : {self.occupation_a}")
        print(f"Occupation Naestved après recalcul : {self.occupation_b}")
        print(f"Trains après recalcul : {[t.nom for t in self.trains]}")

    def ajouter_train_sans_ajout_liste(self, train, depot, optimiser=False, priorite_voie_9=False):
        """
        FR: Ajoute un train à une voie sans l'ajouter à la liste self.trains.
        EN: Add a train to a track without adding it to self.trains.
        FR: Utilisé uniquement pour recalculer les occupations.
        EN: Used only to recalculate occupations.

        Args:
            train (Train): FR: Le train à placer. / EN: Train to place.
            depot (str): FR: "Glostrup" ou "Naestved". / EN: "Glostrup" or "Naestved".
            optimiser (bool): FR: Si True, cherche le meilleur créneau. / EN: If True, search for best slot.
            priorite_voie_9 (bool): FR: Si True, tente la voie 9 en priorité. / EN: If True, try track 9 first.
        """
        depot_data = self.depots[depot]
        occupation = depot_data["occupation"]
        numeros_voies = depot_data["numeros_voies"]
        longueurs_voies = depot_data["longueurs_voies"]
    
        # FR: Priorité pour la voie 9 si spécifié / EN: Priority for track 9 if specified
        if priorite_voie_9 and 9 in numeros_voies:
            voie9_idx = numeros_voies.index(9)
            if longueurs_voies[voie9_idx] >= train.longueur:
                if not verifier_conflit(voie9_idx, train.arrivee, train.depart, occupation, self.delai_securite):
                    train.voie = voie9_idx
                    train.fin_attente = train.arrivee
                    occupation.append((voie9_idx, train.arrivee, train.depart, train))
                    return
    
        # FR: Sinon, chercher une autre voie disponible / EN: Otherwise, find another available track
        meilleure_voie, meilleur_debut = self.chercher_voie_disponible(train, train.arrivee, occupation, longueurs_voies, optimiser)
        if meilleure_voie is not None:
            train.voie = meilleure_voie
            train.fin_attente = meilleur_debut
            occupation.append((meilleure_voie, meilleur_debut, train.depart, train))
        else:
            train.en_attente = True

    def ajouter_train_multi_depot(self, train, optimiser=False):
        """
        FR: Essaye d'abord dans le dépôt d'origine, puis dans les autres dépôts si besoin.
        EN: Try first in the original depot, then in other depots if needed.
        """
        erreur = self.ajouter_train(train, train.depot, optimiser=optimiser)
        if not erreur:
            return None
        # FR: Sinon, tente dans les autres dépôts / EN: Otherwise, try in other depots
        for depot in self.depots:
            if depot != train.depot:
                erreur2 = self.ajouter_train(train, depot, optimiser=optimiser)
                if not erreur2:
                    train.depot = depot
                    return None
        return "Aucun dépôt ne peut accueillir ce train."

    def undo(self):
        """
        FR: Annule la dernière action (ajout, suppression, modification).
        EN: Undo the last action (add, remove, modify).
        """
        if not self.historique:
            return "Aucune action à annuler."
        last = self.historique.pop()
        if last["action"] == "ajout":
            # FR: Supprimer le train ajouté / EN: Remove the added train
            self.trains = [t for t in self.trains if t.id != last["train_id"]]
        elif last["action"] == "suppression":
            # FR: Restaurer le train supprimé / EN: Restore the removed train
            from copy import deepcopy
            train = Train(**{k: v for k, v in last["etat_avant"].items() if k in Train.__init__.__code__.co_varnames})
            for k, v in last["etat_avant"].items():
                setattr(train, k, v)
            self.trains.append(train)
        elif last["action"] == "modification":
            # FR: Restaurer l'état avant modification / EN: Restore state before modification
            train = next((t for t in self.trains if t.id == last["train_id"]), None)
            if train:
                for k, v in last["etat_avant"].items():
                    setattr(train, k, v)
        self.recalculer()
        return None