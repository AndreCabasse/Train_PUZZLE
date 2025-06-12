# -*- coding: utf-8 -*-
"""
Created on Thu May  8 16:11:46 2025

@author: andre
"""
import streamlit as st
import plotly.graph_objects as go
from Traduction import t, get_translation

def main(lang):
    # FR : Initialisation des voies et des compteurs d'identifiants dans la session Streamlit
    # EN : Initialize tracks and ID counters in Streamlit session state
    if "voies_glostrup" not in st.session_state:
        st.session_state.voies_glostrup = {7: [], 8: [], 9: [], 11: []}
    if "wagon_id" not in st.session_state:
        st.session_state.wagon_id = 1
    if "locomotive_id" not in st.session_state:
        st.session_state.locomotive_id = 1
    if "element_id" not in st.session_state:
        st.session_state.element_id = 1

    def afficher_voies():
        """
        FR : Affiche les voies et les wagons/locomotives sous forme de graphique interactif Plotly.
        EN : Display tracks and wagons/locomotives as an interactive Plotly chart.
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
            position_actuelle = 0  # FR : Position de départ sur la voie / EN : Start position on the track
            for element in elements:
                if element["type"] == "wagon":
                    type_wagon = element.get("type_wagon", "")
                    couleur = couleurs_wagon.get(type_wagon, "gray")
                    motif = None
                    longueur = 14
                    label = f"{t('wagon', lang)} {element['id']} ({type_wagon})"
                    text = str(element['id'])
                else:  # Locomotive
                    couleur = "red"
                    motif = "x"
                    longueur = 19
                    label = f"{t('locomotive', lang)} {element['id']}"
                    text = str(element['id'])
                # FR : Ajoute chaque élément comme une barre horizontale
                # EN : Add each element as a horizontal bar
                fig.add_trace(go.Bar(
                    x=[longueur],
                    y=[f"{t('Track', lang)} {voie}"],
                    base=position_actuelle,
                    orientation='h',
                    marker=dict(color=couleur, pattern=dict(shape=motif), line=dict(color="black", width=1)),
                    name=label,
                    text=text,
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
        FR : Vérifie les règles d'enchaînement des wagons sur une voie.
        - Il doit toujours y avoir un wagon type 3 ou 3a adjacent à un wagon type 4.
        - Après un wagon type 4, il doit y avoir un enchaînement 2-3 ou 3-2.
        EN : Check wagon sequence rules on a track.
        - There must always be a type 3 or 3a wagon adjacent to a type 4.
        - After a type 4, there must be a 2-3 or 3-2 sequence.
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
                # FR : Vérifie la séquence après un 4 / EN : Check sequence after a 4
                if i+2 < n:
                    suite = types[i+1:i+3]
                    if not (suite == ["2", "3"] or suite == ["3", "2"]):
                        return False
        return True

    def ajouter_wagon(voie, type_wagon):
        """
        FR : Ajoute un wagon à une voie spécifique avec vérification des règles.
        L'ajout se fait toujours à gauche (début de la liste).
        EN : Add a wagon to a specific track with rule checking.
        Always added to the left (start of the list).
        """
        if voie in st.session_state.voies_glostrup:
            elements = st.session_state.voies_glostrup[voie]
            longueur_totale = sum(14 if e["type"] == "wagon" else 19 for e in elements)
            # FR : Cas spécial pour 2 wagons d'un coup (ex: "2+3")
            # EN : Special case for adding 2 wagons at once (e.g., "2+3")
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
                elements.insert(0, new_wagon2)
                elements.insert(0, new_wagon1)
                if not verifier_regles_wagons(elements):
                    elements.pop(0)
                    elements.pop(0)
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
                elements.insert(0, new_wagon)
                st.session_state.element_id += 1
                if not verifier_regles_wagons(elements):
                    elements.pop(0)
                    st.error("Règle non respectée : il faut un wagon 3 ou 3a adjacent à un 4, et un enchaînement 2-3 ou 3-2 après un 4.")
                    return
                st.session_state.wagon_id += 1
                st.rerun()
            
    def ajouter_locomotive(voie):
        """
        FR : Ajoute une locomotive à une voie spécifique.
        EN : Add a locomotive to a specific track.
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
        FR : Déplace un wagon d'une voie source à une voie cible.
        Seul le wagon à l'extrémité gauche ou droite peut être déplacé.
        EN : Move a wagon from a source track to a target track.
        Only a wagon at the left or right end can be moved.
        """
        elements_source = st.session_state.voies_glostrup[voie_source]
        idx = next((i for i, e in enumerate(elements_source) if e["id"] == wagon_id and e["type"] == "wagon"), None)
        if idx is None:
            st.error("Seuls les wagons peuvent être déplacés ici.")
            return
        if idx != 0 and idx != len(elements_source) - 1:
            st.error("Vous ne pouvez déplacer qu'un wagon à une extrémité de la voie.")
            return
        wagon = elements_source.pop(idx)
        st.session_state.voies_glostrup[voie_cible].append(wagon)
        st.rerun()
    
    def supprimer_element(voie, element_id):
        """
        FR : Supprime un wagon à une extrémité d'une voie.
        EN : Remove a wagon at the end of a track.
        """
        elements = st.session_state.voies_glostrup[voie]
        idx = next((i for i, e in enumerate(elements) if e["id"] == element_id and e["type"] == "wagon"), None)
        if idx is None:
            st.error("Seuls les wagons peuvent être supprimés ici.")
            return
        if idx != 0 and idx != len(elements) - 1:
            st.error("Vous ne pouvez supprimer qu'un wagon à une extrémité de la voie.")
            return
        st.session_state.voies_glostrup[voie] = [e for e in elements if e["id"] != element_id]
        st.rerun()

    def reset_state():
        """
        FR : Réinitialise complètement l'état du mini-jeu.
        EN : Completely reset the mini-game state.
        """
        st.session_state.voies_glostrup = {7: [], 8: [], 9: [], 11: []}
        for key in ["wagon_id", "locomotive_id", "type_wagon", "ajout_voie", "ajout_loco", "supp_voie", "supp_id", "source_voie", "cible_voie"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.last_action = None
        st.rerun()

    st.subheader(t("graph_title1", lang))
    
    # --- Légende des couleurs ---
    # FR : Légende des couleurs pour les types de wagons et locomotives
    # EN : Color legend for wagon and locomotive types
    couleurs_wagon = {
        "1": "blue",
        "2": "orange",
        "3": "green",
        "4": "purple",
        "2a": "red",
        "3a": "brown"
    }
    legend_items = [
        (t("wagon", lang) + " 1", "blue"),
        (t("wagon", lang) + " 2", "orange"),
        (t("wagon", lang) + " 3", "green"),
        (t("wagon", lang) + " 4", "purple"),
        (t("wagon", lang) + " 2a", "red"),
        (t("wagon", lang) + " 3a", "brown"),
        (t("locomotive", lang), "red"),
    ]
    st.markdown("#### " + t("legend", lang))
    legend_cols = st.columns(len(legend_items))
    for col, (label, color) in zip(legend_cols, legend_items):
        col.markdown(
            f'<div style="display:flex;align-items:center">'
            f'<div style="width:20px;height:20px;background:{color};border:1px solid #333;margin-right:8px"></div>'
            f'{label}'
            f'</div>',
            unsafe_allow_html=True
        )

    afficher_voies()

    # --- FR : Interface compacte avec colonnes pour chaque action ---
    # --- EN : Compact interface with columns for each action ---

    # FR : Ligne pour ajouter un wagon
    # EN : Row to add a wagon
    st.markdown("### " + t("add_coach", lang))
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        voie_ajout = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="ajout_voie")
    with col2:
        type_wagon = st.selectbox(t("wagon_type", lang), options=["1", "2", "3", "4", "2a", "3a", "2+3", "3+2", "2a+3a", "3a+2a"], key="type_wagon")
    with col3:
        if st.button(t("add_coach", lang), key="btn_add_wagon"):
            ajouter_wagon(voie_ajout, type_wagon)
            st.session_state.last_action = "add_coach"

    # FR : Ligne pour ajouter une locomotive
    # EN : Row to add a locomotive
    st.markdown("### " + t("add_locomotive", lang))
    col4, col5 = st.columns([3, 1])
    with col4:
        voie_loco = st.selectbox(t("select_track", lang), options=[7, 8, 9, 11], key="ajout_loco")
    with col5:
        if st.button(t("add_locomotive", lang), key="btn_add_loco"):
            ajouter_locomotive(voie_loco)
            st.session_state.last_action = "add_locomotive"
            
    # FR : Ligne pour ajouter un train entier prédéfini
    # EN : Row to add a predefined full train

    def ajouter_train_predefini(voie):
        """
        FR : Ajoute un train entier prédéfini sur la voie choisie.
        EN : Add a predefined full train on the selected track.
        """
        if voie in st.session_state.voies_glostrup:
            elements = st.session_state.voies_glostrup[voie]
            longueur_totale = sum(14 if e["type"] == "wagon" else 19 for e in elements)
            # FR : Séquence prédéfinie de wagons et locomotives
            # EN : Predefined sequence of wagons and locomotives
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
            if not verifier_regles_wagons(elements):
                for _ in nouveaux_elements:
                    elements.pop()
                st.error(t("wagon_rule_error", lang))
                return
            st.success(t("predefined_train_added", lang))
            st.rerun()
            
    st.markdown("### " + t("add_predefined_train", lang))
    col_train, col_btn = st.columns([3, 1])
    with col_train:
        voie_train = st.selectbox(t("track_for_predefined_train", lang), options=[7, 8, 9, 11], key="voie_train_predef")
    with col_btn:
        if st.button(t("add_predefined_train", lang), key="btn_add_predef_train"):
            ajouter_train_predefini(voie_train)
            st.session_state.last_action = "add_predef_train"

    # FR : Ligne pour supprimer un élément (wagon à l'extrémité gauche uniquement)
    # EN : Row to remove an element (leftmost wagon only)
    st.markdown("### " + t("delete_element", lang))
    st.info(t("delete_left_only_info", lang))
    col6, col7, col8 = st.columns([2, 2, 1])
    with col6:
        voie_supp = st.selectbox(
            t("select_track", lang),
            options=[7, 8, 9, 11],
            key="supp_voie"
        )
    with col7:
        #elements = st.session_state.voies_glostrup[voie_supp]
        #wagon_gauche = None
        #if elements and elements[0]["type"] == "wagon":
        #    wagon_gauche = (elements[0]["id"], "gauche")
        elements = st.session_state.voies_glostrup[voie_supp]
        element_gauche = None
        for i, e in enumerate(elements):
            # FR : Propose le premier élément (wagon ou locomotive) à gauche
            # EN : Propose the first element (wagon or locomotive) at the left end
            if all(el["type"] == "locomotive" or el["type"] == "wagon" for el in elements[:i]):
                element_gauche = (e["id"], e["type"], "gauche")
                break
        if element_gauche:
            element_id, element_type, extremite = st.selectbox(
                t("element_to_delete_left", lang),
                options=[element_gauche],
                format_func=lambda x: f"{t(x[1], lang).capitalize()} {x[0]} (extrémité {x[2]})"
            )
        else:
            element_id, element_type, extremite = None, None, None
    with col8:
        if st.button(t("delete", lang), key="btn_delete"):
            if element_id is not None:
                idx = next((i for i, e in enumerate(elements) if e["id"] == element_id), None)
                if idx == 0:
                    st.session_state.voies_glostrup[voie_supp] = elements[1:]
                    st.success(t("success_delete", lang))
                    st.rerun()
                else:
                    st.warning(t("not_leftmost_element", lang))
            else:
                st.warning(t("no_element_left_delete", lang))

    # FR : Ligne pour déplacer un wagon (extrémité uniquement)
    # EN : Row to move a wagon (end only)
    st.markdown("### " + t("move_wagon", lang))
    col9, col10, col11, col12 = st.columns([2, 2, 2, 1])
    with col9:
        voie_source = st.selectbox(
            t("select_source_track", lang),
            options=[7, 8, 9, 11],
            key="source_voie"
        )
    with col10:
        elements_src = st.session_state.voies_glostrup[voie_source]
        elements_extremite_src = []
        # Cherche le premier élément à gauche
        for i, e in enumerate(elements_src):
            if all(el["type"] == "locomotive" or el["type"] == "wagon" for el in elements_src[:i]):
                elements_extremite_src.append((e["id"], e["type"], "gauche"))
                break
        # Cherche le premier élément à droite
        for i in range(len(elements_src)-1, -1, -1):
            e = elements_src[i]
            if all(el["type"] == "locomotive" or el["type"] == "wagon" for el in elements_src[i+1:]):
                elements_extremite_src.append((e["id"], e["type"], "droite"))
                break
        if elements_extremite_src:
            element_id, element_type, extremite = st.selectbox(
                t("element_to_move_end", lang),
                options=elements_extremite_src,
                format_func=lambda x: f"{t(x[1], lang).capitalize()} {x[0]} (extrémité {x[2]})"
            )
        else:
            element_id, element_type, extremite = None, None, None
    with col11:
        voie_cible = st.selectbox(
            t("select_target_track", lang),
            options=[7, 8, 9, 11],
            key="cible_voie"
        )
    with col12:
        if st.button(t("move", lang), key="btn_move"):
            if element_id is not None:
                idx = next((i for i, e in enumerate(elements_src) if e["id"] == element_id), None)
                if idx == 0 or idx == len(elements_src) - 1:
                    element = elements_src.pop(idx)
                    st.session_state.voies_glostrup[voie_cible].append(element)
                    st.success(t("success_move", lang))
                    st.rerun()
                else:
                    st.error(t("only_move_end", lang))
            else:
                st.warning(t("no_element_end_move", lang))

    # FR : Ligne pour réinitialiser le jeu
    # EN : Row to reset the game
    st.markdown("### " + t("reset_game", lang))
    if st.button(t("reset_game", lang), key="btn_reset"):
        reset_state()
        st.rerun()