# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:54:24 2025

@author: andre
"""

import streamlit as st
from datetime import datetime, timedelta
from Simulation import Simulation
from Traduction import t, get_translation
from Interface import afficher_formulaire_ajout, afficher_tableau_trains, afficher_modification_train, afficher_suppression_train
from Stats import calculer_temps_moyen_attente, calculer_taux_occupation, calculer_statistiques_globales, calculer_requirements, regrouper_requirements_par_jour
from Plots import creer_graphique_occupation_depot, creer_graphique_requirements_par_jour, creer_graphique_trains_par_longueur_detaille
import pandas as pd

# Configuration de la page
st.set_page_config(layout="wide")

# Initialisation
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()
    st.session_state.base_time = datetime.combine(datetime.now().date(), datetime.min.time())

lang = st.sidebar.selectbox("Langue", ["fr", "en", "da"])
t_dict = get_translation(lang)

def t(key, **kwargs):
    return t_dict.get(key, {}).get(lang, key).format(**kwargs)

st.title(t("title"))

# Ajout d'un champ pour ajuster le délai de sécurité
st.sidebar.subheader(t("security_settings"))
delai_securite = st.sidebar.slider(
    t("security_delay"), min_value=0, max_value=30, value=10, step=1
)
st.session_state.simulation.delai_securite = delai_securite

if st.sidebar.button(t("reset")):
    st.session_state.simulation.reset()
    st.success(t("simulation_reset"))
    st.rerun()

stats = calculer_statistiques_globales(st.session_state.simulation)


# Affichage des statistiques dans la barre latérale
st.sidebar.write("### Statistiques globales")
st.sidebar.write(f"- {t('train_list')}: {stats['total_trains']}")
st.sidebar.write(f"- {t('Depot de Glostrup')}: {stats['trains_glostrup']} trains")
st.sidebar.write(f"- {t('Depot de Naestved')}: {stats['trains_naestved']} trains")
st.sidebar.write(f"- {t('electric_train')}: {stats['trains_electriques']} trains")
st.sidebar.write(f"- {t('average_wait')}: {stats['temps_moyen_attente']} min")
st.sidebar.write(f"- {t('occupancy_rate')}: {stats['taux_occupation_global']}%")
st.sidebar.write(f"  - {t('Depot de Glostrup')}: {stats['taux_occupation_glostrup']}%")
st.sidebar.write(f"  - {t('Depot de Naestved')}: {stats['taux_occupation_naestved']}%")


# Organisation en onglets
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("add_train"), t("train_list"), t("graph_title"), t("Statistiques"), t("requirements"), "Jeu : Gestion des voies"
])

with tab1:
    afficher_formulaire_ajout(st.session_state.simulation, lang, t)
    afficher_modification_train(st.session_state.simulation.trains, st.session_state.simulation, t)
    afficher_suppression_train(st.session_state.simulation.trains, st.session_state.simulation, t)

with tab2:
    # Tableau pour le dépôt A
    st.subheader(t("Depot de Glostrup"))
    afficher_tableau_trains(
        [train for train in st.session_state.simulation.trains if train.depot == "Glostrup"],
        st.session_state.simulation,
        t
    )

    # Tableau pour le dépôt B
    st.subheader(t("Depot de Naestved"))
    afficher_tableau_trains(
        [train for train in st.session_state.simulation.trains if train.depot == "Naestved"],
        st.session_state.simulation,
        t
    )

with tab3:
    # Statistiques globales
    temps_moyen = calculer_temps_moyen_attente(st.session_state.simulation.trains)
    taux_occupation = calculer_taux_occupation(
    st.session_state.simulation.occupation_a + st.session_state.simulation.occupation_b,
    st.session_state.simulation.numeros_voies_a + st.session_state.simulation.numeros_voies_b
)
    st.markdown(f"Temps moyen d'attente : {temps_moyen} min | Taux d'occupation : {taux_occupation}%")

    # Graphique pour le dépôt A
    st.subheader(t("Depot de Glostrup"))
    fig_a = creer_graphique_occupation_depot(
        st.session_state.simulation, "Glostrup", st.session_state.base_time, t
    )
    st.plotly_chart(fig_a, use_container_width=True)

    # Graphique pour le dépôt B
    st.subheader(t("Depot Naestved"))
    fig_b = creer_graphique_occupation_depot(
        st.session_state.simulation, "Naestved", st.session_state.base_time, t
    )
    st.plotly_chart(fig_b, use_container_width=True)
    
    # Sélecteurs pour choisir une date et une heure spécifiques
    col1, col2 = st.columns(2)
    with col1:
        date_instant = st.date_input(t("base_date"), st.session_state.base_time.date(), key="date_instant")
    with col2:
        heure_instant = st.time_input(t("base_time"), st.session_state.base_time.time(), key="heure_instant")

    # Combiner la date et l'heure pour obtenir l'instant spécifique
    instant = datetime.combine(date_instant, heure_instant)

    # Afficher le graphique pour l'instant sélectionné
    fig_trains_instant = creer_graphique_trains_par_longueur_detaille(
        st.session_state.simulation, t, instant
    )
    st.plotly_chart(fig_trains_instant, use_container_width=True)
    
with tab4:
    st.subheader(t("Statistiques globales"))
    st.write(f"- {t('train_list')}: {stats['total_trains']}")
    st.write(f"- {t('Depot de Glostrup')}: {stats['trains_glostrup']} trains")
    st.write(f"- {t('Depot de Naestved')}: {stats['trains_naestved']} trains")
    st.write(f"- {t('electric_train')}: {stats['trains_electriques']} trains")
    st.write(f"- {t('average_wait')}: {stats['temps_moyen_attente']} min")
    st.write(f"- {t('occupancy_rate')}: {stats['taux_occupation_global']}%")
    st.write(f"  - {t('Depot de Glostrup')}: {stats['taux_occupation_glostrup']}%")
    st.write(f"  - {t('Depot de Naestved')}: {stats['taux_occupation_naestved']}%")
    
# Onglet Requirements
with tab5:
    st.subheader(t("requirements"))
    requirements = calculer_requirements(st.session_state.simulation.trains, t)
    requirements_par_jour = regrouper_requirements_par_jour(st.session_state.simulation.trains, t)

    # Afficher les besoins globaux
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=t("test_drivers"), value=requirements["test_drivers"])
    with col2:
        st.metric(label=t("locomotives"), value=requirements["locomotives"])

    # Afficher les besoins par jour sous forme de diagramme en barres
    if requirements_par_jour:
        st.write(f"### {t('requirements_by_day')}")
        fig = creer_graphique_requirements_par_jour(requirements_par_jour, t)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t("no_requirements"))
        
# Onglet pour le jeu
with tab6:
    import Jeu
    Jeu.main(lang)





