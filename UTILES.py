# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:54:24 2025

@author: andre
"""
from datetime import timedelta

def formater_horaire(horaire):
    """
    FR: Formate un horaire datetime en chaîne lisible.
    EN: Format a datetime object into a readable string.

    Args:
        horaire: 
            FR: Objet datetime.
            EN: Datetime object.

    Returns:
        FR: Chaîne formatée (str).
        EN: Formatted string.
    """
    return horaire.strftime("%Y-%m-%d %H:%M")


def verifier_conflit(voie, debut, fin, occupation, delai_securite):
    """
    FR: Vérifie s'il y a un conflit d'occupation pour une voie donnée.
    EN: Check if there is an occupation conflict for a given track.

    Args:
        voie: 
            FR: Numéro de la voie.
            EN: Track number.
        debut: 
            FR: Heure de début de l'occupation.
            EN: Start time of the occupation.
        fin: 
            FR: Heure de fin de l'occupation.
            EN: End time of the occupation.
        occupation: 
            FR: Liste des occupations actuelles.
            EN: List of current occupations.
        delai_securite: 
            FR: Délai de sécurité en minutes.
            EN: Safety margin in minutes.

    Returns:
        FR: Booléen indiquant s'il y a un conflit (True) ou non (False).
        EN: Boolean indicating if there is a conflict (True) or not (False).
    """
    for v, occ_debut, occ_fin, _ in occupation:
        # FR: Vérifie si la voie est la même et si les périodes se chevauchent en tenant compte du délai de sécurité.
        # EN: Check if the track is the same and if the periods overlap, considering the safety margin.
        if v == voie and (debut - timedelta(minutes=delai_securite) < occ_fin and fin + timedelta(minutes=delai_securite) > occ_debut):
            print(f"Conflit détecté sur la voie {voie} entre {debut} et {fin} avec {occ_debut} - {occ_fin}")  # FR: Affiche le conflit / EN: Print the conflict
            return True
    return False


def trouver_prochaine_disponibilite(voie, ref, occupation, delai_securite):
    """
    FR: Trouve la prochaine disponibilité pour une voie donnée.
    EN: Find the next available time for a given track.

    Args:
        voie: 
            FR: Numéro de la voie.
            EN: Track number.
        ref: 
            FR: Heure de référence pour commencer la recherche.
            EN: Reference time to start searching.
        occupation: 
            FR: Liste des occupations actuelles.
            EN: List of current occupations.
        delai_securite: 
            FR: Délai de sécurité en minutes.
            EN: Safety margin in minutes.

    Returns:
        FR: Heure de début disponible (datetime).
        EN: Available start time (datetime).
    """
    debut = ref
    while True:
        # FR: Vérifie s'il y a un conflit à ce créneau.
        # EN: Check if there is a conflict at this slot.
        conflit = verifier_conflit(voie, debut, debut + timedelta(minutes=1), occupation, delai_securite)
        if not conflit:
            return debut
        debut += timedelta(minutes=1)


def convertir_minutes_en_hhmm(minutes):
    """
    FR: Convertit un nombre de minutes en format HH:MM.
    EN: Convert a number of minutes into HH:MM format.

    Args:
        minutes: 
            FR: Nombre de minutes (int).
            EN: Number of minutes (int).

    Returns:
        FR: Chaîne formatée en HH:MM (str).
        EN: Formatted string in HH:MM.
    """
    heures = minutes // 60
    minutes_restantes = minutes % 60
    return f"{heures:02}:{minutes_restantes:02}"