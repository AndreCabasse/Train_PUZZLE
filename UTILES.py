# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:54:24 2025

@author: andre
"""
from datetime import timedelta

def formater_horaire(horaire):
    """
    Formate un horaire datetime en chaîne lisible.

    Args:
        horaire: Objet datetime.

    Returns:
        Chaîne formatée (str).
    """
    return horaire.strftime("%Y-%m-%d %H:%M")


def verifier_conflit(voie, debut, fin, occupation, delai_securite):
    """
    Vérifie s'il y a un conflit d'occupation pour une voie donnée.

    Args:
        voie: Numéro de la voie.
        debut: Heure de début de l'occupation.
        fin: Heure de fin de l'occupation.
        occupation: Liste des occupations actuelles.
        delai_securite: Délai de sécurité en minutes.

    Returns:
        Booléen indiquant s'il y a un conflit (True) ou non (False).
    """
    for v, occ_debut, occ_fin, _ in occupation:
        if v == voie and (debut - timedelta(minutes=delai_securite) < occ_fin and fin + timedelta(minutes=delai_securite) > occ_debut):
            print(f"Conflit détecté sur la voie {voie} entre {debut} et {fin} avec {occ_debut} - {occ_fin}")
            return True
    return False


def trouver_prochaine_disponibilite(voie, ref, occupation, delai_securite):
    """
    Trouve la prochaine disponibilité pour une voie donnée.

    Args:
        voie: Numéro de la voie.
        ref: Heure de référence pour commencer la recherche.
        occupation: Liste des occupations actuelles.
        delai_securite: Délai de sécurité en minutes.

    Returns:
        Heure de début disponible (datetime).
    """
    debut = ref
    while True:
        conflit = verifier_conflit(voie, debut, debut + timedelta(minutes=1), occupation, delai_securite)
        if not conflit:
            return debut
        debut += timedelta(minutes=1)


def convertir_minutes_en_hhmm(minutes):
    """
    Convertit un nombre de minutes en format HH:MM.

    Args:
        minutes: Nombre de minutes (int).

    Returns:
        Chaîne formatée en HH:MM (str).
    """
    heures = minutes // 60
    minutes_restantes = minutes % 60
    return f"{heures:02}:{minutes_restantes:02}"