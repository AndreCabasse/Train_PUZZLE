# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 14:06:57 2025

@author: andre
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from folium.plugins import MarkerCluster
from datetime import datetime
from folium.features import CustomIcon

def get_depots_dataframe(simulation):
    """Retourne un DataFrame des dépôts avec coordonnées valides."""
    depots = []
    for nom, conf in simulation.depots.items():
        lat = conf.get("lat")
        lon = conf.get("lon")
        if lat is not None and lon is not None:
            depots.append({
                "Depot": nom,
                "lat": lat,
                "lon": lon,
            })
    return pd.DataFrame(depots)

# SVG moderne pour les trains (rouge, stylisé)
svg_train = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><circle cx="16" cy="16" r="14" fill="white" stroke="#d32f2f" stroke-width="3"/><rect x="10" y="10" width="12" height="8" rx="2" fill="#d32f2f"/><rect x="13" y="18" width="6" height="2" rx="1" fill="#d32f2f"/><circle cx="13" cy="22" r="2" fill="#d32f2f"/><circle cx="19" cy="22" r="2" fill="#d32f2f"/></svg>'

def get_train_icon():
    return CustomIcon(
        icon_image="Train.png",
        icon_size=(20, 20),
        icon_anchor=(19, 19),
        popup_anchor=(0, -15)
    )
def afficher_carte_depots(simulation, t, lang):
    df_depots = get_depots_dataframe(simulation)
    if df_depots.empty:
        st.info(t("no_depot_coords", lang) if "no_depot_coords" in t.__code__.co_varnames else "Aucun dépôt géolocalisé à afficher.")
        return

    lat_centre = df_depots["lat"].mean()
    lon_centre = df_depots["lon"].mean()
    m = folium.Map(location=[lat_centre, lon_centre], zoom_start=6)

    # Marqueurs de dépôts (fixes)
    for _, row in df_depots.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(f"<b>{row['Depot']}</b>", max_width=200),
            tooltip=row["Depot"],
            icon=folium.Icon(color="blue", icon="train", prefix="fa"),
        ).add_to(m)

    # Cluster pour les trains
    marker_cluster = MarkerCluster().add_to(m)
    decalage = 0.001  # Décalage en degrés pour ne pas superposer les trains sur le dépôt

    for depot_name in df_depots["Depot"]:
        trains = [train for train in simulation.trains if train.depot == depot_name]
        depot_info = df_depots[df_depots["Depot"] == depot_name].iloc[0]
        lat0, lon0 = depot_info["lat"], depot_info["lon"]
        for i, train in enumerate(trains):
            lat = lat0 + (i + 1) * decalage
            lon = lon0 + (i + 1) * decalage
            popup_html = f"""
            <div style='font-family:sans-serif;min-width:180px'>
                <div style='font-weight:bold;font-size:16px;color:#1976d2'>{t('train_name', lang)}: {train.nom}</div>
                <div style='margin-top:4px'>
                    <span style='background:#eee;border-radius:4px;padding:2px 6px;font-size:12px;color:#555'>{t('train_type', lang)}: {t(train.type, lang)}</span>
                </div>
                <div style='margin-top:8px'>
                    <span style='color:#333'>{t('arrival_time', lang)}:</span> <b>{train.arrivee.strftime('%Y-%m-%d %H:%M')}</b><br>
                    <span style='color:#333'>{t('departure_time', lang)}:</span> <b>{train.depart.strftime('%Y-%m-%d %H:%M')}</b>
                </div>
                <div style='margin-top:8px;color:#888;font-size:12px'>
                    {t('depot', lang)}: {train.depot}
                </div>
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=train.nom,
                icon=get_train_icon(),
            ).add_to(marker_cluster)

    with st.spinner(t("loading_map", lang) if "loading_map" in t.__code__.co_varnames else "Chargement de la carte..."):
        folium_output = st_folium(m, width=1200, height=700, key="carte_depots")
    depot_selectionne = None
    if folium_output and folium_output.get("last_object_clicked_popup"):
        depot_selectionne = folium_output["last_object_clicked_popup"]

    if depot_selectionne:
        trains = [train for train in simulation.trains if train.depot == depot_selectionne]
        if trains:
            st.markdown(f"### {t('train_list', lang)} – {depot_selectionne}")
            data = []
            for train in trains:
                data.append({
                    t("train_name", lang): train.nom,
                    t("arrival_time", lang): train.arrivee.strftime("%Y-%m-%d %H:%M"),
                    t("departure_time", lang): train.depart.strftime("%Y-%m-%d %H:%M"),
                    t("train_type", lang): t(train.type, lang),
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info(t("no_trains", lang))
    else:
        st.info(t("select_depot", lang))

def afficher_carte_etat_trains_heure(simulation, t, lang):
    # Récupère toutes les heures d'arrivée et de départ pour bornes du slider
    heures = []
    for train in simulation.trains:
        # Conversion explicite en datetime si besoin
        try:
            arr = pd.to_datetime(train.arrivee)
            dep = pd.to_datetime(train.depart)
        except Exception:
            continue
        if pd.notnull(arr) and pd.notnull(dep):
            heures.append(arr.to_pydatetime() if hasattr(arr, "to_pydatetime") else arr)
            heures.append(dep.to_pydatetime() if hasattr(dep, "to_pydatetime") else dep)
    # Filtre pour ne garder que des datetime
    heures = [h for h in heures if isinstance(h, datetime)]
    heures = sorted(list(set(heures)))
    if not heures:
        st.info(t("no_time_data", lang) if "no_time_data" in t.__code__.co_varnames else "Aucune donnée horaire disponible.")
        return

    heure_select = st.slider(
        t("select_time", lang),
        min_value=heures[0],
        max_value=heures[-1],
        value=heures[0],
        format="YYYY-MM-DD HH:mm",
        key="slider_etat_trains_heure"
    )

    df_depots = get_depots_dataframe(simulation)
    if df_depots.empty:
        st.info(t("no_depot_coords", lang) if "no_depot_coords" in t.__code__.co_varnames else "Aucun dépôt géolocalisé à afficher.")
        return

    lat_centre = df_depots["lat"].mean()
    lon_centre = df_depots["lon"].mean()
    m = folium.Map(location=[lat_centre, lon_centre], zoom_start=6)

    # Marqueurs de dépôts (fixes)
    for _, row in df_depots.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(f"<b>{row['Depot']}</b>", max_width=200),
            tooltip=row["Depot"],
            icon=folium.Icon(color="blue", icon="train", prefix="fa"),
        ).add_to(m)

    # Cluster pour les trains présents à l'heure choisie
    marker_cluster = MarkerCluster().add_to(m)
    decalage = 0.001
    for depot_name in df_depots["Depot"]:
        trains = [
            train for train in simulation.trains
            if train.depot == depot_name and train.arrivee <= heure_select <= train.depart
        ]
        depot_info = df_depots[df_depots["Depot"] == depot_name].iloc[0]
        lat0, lon0 = depot_info["lat"], depot_info["lon"]
        for i, train in enumerate(trains):
            lat = lat0 + (i + 1) * decalage
            lon = lon0 + (i + 1) * decalage
            popup_html = f"""
            <div style='font-family:sans-serif;min-width:180px'>
                <div style='font-weight:bold;font-size:16px;color:#1976d2'>{t('train_name', lang)}: {train.nom}</div>
                <div style='margin-top:4px'>
                    <span style='background:#eee;border-radius:4px;padding:2px 6px;font-size:12px;color:#555'>{t('train_type', lang)}: {t(train.type, lang)}</span>
                </div>
                <div style='margin-top:8px'>
                    <span style='color:#333'>{t('arrival_time', lang)}:</span> <b>{train.arrivee.strftime('%Y-%m-%d %H:%M')}</b><br>
                    <span style='color:#333'>{t('departure_time', lang)}:</span> <b>{train.depart.strftime('%Y-%m-%d %H:%M')}</b>
                </div>
                <div style='margin-top:8px;color:#888;font-size:12px'>
                    {t('depot', lang)}: {train.depot}
                </div>
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=train.nom,
                icon=get_train_icon(),
            ).add_to(marker_cluster)

    with st.spinner(t("loading_map", lang) if "loading_map" in t.__code__.co_varnames else "Chargement de la carte..."):
        st_folium(m, width=1200, height=700, key="carte_etat_trains_heure")