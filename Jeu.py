# -*- coding: utf-8 -*-
"""
Created on Thu May  8 16:11:46 2025

@author: andre
"""

import streamlit as st
import plotly.graph_objects as go
from Traduction import t, get_translation

def main(lang):
    # Initialisation des voies et des wagons
    if "voies_glostrup" not in st.session_state:
        st.session_state.voies_glostrup = {7: [], 8: [], 9: [], 11: []}
        st.session_state.wagon_id = 1
        st.session_state.locomotive_id = 1
        
    

    def afficher_voies():
        """
        Affiche les voies et les wagons/locomotives sous forme de graphique interactif.
        """
        fig = go.Figure()

        for voie, elements in st.session_state.voies_glostrup.items():
            position_actuelle = 0
            for element in elements:
                if element["type"] == "wagon":
                    couleur = "blue"
                    motif = None
                    longueur = 14
                else:  # Locomotive
                    couleur = "red"
                    motif = "x"
                    longueur = 19

                fig.add_trace(go.Bar(
                    x=[longueur],
                    y=[f"{t('Track', lang)} {voie}"],
                    base=position_actuelle,
                    orientation='h',
                    marker=dict(color=couleur, pattern=dict(shape=motif), line=dict(color="black", width=1)),
                    name=f"{t(element['type'], lang)} {element['id']}",
                    hovertemplate=f"{t(element['type'], lang)} {element['id']}<br>{t('Track', lang)}: {voie}<extra></extra>"
                ))
                position_actuelle += longueur

        fig.update_layout(
            title=t("graph_title", lang),
            xaxis_title=t("length", lang),
            yaxis_title=t("Track", lang),
            height=400,
            margin=dict(l=40, r=40, t=40, b=80),
            barmode='stack'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    # Afficher les voies en haut de la page
    st.subheader(t("graph_title1", lang))
    afficher_voies()  # Appel fixe pour afficher le graphique

    def ajouter_wagon(voie):
        """
        Ajoute un wagon à une voie spécifique.
        """
        if voie in st.session_state.voies_glostrup:
            longueur_totale = sum(14 if e["type"] == "wagon" else 19 for e in st.session_state.voies_glostrup[voie])
            if longueur_totale + 14 > 300:  # Exemple de limite
                st.warning("La voie est pleine, impossible d'ajouter un wagon.")
                return
            st.session_state.voies_glostrup[voie].append({
                "id": st.session_state.wagon_id,
                "type": "wagon"
            })
            st.session_state.wagon_id += 1
            #st.rerun()
           

    def ajouter_locomotive(voie):
        """
        Ajoute une locomotive à une voie spécifique.
        """
        if voie in st.session_state.voies_glostrup:
            st.session_state.voies_glostrup[voie].append({
                "id": st.session_state.locomotive_id,
                "type": "locomotive"
            })
            st.session_state.locomotive_id += 1
            #st.rerun()   

    def deplacer_wagon(voie_source, wagon_id, voie_cible):
        """
        Déplace un wagon d'une voie source à une voie cible.
        """
        for element in st.session_state.voies_glostrup[voie_source]:
            if element["id"] == wagon_id and element["type"] == "wagon":
                st.session_state.voies_glostrup[voie_source].remove(element)
                st.session_state.voies_glostrup[voie_cible].append(element)
                #st.rerun()
                break

    def supprimer_element(voie, element_id):
        st.session_state.voies_glostrup[voie] = [
            e for e in st.session_state.voies_glostrup[voie] if e["id"] != element_id
        ]
        #st.rerun()
        
    def reset_state():
        """
        Réinitialise complètement l'état de l'application.
        """
        st.session_state.voies_glostrup = {7: [], 8: [], 9: [], 11: []}
        st.session_state.wagon_id = 1
        st.session_state.locomotive_id = 1
        st.session_state.last_action = None

    # Afficher les voies
    #st.subheader("graph_title")
    #afficher_voies()
    
    # Ajouter un wagon
    st.subheader(t("add_coach", lang))
    voie_ajout = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="ajout_voie")
    if st.button(t("add_coach", lang)):
        ajouter_wagon(voie_ajout)
        st.session_state.last_action = "add_coach"

    # Ajouter une locomotive
    st.subheader(t("add_locomotive", lang))
    voie_loco = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="ajout_loco")
    if st.button(t("add_locomotive", lang)):
        ajouter_locomotive(voie_loco)
        st.session_state.last_action = "add_locomotive"

    # Supprimer un élément
    st.subheader(t("delete_element", lang))
    voie_supp = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="supp_voie")
    element_id = st.number_input(t("element_id", lang), min_value=1, step=1, key="supp_id")
    if st.button(t("delete", lang)):
        supprimer_element(voie_supp, element_id)
        st.session_state.last_action = "delete_element"

    # Déplacer un wagon
    st.subheader(t("move_wagon", lang))
    col1, col2, col3 = st.columns(3)
    with col1:
        voie_source = st.selectbox(t("select_source_track", lang), options=[7, 8, 9, 11], key="source_voie")
    with col2:
        wagon_id = st.number_input(t("wagon_id", lang), min_value=1, step=1, key="wagon_id")
    with col3:
        voie_cible = st.selectbox(t("select_target_track", lang), options=[7, 8, 9, 11], key="cible_voie")
    if st.button(t("move", lang)):
        deplacer_wagon(voie_source, wagon_id, voie_cible)
        st.session_state.last_action = "move_wagon"

    # Réinitialiser le jeu
    if st.button(t("reset_game", lang)):
        reset_state()
        st.rerun()