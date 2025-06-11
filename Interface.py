# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:54:24 2025

@author: andre
"""

import streamlit as st
from datetime import datetime
from Simulation import Train
import pandas as pd

def afficher_formulaire_ajout(simulation, lang, t):
    st.subheader(t("add_train", lang))

    # Indicateur pour afficher un message de confirmation
    if "train_added" not in st.session_state:
        st.session_state.train_added = False

    # Afficher un message de confirmation si un train a été ajouté
    if st.session_state.train_added:
        st.success(t("train_added", lang, name=st.session_state.last_train_name))
        st.session_state.train_added = False  # Réinitialiser l'indicateur

    depot = st.selectbox(t("select_depot", lang), ["Glostrup", "Naestved"])
    base_time = st.session_state.base_time
    date_base = st.date_input(t("base_date", lang), st.session_state.base_time.date())
    heure_base = st.time_input(t("base_time", lang), base_time.time())
    st.session_state.base_time = datetime.combine(date_base, heure_base)

    col1, col2, col3 = st.columns(3)
    with col1:
        date_arr = st.date_input(t("arrival_date", lang))
        heure_arr = st.time_input(t("arrival_time", lang))
    with col2:
        date_dep = st.date_input(t("departure_date", lang))
        heure_dep = st.time_input(t("departure_time", lang))
    with col3:
        nom = st.text_input(t("train_name", lang), "")
        wagons = st.number_input(t("wagons", lang), min_value=1, step=1)
        locomotives = st.number_input(t("locomotives", lang), min_value=0, step=1)  # Permettre 0 locomotive
        optimiser = st.checkbox(t("optimize", lang))
        electrique = st.checkbox(t("electric_train", lang), value=False)

    # Afficher dynamiquement le choix du côté de la locomotive si une seule est sélectionnée
    locomotive_cote = None
    if locomotives == 1:
        locomotive_cote = st.radio(
            t("locomotive_side", lang),
            options=["left", "right"],
            format_func=lambda x: t(x, lang)
        )

    # Nouveau champ pour le type de train
    type_train = st.selectbox(
        t("train_type", lang),
        ["testing", "storage", "pit"],
        format_func=lambda x: t(x, lang)
    )

    if st.button(t("submit_train", lang)):
        arrivee = datetime.combine(date_arr, heure_arr)
        depart = datetime.combine(date_dep, heure_dep)
        if depart <= arrivee:
            st.error(t("departure_after_arrival_error", lang))
            return

        
        train = Train(
            id=len(simulation.trains),
            nom=nom,
            wagons=wagons,
            locomotives=locomotives,
            arrivee=arrivee,
            depart=depart,
            depot=depot,
            type=type_train
        )
        train.electrique = electrique
        train.locomotive_cote = locomotive_cote  # Stocker le côté de la locomotive
        erreur = simulation.ajouter_train(train, depot, optimiser=optimiser)
        
        if erreur:
            st.error(erreur)
        else:
            # Stocker l'indicateur et le nom du train ajouté
            st.session_state.train_added = True
            st.session_state.last_train_name = nom
            st.rerun()
            
    # --- Import de trains depuis un fichier CSV ou Excel ---
    st.markdown("### " + t("import_trains", lang))
    uploaded_file = st.file_uploader(t("import_file", lang), type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df_import = pd.read_csv(uploaded_file, sep=None, engine="python")
        else:
            df_import = pd.read_excel(uploaded_file)
        st.markdown("#### " + t("file_preview", lang))
        st.dataframe(df_import.head(), use_container_width=True)
        if st.button(t("add_imported_trains", lang)):
            # Correction : calculer l'ID max avant la boucle
            if simulation.trains:
                next_id = max(train.id for train in simulation.trains) + 1
            else:
                next_id = 0
            for _, row in df_import.iterrows():
                try:
                    def get_col(*names):
                        for name in names:
                            if name in row:
                                return row[name]
                        return None

                    locomotive_cote = get_col("Côté sans locomotive", "Locomotive opposite side", "Lokomotivens side")
                    if isinstance(locomotive_cote, str):
                        locomotive_cote = locomotive_cote.strip().lower()
                        if locomotive_cote not in ["left", "right"]:
                            locomotive_cote = None

                    train = Train(
                        id=next_id,
                        nom=get_col("Nom", "Train name", "Tog navn", "Train"),
                        wagons=int(get_col("Nombre de wagons", "Number of wagons", "Antal vogne", "wagons") or 1),
                        locomotives=int(get_col("Nombre de locomotives", "Number of locomotives", "Antal lokomotiver", "locomotives") or 1),
                        arrivee=pd.to_datetime(get_col("Heure d'arrivée", "Arrival time", "Ankomsttid", "Arrival")),
                        depart=pd.to_datetime(get_col("Heure de départ", "Departure time", "Afgangstid", "Departure")),
                        depot=get_col("Dépôt", "Depot", "Depot") or "Glostrup",
                        type=(get_col("Type de train", "Train type", "Togtype", "Type") or "storage").lower()
                    )
                    next_id += 1  # Incrémenter pour le prochain train

                    # Conversion robuste pour le booléen électrique
                    val = get_col("Électrique", "Electric", "Elektrisk", False)
                    if isinstance(val, str):
                        val = val.strip().lower() in ["true", "1", "yes", "oui"]
                    train.electrique = bool(val)

                    train.locomotive_cote = locomotive_cote
                    simulation.ajouter_train(train, train.depot)
                except Exception as e:
                    st.warning(f"{t('import_error_row', lang)} {row.to_dict()}: {e}")
            st.success(t("import_success", lang))
            st.rerun()
            
        st.markdown("#### " + t("import_example_title", lang))
        st.info(t("import_example_help", lang))
    
    # Afficher l'exemple de tableau même si aucun fichier n'est uploadé
    import_columns = [
        "Train Nom", "Nombre de wagons", "Nombre de locomotives", "Heure d'arrivée", "Heure de départ",
        "Dépôt", "Type de train", "Électrique", "Côté sans locomotive"
    ]
    exemple_row = {
        "Train Nom": "Train A",
        "Nombre de wagons": 10,
        "Nombre de locomotives": 1,
        "Heure d'arrivée": "2025-06-12 08:00",
        "Heure de départ": "2025-06-12 12:00",
        "Dépôt": "Glostrup",
        "Type de train": "testing",
        "Électrique": True,
        "Côté sans locomotive": "left"
    }
    translated_columns = [t(col, lang) for col in import_columns]
    exemple_df = pd.DataFrame([[exemple_row[col] for col in import_columns]], columns=translated_columns)
    st.dataframe(exemple_df, use_container_width=True)
    st.caption(t("import_columns_info", lang))
                
def afficher_tableau_trains(trains, simulation, t, lang):
    """Affiche le tableau des trains."""
    if trains:
        st.subheader(t("train_list", lang))

        # Construire un DataFrame
        data = []
        for train in trains:
            attente = (
                (train.fin_attente - train.debut_attente).total_seconds() / 60
                if train.fin_attente and train.debut_attente else 0
            )
            voie_num = (
                simulation.numeros_voies_a[train.voie]
                if train.depot == "Glostrup" and train.voie is not None
                else simulation.numeros_voies_b[train.voie]
                if train.depot == "Naestved" and train.voie is not None
                else "-"
            )
            voie_electrifiee = "⚡" if voie_num == 9 else ""  # Indicateur pour la voie 9
            data.append({
                "Nom": train.nom,  # Afficher le nom du train
                t("arrival_time", lang): train.arrivee.strftime("%Y-%m-%d %H:%M"),
                t("departure_time", lang): train.depart.strftime("%Y-%m-%d %H:%M"),
                t("length", lang): train.longueur,
                t("Track", lang): f"{voie_num} {voie_electrifiee}",
                t("Dépôt", lang): train.depot,
                t("waiting", lang): f"{attente:.1f} min" if attente is not None  else "-", #train.en_attente
                t("train_type", lang): t(train.type, lang),
            })
            
        # Créer et afficher le DataFrame
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        

def afficher_modification_train(trains, simulation, t, lang):
    """Affiche l'interface pour modifier un train existant."""
    train_options = [f"{train.nom} (T{train.id})" for train in trains]  # Afficher le nom et l'ID
    selected_option = st.selectbox(t("select_train_to_modify", lang), options=[""] + train_options)

    if selected_option:
        train_id = int(selected_option.split("(T")[1][:-1])  # Extraire l'ID numérique du train
        train = next((train for train in trains if train.id == train_id), None)
        if train:
            new_arrival_date = st.date_input(t("arrival_date", lang), train.arrivee.date())
            new_arrival_time = st.time_input(t("arrival_time", lang), train.arrivee.time())
            new_departure_date = st.date_input(t("departure_date", lang), train.depart.date())
            new_departure_time = st.time_input(t("departure_time", lang), train.depart.time())

            if st.button(t("apply_changes", lang)):
                new_arrival = datetime.combine(new_arrival_date, new_arrival_time)
                new_departure = datetime.combine(new_departure_date, new_departure_time)

                if new_departure > new_arrival:
                    etat_avant = train.__dict__.copy()
                    # Validation avancée
                    simulation.trains.remove(train)
                    train.arrivee = new_arrival
                    train.depart = new_departure
                    erreur = simulation.ajouter_train(train, train.depot, optimiser=True)
                    if erreur:
                        # Restaure l'ancien état si conflit
                        for k, v in etat_avant.items():
                            setattr(train, k, v)
                        simulation.trains.append(train)
                        st.error("Modification impossible : conflit détecté.")
                    else:
                        simulation.historique.append({
                            "action": "modification",
                            "train_id": train.id,
                            "etat_avant": etat_avant,
                            "etat_apres": train.__dict__.copy()
                        })
                        st.success(t("train_schedule_updated", lang, name=train.nom))
                        st.rerun()
                else:
                    st.error(t("departure_after_arrival_error", lang))

def afficher_suppression_train(trains, simulation, t, lang):
    """Affiche l'interface pour supprimer un train."""
    train_options = [f"{train.nom} (T{train.id})" for train in trains]  # Afficher le nom et l'ID
    selected_option = st.selectbox(t("remove", lang), options=[""] + train_options)
    if selected_option:
        train_id = int(selected_option.split("(T")[1][:-1])  # Extraire l'ID numérique du train
        if st.button(t("remove", lang)):
            
            # Récupérer l'état avant suppression
            train_suppr = next((train for train in simulation.trains if train.id == train_id), None)
            etat_avant = train_suppr.__dict__.copy() if train_suppr else None
            
            # Supprimer le train des occupations
            
            for occupation in [simulation.occupation_a, simulation.occupation_b]:
                occupation[:] = [entry for entry in occupation if entry[3].id != train_id]

            # Supprimer le train de la liste des trains
            simulation.trains = [train for train in simulation.trains if train.id != train_id]
            simulation.historique.append({
                "action": "suppression",
                "train_id": train_id,
                "etat_avant": etat_avant,
                "etat_apres": None
            })
            # Recalculer la simulation
            simulation.recalculer()
            st.success(t("train_removed", lang, name=selected_option))
            st.rerun()