# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:59:53 2025

@author: andre
"""
from datetime import timedelta
from Traduction import t, get_translation

def calculer_temps_attente(train):
    """Calcule le temps d'attente d'un train en minutes."""
    if train.en_attente and train.fin_attente and train.debut_attente:
        return (train.fin_attente - train.debut_attente).total_seconds() / 60
    return 0

def calculer_temps_moyen_attente(trains):
    """Calcule le temps moyen d'attente des trains."""
    trains_en_attente = [train for train in trains if train.en_attente]
    if not trains_en_attente:
        return 0
    total_attente = sum(calculer_temps_attente(train) for train in trains_en_attente)
    return round(total_attente / len(trains_en_attente), 2)

def calculer_taux_occupation(occupation, numeros_voies):
    """Calcule le taux d'occupation des voies."""
    if not occupation:
        return 0

    duree_totale = (max(fin for _, _, fin, _ in occupation) - min(debut for _, debut, _, _ in occupation)).total_seconds() / 60
    duree_occupee = sum((fin - debut).total_seconds() / 60 for _, debut, fin, _ in occupation)
    nb_voies = len(numeros_voies)

    return round((duree_occupee / (duree_totale * nb_voies)) * 100, 2)

def calculer_statistiques_globales(simulation):
    """Calcule les statistiques globales pour la simulation."""
    trains = simulation.trains
    trains_glostrup = [train for train in trains if train.depot == "Glostrup"]
    trains_naestved = [train for train in trains if train.depot == "Naestved"]
    trains_electriques = [train for train in trains if train.electrique]

    temps_moyen_attente = calculer_temps_moyen_attente(trains)
    taux_occupation_glostrup = calculer_taux_occupation(simulation.occupation_a, simulation.numeros_voies_a)
    taux_occupation_naestved = calculer_taux_occupation(simulation.occupation_b, simulation.numeros_voies_b)
    taux_occupation_global = calculer_taux_occupation(simulation.occupation_a + simulation.occupation_b, simulation.numeros_voies_a + simulation.numeros_voies_b)

    return {
        "total_trains": len(trains),
        "trains_glostrup": len(trains_glostrup),
        "trains_naestved": len(trains_naestved),
        "trains_electriques": len(trains_electriques),
        "temps_moyen_attente": temps_moyen_attente,
        "taux_occupation_global": taux_occupation_global,
        "taux_occupation_glostrup": taux_occupation_glostrup,
        "taux_occupation_naestved": taux_occupation_naestved,
    }

def calculer_requirements(trains, t):
    """
    Calcule les besoins en ressources pour les trains de type Testing.

    Args:
        trains: Liste des trains.
        t: Fonction de traduction.

    Returns:
        Dictionnaire contenant les besoins en "test drivers" et locomotives.
    """
    requirements = {
        "test_drivers": 0,
        "locomotives": 0,
        "details": []  # Détails par train
    }

    for train in trains:
        if train.type == t("testing"):  # Comparer avec la traduction du type
            requirements["test_drivers"] += 1
            requirements["locomotives"] += 2
            requirements["details"].append({
                "train_name": train.nom,
                "start_time": train.arrivee,
                "end_time": train.depart
            })

    return requirements

def regrouper_requirements_par_jour(trains, t):
    """
    Regroupe les besoins en ressources par jour, en tenant compte des trains qui s'étendent sur plusieurs jours.

    Args:
        trains: Liste des trains.
        t: Fonction de traduction.

    Returns:
        Dictionnaire avec les besoins par jour.
    """
    requirements_par_jour = {}

    for train in trains:
        if train.type == t("testing"):
            # Calculer tous les jours entre l'arrivée et le départ
            jour_courant = train.arrivee.date()
            dernier_jour = train.depart.date()

            while jour_courant <= dernier_jour:
                if jour_courant not in requirements_par_jour:
                    requirements_par_jour[jour_courant] = {"test_drivers": 0, "locomotives": 0}
                requirements_par_jour[jour_courant]["test_drivers"] += 1
                requirements_par_jour[jour_courant]["locomotives"] += 2
                jour_courant += timedelta(days=1)

    # Supprimer les jours sans besoins réels (au cas où)
    requirements_par_jour = {jour: besoins for jour, besoins in requirements_par_jour.items() if besoins["test_drivers"] > 0 or besoins["locomotives"] > 0}

    return requirements_par_jour