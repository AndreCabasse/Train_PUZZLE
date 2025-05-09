# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:54:23 2025

@author: andre
"""

def get_translation(lang):
    return {
        "title": {"fr": "Simulation d'occupation des voies","en": "Track Occupancy Simulation","da": "Sporbesættelsessimulering"},
        "add_train": {"fr": "Ajouter un train", "en": "Add a train", "da": "Tilføj et tog"},
        "Time": {"fr": "Temps", "en": "Time", "da": "Tid"},
        "train_name": {"fr": "Nom du train", "en": "Train name", "da": "Tog navn"},
        "Track": {"fr": "Voie", "en": "Track", "da": "Togbane"},
        "base_date": {"fr": "Date de base", "en": "Base date", "da": "Grunddato"},
        "base_time": {"fr": "Heure de base", "en": "Base time", "da": "Grundtid"},
        "arrival_date": {"fr": "Date d'arrivée", "en": "Arrival date", "da": "Ankomstdato"},
        "arrival_time": {"fr": "Heure d'arrivée", "en": "Arrival time", "da": "Ankomsttid"},
        "departure_date": {"fr": "Date de départ", "en": "Departure date", "da": "Afgangsdato"},
        "departure_time": {"fr": "Heure de départ", "en": "Departure time", "da": "Afgangstid"},
        "length": {"fr": "Longueur (m)", "en": "Length (m)", "da": "Længde (m)"},
        "optimize": {"fr": "Optimiser le placement", "en": "Optimize placement", "da": "Optimer placering"},
        "submit_train": {"fr": "Ajouter le train", "en": "Add train", "da": "Tilføj tog"},
        "train_list": {"fr": "Liste des trains", "en": "Train list", "da": "Togliste"},
        "waiting_trains": {"fr": "Trains en attente", "en": "Waiting trains", "da": "Ventende tog"},
        "average_wait": {"fr": "Temps moyen d'attente", "en": "Average waiting time", "da": "Gennemsnitlig ventetid"},
        "occupancy_rate": {"fr": "Taux d'occupation", "en": "Occupancy rate", "da": "Belægningsgrad"},
        "remove": {"fr": "Supprimer", "en": "Delete", "da": "Slet"},
        "reset": {"fr": "Réinitialiser la simulation", "en": "Reset simulation", "da": "Nulstil simulering"},
        "waiting": {"fr": "Trains en attente", "en": "Trains waiting", "da": "Ventende tog"},
        "avg_waiting": {"fr": "Temps moyen d'attente", "en": "Average waiting time", "da": "Gennemsnitlig ventetid"},
        "occupancy": {"fr": "Taux d'occupation", "en": "Occupancy rate", "da": "Belægningsgrad"},
        "graph_title": {"fr": "Occupation des voies", "en": "Track occupancy", "da": "Sporbesættelse"},
        "hour_of_day": {"fr": "Heure de la journée", "en": "Hour of the day", "da": "Dagens timer"},
        "train_added": {"fr": "Train {name} ajouté !","en": "Train {name} added!","da": "Tog {name} tilføjet!"},
        "train_too_long": {"fr": "Le train est trop long pour toutes les voies disponibles.","en": "The train is too long for all available tracks.","da": "Toget er for langt til alle tilgængelige spor."},
        "security_delay": {"fr": "Délai de sécurité (minutes)", "en": "Security delay (minutes)", "da": "Sikkerhedsforsinkelse (minutter)"},
        "electric_train": {"fr": "🚆 Train électrique", "en": "🚆 Electric train", "da": "🚆 Elektrisk tog"},
        "select_depot": {"fr": "Sélectionnez un dépôt", "en": "Select a depot", "da": "Vælg et depot"},
        "modify_train": {"fr": "Modifier un train", "en": "Modify a train", "da": "Rediger et tog"},
        "delete_train": {"fr": "Supprimer un train", "en": "Delete a train", "da": "Slet et tog"},
        "select_train_to_modify": {"fr": "Sélectionnez un train à modifier", "en": "Select a train to modify", "da": "Vælg et tog til redigering"},
        "select_train_to_delete": {"fr": "Sélectionnez un train à supprimer", "en": "Select a train to delete", "da": "Vælg et tog til sletning"},
        "apply_changes": {"fr": "Appliquer les modifications", "en": "Apply changes", "da": "Anvend ændringer"},
        "train_updated": {"fr": "Train {id} mis à jour avec succès !", "en": "Train {id} successfully updated!", "da": "Tog {id} opdateret med succes!"},
        "departure_after_arrival_error": {
            "fr": "L'heure de départ doit être postérieure à l'heure d'arrivée.",
            "en": "Departure time must be after arrival time.",
            "da": "Afgangstid skal være efter ankomsttid."
        },
        "delete": {"fr": "Supprimer", "en": "Delete", "da": "Slet"},
        "security_settings": {
            "fr": "Paramètres de sécurité",
            "en": "Security Settings",
            "da": "Sikkerhedsindstillinger"
        },
        "transfer_train": {
            "fr": "Voulez-vous transférer le train {name} au dépôt {depot} ?",
            "en": "Do you want to transfer train {name} to depot {depot}?",
            "da": "Vil du overføre toget {name} til depotet {depot}?"
        },
        "train_transferred": {
            "fr": "Le train {name} a été transféré au dépôt {depot}.",
            "en": "Train {name} has been transferred to depot {depot}.",
            "da": "Toget {name} er blevet overført til depotet {depot}."
        },
        "transfer_failed": {
            "fr": "Impossible de transférer le train {name} au dépôt {depot}.",
            "en": "Unable to transfer train {name} to depot {depot}.",
            "da": "Kan ikke overføre toget {name} til depotet {depot}."
        },
        "invalid_train_length": {
            "fr": "La longueur du train doit être supérieure à 0.",
            "en": "The train length must be greater than 0.",
            "da": "Togets længde skal være større end 0."
        },
        "departure_after_arrival_error": {
            "fr": "L'heure de départ doit être postérieure à l'heure d'arrivée.",
            "en": "Departure time must be after arrival time.",
            "da": "Afgangstid skal være efter ankomsttid."
        },
        "train_not_placed": {
            "fr": "Le train {name} n'a pas pu être placé dans le dépôt {depot}.",
            "en": "The train {name} could not be placed in depot {depot}.",
            "da": "Toget {name} kunne ikke placeres i depotet {depot}."
        },
        "transfer_failed": {
            "fr": "Impossible de transférer le train {name} au dépôt {depot}.",
            "en": "Unable to transfer train {name} to depot {depot}.",
            "da": "Kan ikke overføre toget {name} til depotet {depot}."
        },
        "train_transferred": {
            "fr": "Le train {name} a été transféré au dépôt {depot}.",
            "en": "Train {name} has been transferred to depot {depot}.",
            "da": "Toget {name} er blevet overført til depotet {depot}."
        },
        "requirements": {
            "fr": "Besoins",
            "en": "Requirements",
            "da": "Krav"
        },
        "test_drivers": {
            "fr": "Conducteurs de test",
            "en": "Test drivers",
            "da": "Testførere"
        },
        "locomotives": {
            "fr": "Locomotives",
            "en": "Locomotives",
            "da": "Lokomotiver"
        },
        "details": {
            "fr": "Détails",
            "en": "Details",
            "da": "Detaljer"
        },
        "train_type": {
            "fr": "Type de train",
            "en": "Train type",
            "da": "Togtype"
        },
        "testing": {
            "fr": "Test",
            "en": "Testing",
            "da": "Test"
        },
        "storage": {
            "fr": "Stockage",
            "en": "Storage",
            "da": "Opbevaring"
        },
        "pit": {
            "fr": "Fosse",
            "en": "Pit",
            "da": "Grav"
        },
        "from": {
            "fr": "De",
            "en": "From",
            "da": "Fra"
        },
        "to": {
            "fr": "À",
            "en": "To",
            "da": "Til"
        },
        "requirements_by_day": {
            "fr": "Besoins par jour",
            "en": "Requirements by day",
            "da": "Krav pr. dag"
        },
        "resource_type": {
            "fr": "Type de ressource",
            "en": "Resource type",
            "da": "Ressourcetype"
        },
        "quantity": {
            "fr": "Quantité",
            "en": "Quantity",
            "da": "Mængde"
        },
        "no_requirements": {
            "fr": "Aucun besoin pour les trains actuels.",
            "en": "No requirements for the current trains.",
            "da": "Ingen krav til de nuværende tog."
        },
        "train_schedule": {
    "fr": "Horaires des trains",
    "en": "Train schedule",
    "da": "Togplan"
},
"no_trains": {
    "fr": "Aucun train à afficher.",
    "en": "No trains to display.",
    "da": "Ingen tog at vise."
},
"train_length_by_track": {
    "fr": "Longueur des trains par voie",
    "en": "Train length by track",
    "da": "Toglængde pr. spor"
},
"wagons": {
    "fr": "Nombre de wagons",
    "en": "Number of wagons",
    "da": "Antal vogne"
},
"locomotives": {
    "fr": "Nombre de locomotives",
    "en": "Number of locomotives",
    "da": "Antal lokomotiver"
},
"wagon": {
    "fr": "Wagon",
    "en": "Wagon",
    "da": "Vogn"
},
"locomotive": {
    "fr": "Locomotive",
    "en": "Locomotive",
    "da": "Lokomotiv"
},
"locomotive_side": {
    "fr": "Côté de la locomotive",
    "en": "Locomotive side",
    "da": "Lokomotivens side"
},
"left": {
    "fr": "Gauche",
    "en": "Left",
    "da": "Venstre"
},
"right": {
    "fr": "Droite",
    "en": "Right",
    "da": "Højre"
}, 
"end_date": {
    "fr": "Date de fin",
    "en": "End date",
    "da": "Slutdato"
},
"end_time": {
    "fr": "Heure de fin",
    "en": "End time",
    "da": "Sluttid"
},
"invalid_time_range": {
    "fr": "La plage horaire est invalide. L'heure de début doit être antérieure à l'heure de fin.",
    "en": "Invalid time range. Start time must be earlier than end time.",
    "da": "Ugyldigt tidsinterval. Starttid skal være tidligere end sluttid."
},

    "graph_title1": {
        "fr": "Occupation des voies",
        "en": "Track Occupancy",
        "da": "Sporbesættelse"
    },
    "add_coach": {
        "fr": "Ajouter un wagon",
        "en": "Add a wagon",
        "da": "Tilføj en vogn eller"
    },
    "add_wagon": {
        "fr": "Ajouter un wagon",
        "en": "Add a wagon",
        "da": "Tilføj en vogn"
    },
    "add_locomotive": {
        "fr": "Ajouter une locomotive",
        "en": "Add a locomotive",
        "da": "Tilføj et lokomotiv"
    },
    "delete_element": {
        "fr": "Supprimer un élément",
        "en": "Delete an element",
        "da": "Slet et element"
    },
    "select_track": {
        "fr": "Sélectionnez une voie",
        "en": "Select a track",
        "da": "Vælg et spor"
    },
    "element_id": {
        "fr": "ID de l'élément",
        "en": "Element ID",
        "da": "Element-ID"
    },
    "move_wagon": {
        "fr": "Déplacer un wagon",
        "en": "Move a wagon",
        "da": "Flyt en vogn"
    },
    "select_source_track": {
        "fr": "Sélectionnez la voie source",
        "en": "Select source track",
        "da": "Vælg kildespor"
    },
    "select_target_track": {
        "fr": "Sélectionnez la voie cible",
        "en": "Select target track",
        "da": "Vælg målespor"
    },
    "wagon_id": {
        "fr": "ID du wagon",
        "en": "Wagon ID",
        "da": "Vogn-ID"
    },
    "move": {
        "fr": "Déplacer",
        "en": "Move",
        "da": "Flyt"
    },
    "track_full": {
        "fr": "La voie est pleine, impossible d'ajouter un wagon.",
        "en": "The track is full, cannot add a wagon.",
        "da": "Sporret er fuldt, kan ikke tilføje en vogn."
    },
    "success_add": {
        "fr": "Wagon ajouté avec succès.",
        "en": "Wagon added successfully.",
        "da": "Vogn tilføjet med succes."
    },
    "success_delete": {
        "fr": "Élément supprimé avec succès.",
        "en": "Element deleted successfully.",
        "da": "Element slettet med succes."
    },
    "success_move": {
        "fr": "Wagon déplacé avec succès.",
        "en": "Wagon moved successfully.",
        "da": "Vogn flyttet med succes."
    },
    "error_move": {
        "fr": "Impossible de déplacer le wagon.",
        "en": "Unable to move the wagon.",
        "da": "Kan ikke flytte vognen."
    },

    "reset_game": {"fr": "Réinitialiser le jeu", "en": "Reset game", "da": "Nulstil spil"},

}

def t(key, lang, **kwargs):
    translations = get_translation(lang)
    return translations.get(key, {}).get(lang, key).format(**kwargs)