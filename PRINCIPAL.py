# -*- coding: utf-8 -*-
"""
PRINCIPAL.py
============

Application principale Streamlit pour la simulation d'occupation des voies de dépôt ferroviaire.

- Permet d'ajouter, modifier, supprimer des trains.
- Visualise l'occupation des voies, les statistiques et les besoins en ressources.
- Gère la langue de l'interface (français, anglais, danois).
- Propose un mini-jeu de gestion de wagons.

Modules utilisés :
- Simulation : logique métier et gestion des trains/voies.
- Traduction : gestion multilingue.
- Interface : composants d'interface utilisateur.
- Stats : calculs statistiques et requirements.
- Plots : graphiques Plotly pour la visualisation.

Auteur : andre
Date de création : 02/05/2025
"""

import streamlit as st
from datetime import datetime, timedelta
from Simulation import Simulation
from Traduction import t, get_translation
from Interface import (afficher_formulaire_ajout, 
                       afficher_tableau_trains, 
                       afficher_modification_train, 
                       afficher_suppression_train)
from Stats import (calculer_temps_moyen_attente, 
                   calculer_taux_occupation, 
                   calculer_statistiques_globales, 
                   calculer_requirements, 
                   regrouper_requirements_par_jour)
from Plots import (creer_graphique_occupation_depot,
                   creer_graphique_requirements_par_jour,
                   creer_graphique_trains_par_longueur_detaille,
                   creer_gantt_occupation_depot)

import pandas as pd
import io

# ---------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE ET INITIALISATION DE LA SIMULATION
# ---------------------------------------------------------------------------

# Configuration de la page
st.set_page_config(layout="wide")

# Initialisation
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()
    st.session_state.base_time = datetime.combine(datetime.now().date(), datetime.min.time())

# ---------------------------------------------------------------------------
# GESTION DE LA LANGUE
# ---------------------------------------------------------------------------

lang = st.sidebar.selectbox("Langue", ["fr", "en", "da"])
t_dict = get_translation(lang)

# ---------------------------------------------------------------------------
# TITRE PRINCIPAL ET PARAMÈTRES DE SÉCURITÉ
# ---------------------------------------------------------------------------

st.title(t("title", lang))

# Délai de sécurité entre deux trains sur une même voie (slider dans la sidebar)
st.sidebar.subheader(t("security_settings", lang))
delai_securite = st.sidebar.slider(
    t("security_delay", lang), min_value=0, max_value=30, value=10, step=1
)
st.session_state.simulation.delai_securite = delai_securite

# Bouton pour réinitialiser la simulation
if st.sidebar.button(t("reset", lang)):
    st.session_state.simulation.reset()
    st.success(t("simulation_reset", lang))
    st.rerun()

# ---------------------------------------------------------------------------
# CALCUL DES STATISTIQUES GLOBALES
# ---------------------------------------------------------------------------

stats = calculer_statistiques_globales(st.session_state.simulation)

# ---------------------------------------------------------------------------
# ORGANISATION EN ONGLETS PRINCIPAUX
# ---------------------------------------------------------------------------
# tab1 : Ajout/Modification/Suppression de trains
# tab2 : Liste des trains par dépôt
# tab3 : Visualisations graphiques (occupation, export, Gantt, etc.)
# tab4 : Statistiques globales
# tab5 : Besoins en ressources (requirements)
# tab6 : Mini-jeu de gestion des voies

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("add_train", lang), 
    t("train_list", lang), 
    t("graph_title", lang), 
    t("Statistiques", lang), 
    t("requirements", lang), 
    t("Gestion des voies", lang)])

# ---------------------------------------------------------------------------
# ONGLET 1 : AJOUT / MODIFICATION / SUPPRESSION DE TRAINS
# ---------------------------------------------------------------------------

with tab1:
    sous_tab_ajout, sous_tab_modif, sous_tab_suppr = st.tabs([
        t("add_train", lang),
        t("modify_train", lang),
        t("delete_train", lang)
    ])
    with sous_tab_ajout:
        afficher_formulaire_ajout(st.session_state.simulation, lang, t)
    with sous_tab_modif:
        afficher_modification_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)
    with sous_tab_suppr:
        afficher_suppression_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)

# ---------------------------------------------------------------------------
# ONGLET 2 : LISTE DES TRAINS PAR DÉPÔT
# ---------------------------------------------------------------------------

with tab2:
    # Tableau pour le dépôt A
    st.subheader(t("Depot de Glostrup", lang))
    afficher_tableau_trains(
        [train for train in st.session_state.simulation.trains if train.depot == "Glostrup"],
        st.session_state.simulation,t, lang
    )

    # Tableau pour le dépôt B
    st.subheader(t("Depot de Naestved", lang))
    afficher_tableau_trains(
        [train for train in st.session_state.simulation.trains if train.depot == "Naestved"],
        st.session_state.simulation,t, lang
    )
    
# ---------------------------------------------------------------------------
# ONGLET 3 : VISUALISATIONS GRAPHIQUES
# ---------------------------------------------------------------------------

with tab3:
    sous_tab_occ, sous_tab_export, sous_tab_instant, sous_tab_gantt_a, sous_tab_gantt_b = st.tabs([
        t("graph_title", lang),
        "Export",
        t("train_length_by_track", lang),
        f"Gantt {t('Depot de Glostrup', lang)}",
        f"Gantt {t('Depot de Naestved', lang)}"
    ])
    
    # Visualisation occupation des voies
    with sous_tab_occ:
        st.subheader(t("Depot de Glostrup", lang))
        fig_a = creer_graphique_occupation_depot(
            st.session_state.simulation, "Glostrup", st.session_state.base_time, t, lang
        )
        st.plotly_chart(fig_a, use_container_width=True)

        st.subheader(t("Depot Naestved", lang))
        fig_b = creer_graphique_occupation_depot(
            st.session_state.simulation, "Naestved", st.session_state.base_time, t, lang
        )
        st.plotly_chart(fig_b, use_container_width=True)
        
    # Export des occupations (CSV, Excel, JSON)
    with sous_tab_export:
        def occupation_to_df(simulation):
            data = []
            for depot, occupation, numeros_voies in [
                ("Glostrup", simulation.occupation_a, simulation.numeros_voies_a),
                ("Naestved", simulation.occupation_b, simulation.numeros_voies_b),
            ]:
                for voie_idx, debut, fin, train in occupation:
                    data.append({
                        "Depot": depot,
                        "Track": numeros_voies[voie_idx],
                        "Train": train.nom,
                        "Type": train.type,
                        "Arrival": debut.strftime("%Y-%m-%d %H:%M"),
                        "Departure": fin.strftime("%Y-%m-%d %H:%M"),
                        "Electric": train.electrique,
                    })
            return pd.DataFrame(data)
        
        df_occ = occupation_to_df(st.session_state.simulation)
        csv = df_occ.to_csv(index=False, sep=";").encode('utf-8')  # <-- AJOUTE sep=";"
        st.download_button(
            label="📥 Télécharger l'occupation des voies (CSV)",
            data=csv,
            file_name="occupation_voies.csv",
            mime="text/csv"
        )
        output = io.BytesIO()
        df_occ.to_excel(output, index=False)
        st.download_button(
            label="📥 Télécharger l'occupation des voies (Excel)",
            data=output.getvalue(),
            file_name="occupation_voies.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="📥 Télécharger l'occupation des voies (JSON)",
            data=df_occ.to_json(orient="records"),
            file_name="occupation_voies.json",
            mime="application/json"
        )
    
    # Visualisation instantanée de la composition des trains
    with sous_tab_instant:
        col1, col2 = st.columns(2)
        with col1:
            date_instant = st.date_input(t("base_date", lang), st.session_state.base_time.date(), key="date_instant")
        with col2:
            heure_instant = st.time_input(t("base_time", lang), st.session_state.base_time.time(), key="heure_instant")
        instant = datetime.combine(date_instant, heure_instant)
        fig_trains_instant = creer_graphique_trains_par_longueur_detaille(
            st.session_state.simulation, t, instant, lang
        )
        st.plotly_chart(fig_trains_instant, use_container_width=True)

    # Gantt Glostrup
    with sous_tab_gantt_a:
        st.markdown(f"### {t('Planning', lang)} - {t('Depot de Glostrup', lang)}")
        fig_gantt_a = creer_gantt_occupation_depot(
            st.session_state.simulation, "Glostrup", t, lang
        )
        st.plotly_chart(fig_gantt_a, use_container_width=True)
        # Export Gantt Glostrup
        data_gantt_a = []
        for voie_idx, debut, fin, train in st.session_state.simulation.occupation_a:
            data_gantt_a.append({
                "Voie": st.session_state.simulation.numeros_voies_a[voie_idx],
                "Début": debut.strftime("%Y-%m-%d %H:%M"),
                "Fin": fin.strftime("%Y-%m-%d %H:%M"),
                "Train": train.nom,
                "Type": t(train.type, lang) if hasattr(train, "type") else "",
                "Électrique": "⚡" if getattr(train, "electrique", False) else "",
            })
        df_gantt_a = pd.DataFrame(data_gantt_a)
        csv_gantt_a = df_gantt_a.to_csv(index=False, sep=";").encode('utf-8')  # <-- AJOUTE sep=";"
        st.download_button(
            label="📥 Télécharger le planning Gantt Glostrup (CSV)",
            data=csv_gantt_a,
            file_name="planning_gantt_glostrup.csv",
            mime="text/csv"
        )

    # Gantt Naestved
    with sous_tab_gantt_b:
        st.markdown(f"### {t('Planning', lang)} - {t('Depot de Naestved', lang)}")
        fig_gantt_b = creer_gantt_occupation_depot(
            st.session_state.simulation, "Naestved", t, lang
        )
        st.plotly_chart(fig_gantt_b, use_container_width=True)
        # Export Gantt Naestved
        data_gantt_b = []
        for voie_idx, debut, fin, train in st.session_state.simulation.occupation_b:
            data_gantt_b.append({
                "Voie": st.session_state.simulation.numeros_voies_b[voie_idx],
                "Début": debut.strftime("%Y-%m-%d %H:%M"),
                "Fin": fin.strftime("%Y-%m-%d %H:%M"),
                "Train": train.nom,
                "Type": t(train.type, lang) if hasattr(train, "type") else "",
                "Électrique": "⚡" if getattr(train, "electrique", False) else "",
            })
        df_gantt_b = pd.DataFrame(data_gantt_b)
        csv_gantt_b = df_gantt_b.to_csv(index=False, sep=";").encode('utf-8')  # <-- AJOUTE sep=";"
        st.download_button(
            label="📥 Télécharger le planning Gantt Naestved (CSV)",
            data=csv_gantt_b,
            file_name="planning_gantt_naestved.csv",
            mime="text/csv"
        )
        
# ---------------------------------------------------------------------------
# ONGLET 4 : STATISTIQUES GLOBALES
# ---------------------------------------------------------------------------

with tab4:
    st.subheader(t("Statistiques globales", lang))

    # Affichage sous forme de colonnes de métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=t("train_list", lang), value=stats['total_trains'])
        st.metric(label=t("Depot de Glostrup", lang), value=stats['trains_glostrup'])
        st.metric(label=t("Depot de Naestved", lang), value=stats['trains_naestved'])
    with col2:
        st.metric(label=t("electric_train", lang), value=stats['trains_electriques'])
        st.metric(label=t("average_wait", lang), value=f"{stats['temps_moyen_attente']} min")
    with col3:
        st.metric(label=t("occupancy_rate", lang), value=f"{stats['taux_occupation_global']}%")
        st.metric(label=f"{t('Depot de Glostrup', lang)}", value=f"{stats['taux_occupation_glostrup']}%")
        st.metric(label=f"{t('Depot de Naestved', lang)}", value=f"{stats['taux_occupation_naestved']}%")

    # Graphique de répartition des trains par dépôt
    import plotly.express as px
    depot_counts = [
        {"Depot": t("Depot de Glostrup", lang), "Trains": stats['trains_glostrup']},
        {"Depot": t("Depot de Naestved", lang), "Trains": stats['trains_naestved']}
    ]
    fig_depot = px.pie(depot_counts, names="Depot", values="Trains", title=t("train_list", lang))
    st.plotly_chart(fig_depot, use_container_width=True)

    # Graphique de répartition par type de train
    type_counts = {}
    for train in st.session_state.simulation.trains:
        type_label = t(train.type, lang)
        type_counts[type_label] = type_counts.get(type_label, 0) + 1
    if type_counts:
        fig_type = px.bar(
            x=list(type_counts.keys()),
            y=list(type_counts.values()),
            labels={"x": t("train_type", lang), "y": t("train_list", lang)},
            title=t("train_type", lang)
        )
        st.plotly_chart(fig_type, use_container_width=True)
    
# ---------------------------------------------------------------------------
# ONGLET 5 : REQUIREMENTS (BESOINS EN RESSOURCES)
# ---------------------------------------------------------------------------

with tab5:
    st.subheader(t("requirements", lang))
    requirements = calculer_requirements(st.session_state.simulation.trains, t, lang)
    requirements_par_jour = regrouper_requirements_par_jour(st.session_state.simulation.trains, t, lang)

    # Affichage global
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=t("test_drivers", lang), value=requirements["test_drivers"])
    with col2:
        st.metric(label=t("locomotives", lang), value=requirements["locomotives"])

    # Nouveau : Détail par type de train
    st.markdown("#### " + t("details", lang))
    details = []
    for train in st.session_state.simulation.trains:
        if train.type == "testing":
            details.append({
                t("train_name", lang): train.nom,
                t("train_type", lang): t(train.type, lang),
                t("arrival_time", lang): train.arrivee.strftime("%Y-%m-%d %H:%M"),
                t("departure_time", lang): train.depart.strftime("%Y-%m-%d %H:%M"),
                t("test_drivers", lang): 1,
                t("locomotives", lang): 2
            })
        # Ajoute ici d'autres types si besoin

    if details:
        st.dataframe(pd.DataFrame(details), use_container_width=True)
    else:
        st.info(t("no_requirements", lang))

    # Affichage par jour (déjà présent)
    if requirements_par_jour:
        st.write(f"### {t('requirements_by_day', lang)}")
        fig = creer_graphique_requirements_par_jour(requirements_par_jour, t, lang)
        st.plotly_chart(fig, use_container_width=True)

        # Tableau exportable par jour
        export_data = []
        for jour, besoins in sorted(requirements_par_jour.items()):
            for detail in besoins["details"]:
                export_data.append({
                    "Date": jour.strftime("%Y-%m-%d"),
                    t("train_name", lang): detail["train_name"],
                    t("arrival_time", lang): detail["start_time"],
                    t("departure_time", lang): detail["end_time"],
                    t("test_drivers", lang): besoins["test_drivers"],
                    t("locomotives", lang): besoins["locomotives"]
                })
        df_export = pd.DataFrame(export_data)
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False, sep=";", encoding="utf-8")
        st.download_button(
            label="📥 Télécharger les besoins (CSV)",
            data=csv_buffer.getvalue().encode("utf-8"),
            file_name="besoins_trains.csv",
            mime="text/csv"
        )
    else:
        st.info(t("no_requirements", lang))
        
# ---------------------------------------------------------------------------
# ONGLET 6 : MINI-JEU DE GESTION DES VOIES
# ---------------------------------------------------------------------------

with tab6:
    import Jeu
    Jeu.main(lang)





