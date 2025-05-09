# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:54:23 2025

@author: andre
"""

from datetime import datetime, timedelta
from UTILES import verifier_conflit

class Train:
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
        self.depot = depot  # Nouveau champ pour stocker le dépôt
        self.type = type  # Nouveau champ pour le type de train
        self.locomotive_cote = None  # Côté de la locomotive (gauche ou droite)
        self.type_wagon = None  # Nouveau champ pour le type de wagon

    def calculer_longueur(self):
        """
        Calcule la longueur totale du train en fonction des wagons et des locomotives.

        Returns:
            Longueur totale du train (en mètres).
        """
        longueur_wagon = 14  # Longueur d'un wagon en mètres
        longueur_locomotive = 19  # Longueur d'une locomotive en mètres
        return self.wagons * longueur_wagon + self.locomotives * longueur_locomotive

class Simulation:
    def __init__(self, longueurs_voies_a=None, longueurs_voies_b=None):
        # Dépôt A
        self.numeros_voies_a = [7, 8, 9, 11]
        self.longueurs_voies_a = longueurs_voies_a or [290, 340, 400, 300]
        self.occupation_a = []

        # Dépôt B
        self.numeros_voies_b = [1, 2, 3, 4]
        self.longueurs_voies_b = longueurs_voies_b or [250, 300, 350, 280]
        self.occupation_b = []

        self.trains = []
        self.delai_securite = 10

    def ajouter_train(self, train, depot, optimiser=False, ajouter_a_liste=True):
        if train.arrivee >= train.depart:
            return "L'heure d'arrivée doit être antérieure à l'heure de départ."
        if train.longueur <= 0:
            return "La longueur du train doit être positive."
    
        train.en_attente = False
        train.debut_attente = train.arrivee
    
        if depot == "Glostrup":
            occupation = self.occupation_a
            numeros_voies = self.numeros_voies_a
            longueurs_voies = self.longueurs_voies_a
        else:
            occupation = self.occupation_b
            numeros_voies = self.numeros_voies_b
            longueurs_voies = self.longueurs_voies_b
    
        # Priorité pour la voie 9 si le train est électrique
        if train.electrique and 9 in numeros_voies:
            voie9_idx = numeros_voies.index(9)
            if longueurs_voies[voie9_idx] >= train.longueur:
                if not verifier_conflit(voie9_idx, train.arrivee, train.depart, occupation, self.delai_securite):
                    train.voie = voie9_idx
                    train.fin_attente = train.arrivee
                    occupation.append((voie9_idx, train.arrivee, train.depart, train))
                    if ajouter_a_liste:
                        self.trains.append(train)
                        self.trains.sort(key=lambda t: t.arrivee)
                    return
    
        # Si la voie 9 n'est pas disponible ou le train n'est pas électrique, chercher une autre voie
        meilleure_voie, meilleur_debut = self.chercher_voie_disponible(
            train, train.arrivee, occupation, longueurs_voies, optimiser
        )
        if meilleure_voie is not None:
            train.voie = meilleure_voie
            train.fin_attente = meilleur_debut
            occupation.append((meilleure_voie, meilleur_debut, train.depart, train))
        else:
            train.en_attente = True
    
        if ajouter_a_liste:
            self.trains.append(train)
            self.trains.sort(key=lambda t: t.arrivee)
            self.recalculer()  # Recalculer les occupations après ajout

    def gerer_voie_9(self, train, occupation, numeros_voies, longueurs_voies):
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
        self.occupation_a.clear()
        self.occupation_b.clear()
        self.trains.clear()

    def recalculer(self, optimiser=False):
        """
    Recalcule les occupations des voies après une modification ou suppression de train.
    Les trains restent dans leur dépôt d'origine et les duplications sont évitées.
    """
        # Réinitialiser les occupations
        self.occupation_a.clear()
        self.occupation_b.clear()

        # Réinitialiser les voies des trains
        for train in self.trains:
            train.voie = None
            train.en_attente = False
            train.debut_attente = train.arrivee
            train.fin_attente = None

        # Replacer les trains électriques en priorité sur la voie 9 du dépôt Glostrup
        trains_a_electriques = [train for train in self.trains if train.depot == "Glostrup" and train.electrique]
        for train in sorted(trains_a_electriques, key=lambda t: t.arrivee):
            self.ajouter_train_sans_ajout_liste(train, "Glostrup", optimiser=optimiser, priorite_voie_9=True)

        # Replacer les autres trains du dépôt Glostrup
        trains_a = [train for train in self.trains if train.depot == "Glostrup" and not train.electrique]
        for train in sorted(trains_a, key=lambda t: t.arrivee):
            self.ajouter_train_sans_ajout_liste(train, "Glostrup", optimiser=optimiser)

        # Replacer les trains dans le dépôt Naestved
        trains_b = [train for train in self.trains if train.depot == "Naestved"]
        for train in sorted(trains_b, key=lambda t: t.arrivee):
            self.ajouter_train_sans_ajout_liste(train, "Naestved", optimiser=optimiser)
    
        print(f"Occupation Glostrup après recalcul : {self.occupation_a}")
        print(f"Occupation Naestved après recalcul : {self.occupation_b}")
        print(f"Trains après recalcul : {[t.nom for t in self.trains]}")

    def ajouter_train_sans_ajout_liste(self, train, depot, optimiser=False, priorite_voie_9=False):
        """
    Ajoute un train à une voie sans l'ajouter à la liste self.trains.
    Utilisé uniquement pour recalculer les occupations.
    """
        if depot == "Glostrup":
            occupation = self.occupation_a
            numeros_voies = self.numeros_voies_a
            longueurs_voies = self.longueurs_voies_a
        else:
            occupation = self.occupation_b
            numeros_voies = self.numeros_voies_b
            longueurs_voies = self.longueurs_voies_b
    
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
            
    def transferer_train(self, train, depot_source, depot_cible, optimiser=False):
        """
    Transfère un train d'un dépôt à un autre si possible.
    """
        # Retirer le train des occupations du dépôt source
        if depot_source == "Glostrup":
            self.occupation_a = [entry for entry in self.occupation_a if entry[3].id != train.id]
        else:
            self.occupation_b = [entry for entry in self.occupation_b if entry[3].id != train.id]

        # Essayer d'ajouter le train au dépôt cible
        erreur = self.ajouter_train(train, depot_cible, optimiser=optimiser)
        if erreur:
           # Si le transfert échoue, remettre le train dans le dépôt source
           self.ajouter_train(train, depot_source, optimiser=optimiser)
           return False
        else:
           # Mettre à jour le dépôt du train
           train.depot = depot_cible
           return True