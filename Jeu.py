# -*- coding: utf-8 -*-
"""
Created on Thu May  8 16:11:46 2025

@author: andre
"""
#lol
import streamlit as st
import plotly.graph_objects as go
from Traduction import t, get_translation

def main(lang):
    # Initialisation des voies et des wagons
    if "voies_glostrup" not in st.session_state:
        st.session_state.voies_glostrup = {7: [], 8: [], 9: [], 11: []}
        st.session_state.wagon_id = 1
        st.session_state.locomotive_id = 1
        st.session_state.element_id = 1

    def afficher_voies():
        """
        Affiche les voies et les wagons/locomotives sous forme de graphique interactif.
        """
        couleurs_wagon = {
        "1": "blue",
        "2": "orange",
        "3": "green",
        "4": "purple",
        "2a": "red",
        "3a": "brown"
        }
        fig = go.Figure()
        for voie, elements in st.session_state.voies_glostrup.items():
            position_actuelle = 0
            for element in elements:
                if element["type"] == "wagon":
                    type_wagon = element.get("type_wagon", "")
                    couleur = couleurs_wagon.get(type_wagon, "gray")
                    motif = None
                    longueur = 14
                    # Afficher le numéro du wagon sur la barre (en annotation)
                    label = f"{t('wagon', lang)} {element['id']} ({type_wagon})"
                    text = str(element['id'])
                else:  # Locomotive
                    couleur = "red"
                    motif = "x"
                    longueur = 19
                    label = f"{t('locomotive', lang)} {element['id']}"
                    text = str(element['id'])
                fig.add_trace(go.Bar(
                    x=[longueur],
                    y=[f"{t('Track', lang)} {voie}"],
                    base=position_actuelle,
                    orientation='h',
                    marker=dict(color=couleur, pattern=dict(shape=motif), line=dict(color="black", width=1)),
                    name=label,
                    text=text,  # Affiche le numéro du wagon sur la barre
                    textposition="inside",
                    hovertemplate=f"{label}<br>{t('Track', lang)}: {voie}<extra></extra>"
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

    def verifier_regles_wagons(elements):
        """
        Vérifie les règles d'enchaînement des wagons sur une voie.
        - Il doit toujours y avoir un wagon type 3 ou 3a adjacent à un wagon type 4.
        - À partir d’un wagon type 4, il doit y avoir un enchaînement wagon 2 puis 3, ou 3 puis 2.
        """
        types = [e.get("type_wagon") for e in elements if e["type"] == "wagon"]
        n = len(types)
        for i, t_w in enumerate(types):
            if t_w == "4":
                voisin_gauche = types[i-1] if i > 0 else None
                voisin_droite = types[i+1] if i < n-1 else None
                if not (
                    (voisin_gauche in ("3", "3a")) or
                    (voisin_droite in ("3", "3a"))
                ):
                    return False
                # Règle d'enchaînement après un 4
                if i+2 < n:
                    suite = types[i+1:i+3]
                    if not (suite == ["2", "3"] or suite == ["3", "2"]):
                        return False
        return True

    def ajouter_wagon(voie, type_wagon):
        """
        Ajoute un wagon à une voie spécifique avec vérification des règles.
        """
        if voie in st.session_state.voies_glostrup:
            elements = st.session_state.voies_glostrup[voie]
            longueur_totale = sum(14 if e["type"] == "wagon" else 19 for e in elements)
            # Cas spécial pour 2 wagons d'un coup
            if type_wagon in ["2+3", "3+2", "2a+3a", "3a+2a"]:
                types = type_wagon.replace("a+", "a+").split("+")
                if longueur_totale + 28 > 300:
                    st.warning(t("track_full_warning", lang))
                    return
                new_wagon1 = {
                    "id": st.session_state.element_id,
                    "type": "wagon",
                    "type_wagon": types[0]
                }
                st.session_state.element_id += 1
                new_wagon2 = {
                    "id": st.session_state.element_id,
                    "type": "wagon",
                    "type_wagon": types[1]
                }
                st.session_state.element_id += 1
                elements.extend([new_wagon1, new_wagon2])
                if not verifier_regles_wagons(elements):
                    elements.pop()
                    elements.pop()
                    st.error("Règle non respectée : il faut un wagon 3 ou 3a adjacent à un 4, et un enchaînement 2-3 ou 3-2 après un 4.")
                    return
                st.session_state.wagon_id += 2
                st.rerun()
            else:
                if longueur_totale + 14 > 300:
                    st.warning(t("track_full_warning", lang))
                    return
                new_wagon = {
                    "id": st.session_state.element_id,
                    "type": "wagon",
                    "type_wagon": type_wagon
                }
                elements.append(new_wagon)
                st.session_state.element_id += 1
                if not verifier_regles_wagons(elements):
                    elements.pop()
                    st.error("Règle non respectée : il faut un wagon 3 ou 3a adjacent à un 4, et un enchaînement 2-3 ou 3-2 après un 4.")
                    return
                st.session_state.wagon_id += 1
                st.rerun()
            
    def ajouter_locomotive(voie):
        """
        Ajoute une locomotive à une voie spécifique.
        """
        if voie in st.session_state.voies_glostrup:
            st.session_state.voies_glostrup[voie].append({
            "id": st.session_state.element_id,
                    "type": "locomotive"
                })
            st.session_state.element_id += 1
            st.rerun()

    def deplacer_wagon(voie_source, wagon_id, voie_cible):
        """
        Déplace un wagon d'une voie source à une voie cible.
        Seul le wagon à l'extrémité gauche (premier wagon) peut être déplacé.
        """
        elements_source = st.session_state.voies_glostrup[voie_source]
        if elements_source and elements_source[0]["type"] == "wagon" and elements_source[0]["id"] == wagon_id:
            wagon = elements_source.pop(0)
            st.session_state.voies_glostrup[voie_cible].append(wagon)
            st.rerun()
        else:
            st.error("Seul le wagon à l'extrémité gauche de la voie peut être déplacé.")

    def supprimer_element(voie, element_id):
        st.session_state.voies_glostrup[voie] = [
            e for e in st.session_state.voies_glostrup[voie] if e["id"] != element_id
        ]
        st.rerun()

    def reset_state():
        """
        Réinitialise complètement l'état de l'application.
        """
        st.session_state.voies_glostrup = {7: [], 8: [], 9: [], 11: []}
        # Supprimer les clés pour éviter le conflit avec les widgets
        for key in ["wagon_id", "locomotive_id", "type_wagon", "ajout_voie", "ajout_loco", "supp_voie", "supp_id", "source_voie", "cible_voie"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.last_action = None
        st.rerun()

    st.subheader(t("graph_title1", lang))
    afficher_voies()

    # --- Interface compacte avec colonnes ---

    # Ligne pour ajouter un wagon
    st.markdown("### " + t("add_coach", lang))
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        voie_ajout = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="ajout_voie")
    with col2:
        type_wagon = st.selectbox("Type de wagon",options=["1", "2", "3", "4", "2a", "3a", "2+3", "3+2","2a+3a", "3a+2a"],
            key="type_wagon"
        )
    with col3:
        if st.button(t("add_coach", lang), key="btn_add_wagon"):
            ajouter_wagon(voie_ajout, type_wagon)
            st.session_state.last_action = "add_coach"

    # Ligne pour ajouter une locomotive
    st.markdown("### " + t("add_locomotive", lang))
    col4, col5 = st.columns([3, 1])
    with col4:
        voie_loco = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="ajout_loco")
    with col5:
        if st.button(t("add_locomotive", lang), key="btn_add_loco"):
            ajouter_locomotive(voie_loco)
            st.session_state.last_action = "add_locomotive"
            
    # Ligne pour ajouter un train entier prédéfini


    def ajouter_train_predefini(voie):
        """
        Ajoute un train entier prédéfini sur la voie choisie :
        locomotive,1,2a,3a,4,3,2,3,2,3,2,3,2,3,2,locomotive
        """
        if voie in st.session_state.voies_glostrup:
            elements = st.session_state.voies_glostrup[voie]
            longueur_totale = sum(14 if e["type"] == "wagon" else 19 for e in elements)
            # Séquence du train
            sequence = [
                ("locomotive", None),
                ("wagon", "1"),
                ("wagon", "2a"),
                ("wagon", "3a"),
                ("wagon", "4"),
                ("wagon", "3"),
                ("wagon", "2"),
                ("wagon", "3"),
                ("wagon", "2"),
                ("wagon", "3"),
                ("wagon", "2"),
                ("wagon", "3"),
                ("wagon", "2"),
                ("wagon", "3"),
                ("wagon", "2"),
                ("locomotive", None)
            ]
            longueur_train = sum(19 if t == "locomotive" else 14 for t, _ in sequence)
            if longueur_totale + longueur_train > 300:
                st.warning(t("track_full_warning", lang))
                return
            nouveaux_elements = []
            for t_elem, type_wagon in sequence:
                if t_elem == "locomotive":
                    nouveaux_elements.append({
                        "id": st.session_state.element_id,
                        "type": "locomotive"
                    })
                    st.session_state.element_id += 1
                else:
                    nouveaux_elements.append({
                        "id": st.session_state.element_id,
                        "type": "wagon",
                        "type_wagon": type_wagon
                    })
                    st.session_state.element_id += 1
            elements.extend(nouveaux_elements)
            # Vérification des règles métier
            if not verifier_regles_wagons(elements):
            # On retire ce qu'on vient d'ajouter
                for _ in nouveaux_elements:
                    elements.pop()
                st.error("Règle non respectée : il faut un wagon 3 ou 3a adjacent à un 4, et un enchaînement 2-3 ou 3-2 après un 4.")
                return
            st.success("Train prédéfini ajouté avec succès.")
            st.rerun()
            
    st.markdown("### Ajouter un train entier prédéfini")
    col_train, col_btn = st.columns([3, 1])
    with col_train:
        voie_train = st.selectbox("Voie pour le train prédéfini", options=[7, 8, 9, 11], key="voie_train_predef")
    with col_btn:
        if st.button("Ajouter le train prédéfini", key="btn_add_predef_train"):
            ajouter_train_predefini(voie_train)
            st.session_state.last_action = "add_predef_train"

    # Ligne pour supprimer un élément
    st.markdown("### " + t("delete_element", lang))
    col6, col7, col8 = st.columns([2, 2, 1])
    with col6:
        voie_supp = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="supp_voie")
    with col7:
        element_id = st.number_input(t("element_id", lang), min_value=1, step=1, key="supp_id")
    with col8:
        if st.button(t("delete", lang), key="btn_delete"):
            supprimer_element(voie_supp, element_id)
            st.session_state.last_action = "delete_element"

    # Ligne pour déplacer un wagon
    st.markdown("### " + t("move_wagon", lang))
    col9, col10, col11, col12 = st.columns([2, 2, 2, 1])
    with col9:
        voie_source = st.selectbox(t("select_source_track", lang), options=[7, 8, 9, 11], key="source_voie")
    with col10:
        wagon_id = st.number_input(t("wagon_id", lang), min_value=1, step=1, key="wagon_id")
    with col11:
        voie_cible = st.selectbox(t("select_target_track", lang), options=[7, 8, 9, 11], key="cible_voie")
    with col12:
        if st.button(t("move", lang), key="btn_move"):
            deplacer_wagon(voie_source, wagon_id, voie_cible)
            st.session_state.last_action = "move_wagon"

    # Ligne pour réinitialiser le jeu
    st.markdown("### " + t("reset_game", lang))
    if st.button(t("reset_game", lang), key="btn_reset"):
        reset_state()
        st.rerun()