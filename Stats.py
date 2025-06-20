# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:59:53 2025

@author: andre
"""
from datetime import timedelta
from Traduction import t, get_translation

def calculer_temps_attente(train):
    """
    FR : Calcule le temps d'attente d'un train en minutes.
    EN : Compute the waiting time of a train in minutes.
    """
    if train.fin_attente and train.debut_attente:
        return max(0, (train.fin_attente - train.debut_attente).total_seconds() / 60)
    return 0

def calculer_temps_moyen_attente(trains):
    """
    FR : Calcule le temps moyen d'attente des trains.
    EN : Compute the average waiting time of all trains.
    """
    if not trains:
        return 0
    total_attente = sum(calculer_temps_attente(train) for train in trains)
    return round(total_attente / len(trains), 2)

def calculer_taux_occupation(occupation, numeros_voies):
    """
    FR : Calcule le taux d'occupation des voies.
    EN : Compute the track occupation rate.
    Args:
        FR : occupation: Liste des tuples (voie, début, fin, train)
        EN : occupation: List of tuples (track, start, end, train)
        numeros_voies: 
            FR : Liste des numéros de voies 
            EN : List of track numbers
    Returns:
        FR : Pourcentage d'occupation des voies  
        EN : Percentage of track occupation
    """
    if not occupation:
        return 0

    # Durée totale de la période considérée (en minutes)
    # Total duration of the considered period (in minutes)
    duree_totale = (max(fin for _, _, fin, _ in occupation) - min(debut for _, debut, _, _ in occupation)).total_seconds() / 60
    # Somme des durées d'occupation de toutes les voies (en minutes)
    # Sum of all occupation durations (in minutes)
    duree_occupee = sum((fin - debut).total_seconds() / 60 for _, debut, fin, _ in occupation)
    nb_voies = len(numeros_voies)

    return round((duree_occupee / (duree_totale * nb_voies)) * 100, 2)

def calculer_statistiques_globales(simulation):
    """
    FR : Calcule les statistiques globales pour la simulation.
    EN : Compute global statistics for the simulation.
    Args:
        simulation: 
            FR : Objet Simulation
            EN : Simulation object
    Returns:
        FR : Dictionnaire des statistiques
        EN : Dictionary of statistics
    """
    trains = simulation.trains
    depots = simulation.depots.keys()
    stats_par_depot = {}
    for depot in depots:
        trains_depot = [train for train in trains if train.depot == depot]
        stats_par_depot[depot] = {
            "trains": len(trains_depot),
            "taux_occupation": calculer_taux_occupation(
                simulation.depots[depot]["occupation"],
                simulation.depots[depot]["numeros_voies"]
            )
        }
    trains_electriques = [train for train in trains if train.electrique]
    temps_moyen_attente = calculer_temps_moyen_attente(trains)
    # Taux d'occupation global
    all_occupations = []
    all_voies = []
    for depot in depots:
        all_occupations += simulation.depots[depot]["occupation"]
        all_voies += simulation.depots[depot]["numeros_voies"]
    taux_occupation_global = calculer_taux_occupation(all_occupations, all_voies)

    return {
        "total_trains": len(trains),  # Nombre total de trains / Total number of trains
        "trains_electriques": len(trains_electriques),  # Trains électriques / Electric trains
        "temps_moyen_attente": temps_moyen_attente,  # Temps moyen d'attente / Average waiting time
        "taux_occupation_global": taux_occupation_global,  # Taux d'occupation global / Global occupation rate
        "stats_par_depot": stats_par_depot
    }

def calculer_requirements(trains, t, lang):
    """
    FR : Calcule les besoins en ressources pour les trains de type Testing, par dépôt.
    EN : Compute resource requirements for 'Testing' trains, by depot.
    """
    requirements = {
        "test_drivers": 0,
        "locomotives": 0,
        "details": [],  # Détails par train
        "by_depot": {}  # Nouveau : besoins par dépôt
    }

    for train in trains:
        if train.type == "testing":
            requirements["test_drivers"] += 1
            requirements["locomotives"] += 2
            requirements["details"].append({
                "train_name": train.nom,
                "start_time": train.arrivee,
                "end_time": train.depart,
                "depot": train.depot
            })
            # Ajout par dépôt
            if train.depot not in requirements["by_depot"]:
                requirements["by_depot"][train.depot] = {"test_drivers": 0, "locomotives": 0, "trains": []}
            requirements["by_depot"][train.depot]["test_drivers"] += 1
            requirements["by_depot"][train.depot]["locomotives"] += 2
            requirements["by_depot"][train.depot]["trains"].append(train.nom)
    return requirements

def regrouper_requirements_par_jour(trains, t, lang):
    """
    FR : Regroupe les besoins en ressources par jour, en tenant compte des trains qui s'étendent sur plusieurs jours.
    EN : Group resource requirements per day, considering trains spanning several days.
    Args:
        trains: Liste des trains / List of trains
        t: Fonction de traduction / Translation function
        lang: Langue / Language
    Returns:
        FR : Dictionnaire avec les besoins par jour, incluant les détails des trains.
        EN : Dictionary with requirements per day, including train details.
    """
    requirements_par_jour = {}

    for train in trains:
        if train.type == "testing":
            jour_courant = train.arrivee.date()
            dernier_jour = train.depart.date()

            # Boucle sur chaque jour couvert par le train
            # Loop over each day covered by the train
            while jour_courant <= dernier_jour:
                if jour_courant not in requirements_par_jour:
                    requirements_par_jour[jour_courant] = {
                        "test_drivers": 0,
                        "locomotives": 0,
                        "details": []
                    }
                requirements_par_jour[jour_courant]["test_drivers"] += 1
                requirements_par_jour[jour_courant]["locomotives"] += 2
                # Ajoute le détail du train pour ce jour / Add train detail for this day
                requirements_par_jour[jour_courant]["details"].append({
                    "train_name": train.nom,
                    "start_time": train.arrivee.strftime("%H:%M") if train.arrivee.date() == jour_courant else "--:--",
                    "end_time": train.depart.strftime("%H:%M") if train.depart.date() == jour_courant else "--:--"
                })
                jour_courant += timedelta(days=1)

    # Supprimer les jours sans besoins réels (au cas où)
    # Remove days without actual requirements (just in case)
    requirements_par_jour = {
        jour: besoins for jour, besoins in requirements_par_jour.items()
        if besoins["test_drivers"] > 0 or besoins["locomotives"] > 0
    }

    return requirements_par_jour