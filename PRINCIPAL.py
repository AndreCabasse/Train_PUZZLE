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
from Plots import creer_graphique_occupation_depot, creer_graphique_requirements_par_jour, creer_graphique_trains_par_longueur_detaille, creer_gantt_occupation_depot
import pandas as pd
import io

# Configuration de la page
st.set_page_config(layout="wide")

# Initialisation
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()
    st.session_state.base_time = datetime.combine(datetime.now().date(), datetime.min.time())

lang = st.sidebar.selectbox("Langue", ["fr", "en", "da"])
t_dict = get_translation(lang)

#def t(key, **kwargs):
#    return t_dict.get(key, {}).get(lang, key).format(**kwargs)

st.title(t("title", lang))

# Ajout d'un champ pour ajuster le délai de sécurité
st.sidebar.subheader(t("security_settings", lang))
delai_securite = st.sidebar.slider(
    t("security_delay", lang), min_value=0, max_value=30, value=10, step=1
)
st.session_state.simulation.delai_securite = delai_securite

if st.sidebar.button(t("reset", lang)):
    st.session_state.simulation.reset()
    #st.session_state.voies_glostrup = {7: [], 8: [], 9: [], 11: []}
    #st.session_state.wagon_id = 1
    #st.session_state.locomotive_id = 1
    st.success(t("simulation_reset", lang))
    st.rerun()

stats = calculer_statistiques_globales(st.session_state.simulation)

# Organisation en onglets
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("add_train", lang), t("train_list", lang), t("graph_title", lang), t("Statistiques", lang), t("requirements", lang), t("Gestion des voies", lang)])

with tab1:
    afficher_formulaire_ajout(st.session_state.simulation, lang, t)
    afficher_modification_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)
    afficher_suppression_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)

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

with tab3:
    # Statistiques globales
    temps_moyen = calculer_temps_moyen_attente(st.session_state.simulation.trains)
    taux_occupation = calculer_taux_occupation(
    st.session_state.simulation.occupation_a + st.session_state.simulation.occupation_b,
    st.session_state.simulation.numeros_voies_a + st.session_state.simulation.numeros_voies_b
)
    # Graphique pour le dépôt A
    st.subheader(t("Depot de Glostrup", lang))
    fig_a = creer_graphique_occupation_depot(
        st.session_state.simulation, "Glostrup", st.session_state.base_time, t, lang
    )
    st.plotly_chart(fig_a, use_container_width=True)

    # Graphique pour le dépôt B
    st.subheader(t("Depot Naestved", lang))
    fig_b = creer_graphique_occupation_depot(
        st.session_state.simulation, "Naestved", st.session_state.base_time, t, lang
    )
    st.plotly_chart(fig_b, use_container_width=True)
    
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
    
    csv = df_occ.to_csv(index=False).encode('utf-8')
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
    
    # Sélecteurs pour choisir une date et une heure spécifiques
    col1, col2 = st.columns(2)
    with col1:
        date_instant = st.date_input(t("base_date", lang), st.session_state.base_time.date(), key="date_instant")
    with col2:
        heure_instant = st.time_input(t("base_time", lang), st.session_state.base_time.time(), key="heure_instant")

    # Combiner la date et l'heure pour obtenir l'instant spécifique
    instant = datetime.combine(date_instant, heure_instant)

    # Afficher le graphique pour l'instant sélectionné
    fig_trains_instant = creer_graphique_trains_par_longueur_detaille(
        st.session_state.simulation, t, instant, lang
    )
    st.plotly_chart(fig_trains_instant, use_container_width=True)
    
    # Planning Gantt pour Glostrup
    st.markdown(f"### {t('Planning', lang)} - {t('Depot de Glostrup', lang)}")
    fig_gantt_a = creer_gantt_occupation_depot(
        st.session_state.simulation, "Glostrup", t, lang
    )
    st.plotly_chart(fig_gantt_a, use_container_width=True)
    
    # On récupère les données du Gantt
    from io import BytesIO
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
    csv_gantt_a = df_gantt_a.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger le planning Gantt Glostrup (CSV)",
        data=csv_gantt_a,
        file_name="planning_gantt_glostrup.csv",
        mime="text/csv"
    )

    # Planning Gantt pour Naestved
    st.markdown(f"### {t('Planning', lang)} - {t('Depot de Naestved', lang)}")
    fig_gantt_b = creer_gantt_occupation_depot(
        st.session_state.simulation, "Naestved", t, lang
    )
    st.plotly_chart(fig_gantt_b, use_container_width=True)
    
    # Téléchargement du planning Gantt Naestved
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
    csv_gantt_b = df_gantt_b.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger le planning Gantt Naestved (CSV)",
        data=csv_gantt_b,
        file_name="planning_gantt_naestved.csv",
        mime="text/csv"
        )
with tab4:
    st.subheader(t("Statistiques globales", lang))
    st.write(f"- {t('train_list', lang)}: {stats['total_trains']}")
    st.write(f"- {t('Depot de Glostrup', lang)}: {stats['trains_glostrup']} trains")
    st.write(f"- {t('Depot de Naestved', lang)}: {stats['trains_naestved']} trains")
    st.write(f"- {t('electric_train', lang)}: {stats['trains_electriques']} trains")
    st.write(f"- {t('average_wait', lang)}: {stats['temps_moyen_attente']} min")
    st.write(f"- {t('occupancy_rate', lang)}: {stats['taux_occupation_global']}%")
    st.write(f"  - {t('Depot de Glostrup', lang)}: {stats['taux_occupation_glostrup']}%")
    st.write(f"  - {t('Depot de Naestved', lang)}: {stats['taux_occupation_naestved']}%")
    
# Onglet Requirements
with tab5:
    st.subheader(t("requirements", lang))
    requirements = calculer_requirements(st.session_state.simulation.trains, t, lang)
    requirements_par_jour = regrouper_requirements_par_jour(st.session_state.simulation.trains, t, lang)

    # Afficher les besoins globaux
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=t("test_drivers", lang), value=requirements["test_drivers"])
    with col2:
        st.metric(label=t("locomotives", lang), value=requirements["locomotives"])

    # Afficher les besoins par jour sous forme de diagramme en barres
    if requirements_par_jour:
        st.write(f"### {t('requirements_by_day', lang)}")
        fig = creer_graphique_requirements_par_jour(requirements_par_jour, t, lang)
        st.plotly_chart(fig, use_container_width=True)

        # Affichage détaillé par jour
        for jour, besoins in sorted(requirements_par_jour.items()):
            st.markdown(f"**{jour.strftime('%A %d/%m/%Y')}**")
            st.write(f"- {t('test_drivers', lang)}: {besoins['test_drivers']}")
            st.write(f"- {t('locomotives', lang)}: {besoins['locomotives']}")
            if besoins["details"]:
                st.write(f"{t('details', lang)}:")
                df_details = pd.DataFrame(besoins["details"])
                df_details.rename(columns={
                    "train_name": t("train_name", lang),
                    "start_time": t("arrival_time", lang),
                    "end_time": t("departure_time", lang)
                }, inplace=True)
                st.dataframe(df_details, hide_index=True, use_container_width=True)
            st.markdown("---")
    else:
        st.info(t("no_requirements", lang))
        
# Onglet pour le jeu
with tab6:
    import Jeu
    Jeu.main(lang)





