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

       # if depart <= arrivee:
        #    st.error(erreur)
       #     return

      #  if erreur:
       #     st.error(erreur)
      #  else:
            # Stocker l'indicateur et le nom du train ajouté
      #      st.session_state.train_added = True
      #      st.session_state.last_train_name = nom
                
def afficher_tableau_trains(trains, simulation, t, lang):
    """Affiche le tableau des trains."""
    if trains:
        st.subheader(t("train_list", lang))

        # Construire un DataFrame
        data = []
        for train in trains:
            attente = (
    (train.fin_attente - train.debut_attente).total_seconds() / 60
    if train.en_attente and train.fin_attente and train.debut_attente
    else None
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
                    train.arrivee = new_arrival
                    train.depart = new_departure
                    simulation.recalculer()
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
            # Supprimer le train des occupations
            for occupation in [simulation.occupation_a, simulation.occupation_b]:
                occupation[:] = [entry for entry in occupation if entry[3].id != train_id]

            # Supprimer le train de la liste des trains
            simulation.trains = [train for train in simulation.trains if train.id != train_id]

            # Recalculer la simulation
            simulation.recalculer()
            st.success(t("train_removed", lang, name=selected_option))
            st.rerun()