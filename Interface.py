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

    if "train_added" not in st.session_state:
        st.session_state.train_added = False

    if st.session_state.train_added:
        st.success(t("train_added", lang, name=st.session_state.last_train_name))
        st.session_state.train_added = False

    depot = st.selectbox(t("select_depot", lang), list(simulation.depots.keys()), help=t("select_depot_tooltip",lang))
    st.divider()

    # Bloc 1 : Dates et heures sur une ligne
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        date_arr = st.date_input(t("arrival_date", lang), help=t("arrival_date_tooltip",lang))
    with col2:
        heure_arr = st.time_input(t("arrival_time", lang), help=t("arrival_time_tooltip",lang))
    with col3:
        date_dep = st.date_input(t("departure_date", lang), help=t("departure_date_tooltip",lang))
    with col4:
        heure_dep = st.time_input(t("departure_time", lang), help=t("departure_time_tooltip",lang))
    st.divider()

    # Bloc 2 : Nom, wagons, locomotives, type, options sur une ligne
    col5, col6, col7, col8 = st.columns([2, 1, 1, 2])
    with col5:
        nom = st.text_input(t("train_name", lang), "", help=t("train_name_tooltip",lang))
    with col6:
        wagons = st.number_input(t("wagons", lang), min_value=1, step=1, help=t("wagons_tooltip",lang))
    with col7:
        locomotives = st.number_input(t("locomotives", lang), min_value=0, step=1, help=t("locomotives_tooltip",lang))
    with col8:
        type_train = st.selectbox(
            t("train_type", lang),
            ["testing", "storage", "pit"],
            format_func=lambda x: t(x, lang),
            help=t("train_type_tooltip",lang)
        )
    st.divider()

    # Bloc 3 : Options (optimiser, électrique, côté loco si 1 loco)
    col9, col10, col11 = st.columns([1, 1, 2])
    with col9:
        optimiser = st.checkbox(t("optimize", lang), help=t("optimize_tooltip",lang))
    with col10:
        electrique = st.checkbox(t("electric_train", lang), value=False, help=t("electric_train_tooltip",lang))
    with col11:
        locomotive_cote = None
        if locomotives == 1:
            locomotive_cote = st.radio(
                t("locomotive_side", lang),
                options=["left", "right"],
                format_func=lambda x: t(x, lang),
                help=t("locomotive_side_tooltip",lang)
            )
    st.divider()

    if st.button(t("submit_train", lang)):
        from datetime import datetime
        arrivee = datetime.combine(date_arr, heure_arr)
        depart = datetime.combine(date_dep, heure_dep)
        if depart <= arrivee:
            st.error(t("departure_after_arrival_error", lang))
            return

        if simulation.trains:
            next_id = max(train.id for train in simulation.trains) + 1
        else:
            next_id = 0

        train = Train(
            id=next_id,
            nom=nom,
            wagons=wagons,
            locomotives=locomotives,
            arrivee=arrivee,
            depart=depart,
            depot=depot,
            type=type_train
        )
        train.electrique = electrique
        train.locomotive_cote = locomotive_cote
        erreur = simulation.ajouter_train(train, depot, optimiser=optimiser)

        if erreur:
            st.error(erreur)
        else:
            st.session_state.train_added = True
            st.session_state.last_train_name = nom
            st.rerun()
            
    # --- FR : Import de trains depuis un fichier CSV ou Excel ---
    # --- EN : Import trains from a CSV or Excel file ---
    st.markdown("### " + t("import_trains", lang))
    uploaded_file = st.file_uploader(t("import_file", lang), type=["csv", "xlsx"], help=t("import_file_tooltip",lang))
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df_import = pd.read_csv(uploaded_file, sep=None, engine="python")
        else:
            df_import = pd.read_excel(uploaded_file)
        st.markdown("#### " + t("file_preview", lang))
        st.dataframe(df_import.head(), use_container_width=True)
        if "import_done" not in st.session_state:
            st.session_state.import_done = False
        if st.button(t("add_imported_trains", lang)):
            # FR : Calculer l'ID max avant la boucle d'import.
            # EN : Compute max ID before import loop.
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

                    # FR : Récupère et nettoie le côté de la locomotive si présent.
                    # EN : Get and clean locomotive side if present.
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
                    next_id += 1  # FR : Incrémente pour le prochain train / EN : Increment for next train

                    # FR : Conversion robuste pour le booléen électrique.
                    # EN : Robust conversion for electric boolean.
                    val = get_col("Électrique", "Electric", "Elektrisk", False)
                    if isinstance(val, str):
                        val = val.strip().lower() in ["true", "1", "yes", "oui"]
                    train.electrique = bool(val)

                    # FR : Attribue le côté de la locomotive uniquement si 1 locomotive.
                    # EN : Assign locomotive side only if 1 locomotive.
                    if train.locomotives == 1:
                        train.locomotive_cote = locomotive_cote
                    else:
                        train.locomotive_cote = None
                    simulation.ajouter_train(train, train.depot)
                except Exception as e:
                    st.warning(f"{t('import_error_row', lang)} {row.to_dict()}: {e}")
            st.session_state.import_done = True
            st.success(t("import_success", lang))
            st.rerun()
        elif st.session_state.import_done:
            st.info(t("import_success", lang))
            
        st.markdown("#### " + t("import_example_title", lang))
        st.info(t("import_example_help", lang))
    
    # FR : Affiche un exemple de tableau d'import même sans fichier uploadé.
    # EN : Show an import table example even if no file is uploaded.
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
    """
    FR : Affiche le tableau des trains avec toutes les informations utiles.
    EN : Display the train table with all useful information.
    """
    if trains:
        st.subheader(t("train_list", lang))

        # FR : Construction du DataFrame pour affichage.
        # EN : Build DataFrame for display.
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
            voie_electrifiee = "⚡" if voie_num == 9 else ""  # FR : Indicateur pour la voie 9 / EN : Indicator for track 9
            data.append({
                "Nom": train.nom,
                t("arrival_time", lang): train.arrivee.strftime("%Y-%m-%d %H:%M"),
                t("departure_time", lang): train.depart.strftime("%Y-%m-%d %H:%M"),
                t("length", lang): train.longueur,
                t("Track", lang): f"{voie_num} {voie_electrifiee}",
                t("Dépôt", lang): train.depot,
                t("waiting", lang): f"{attente:.1f} min" if attente is not None  else "-",
                t("train_type", lang): t(train.type, lang),
            })
            
        # FR : Affiche le DataFrame dans Streamlit.
        # EN : Show DataFrame in Streamlit.
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        

def afficher_modification_train(trains, simulation, t, lang):
    """
    FR : Affiche l'interface pour modifier un train existant.
    EN : Display the interface to modify an existing train.
    """
    train_options = [f"{train.nom} (T{train.id})" for train in trains]  # FR : Affiche nom et ID / EN : Show name and ID
    selected_option = st.selectbox(t("select_train_to_modify", lang), options=[""] + train_options)

    if selected_option:
        train_id = int(selected_option.split("(T")[1][:-1])  # FR : Extrait l'ID numérique du train / EN : Extract numeric train ID
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
                    # FR : Retire le train avant modification pour éviter les conflits.
                    # EN : Remove train before modification to avoid conflicts.
                    simulation.trains.remove(train)
                    train.arrivee = new_arrival
                    train.depart = new_departure
                    erreur = simulation.ajouter_train(train, train.depot, optimiser=True)
                    if erreur:
                        # FR : Restaure l'ancien état si conflit.
                        # EN : Restore previous state if conflict.
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
    """
    FR : Affiche l'interface pour supprimer un train.
    EN : Display the interface to delete a train.
    """
    train_options = [f"{train.nom} (T{train.id})" for train in trains]  # FR : Affiche nom et ID / EN : Show name and ID
    selected_option = st.selectbox(t("remove", lang), options=[""] + train_options)
    if selected_option:
        train_id = int(selected_option.split("(T")[1][:-1])  # FR : Extrait l'ID numérique du train / EN : Extract numeric train ID
        if st.button(t("remove", lang)):
            
            # FR : Récupère l'état avant suppression pour l'historique.
            # EN : Get state before deletion for history.
            train_suppr = next((train for train in simulation.trains if train.id == train_id), None)
            etat_avant = train_suppr.__dict__.copy() if train_suppr else None
            
            # FR : Supprime le train des occupations de voies.
            # EN : Remove train from track occupations.
            for occupation in [simulation.occupation_a, simulation.occupation_b]:
                occupation[:] = [entry for entry in occupation if entry[3].id != train_id]

            # FR : Supprime le train de la liste des trains.
            # EN : Remove train from train list.
            simulation.trains = [train for train in simulation.trains if train.id != train_id]
            simulation.historique.append({
                "action": "suppression",
                "train_id": train_id,
                "etat_avant": etat_avant,
                "etat_apres": None
            })
            # FR : Recalcule la simulation après suppression.
            # EN : Recalculate simulation after deletion.
            simulation.recalculer()
            st.success(t("train_removed", lang, name=selected_option))
            st.rerun()