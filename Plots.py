# -*- coding: utf-8 -*-
"""
Created on Fri May  2 11:02:51 2025

@author: andre
"""

import plotly.graph_objects as go
from datetime import timedelta

def creer_graphique_occupation_depot(simulation, depot, base_time, t):
    fig = go.Figure()
    if depot == "Glostrup":
        occupation = simulation.occupation_a
        numeros_voies = simulation.numeros_voies_a
    else:
        occupation = simulation.occupation_b
        numeros_voies = simulation.numeros_voies_b

    # Couleurs pour les types de trains
    couleurs = {
        t("testing"): "red",
        t("storage"): "blue",
        t("pit"): "green"
    }
    
    # Hachures pour les trains électriques
    patterns = {
        t("testing"): "x",  # Hachures croisées pour les trains en test
        t("storage"): "/",  # Hachures diagonales pour les trains en stockage
        t("pit"): "\\"      # Hachures inversées pour les trains en fosse
    }

    for voie_idx, debut, fin, train in occupation:
        debut_heure = (debut - base_time).total_seconds() / 3600
        fin_heure = (fin - base_time).total_seconds() / 3600
        voie_num = numeros_voies[voie_idx]
        nom_train = f"{train.nom} ⚡" if train.electrique else f"{train.nom}"
        couleur = couleurs.get(train.type, "gray")  # Couleur par défaut si le type n'est pas défini
        pattern_shape = patterns.get(train.type, "") if train.electrique else None  # Appliquer un motif uniquement pour les trains électriques

        fig.add_trace(go.Bar(
            x=[fin_heure - debut_heure],
            y=[f"{t('Track')} {voie_num}"],
            base=debut_heure,
            orientation='h',
            marker=dict(
                color=couleur,
                pattern=dict(shape=pattern_shape)  # Ajouter le motif pour les trains électriques
            ),
            name=f"{nom_train} ({train.type})",
            hovertemplate=f"Train {nom_train}<br>Type: {train.type}<br>Début: {debut}<br>Fin: {fin}<extra></extra>"
        ))

    # Configuration de l'axe X
    if occupation:
        max_hours = max((fin - base_time).total_seconds() / 3600 for _, _, fin, _ in occupation)
    else:
        max_hours = 24

    tick_interval = 1 if max_hours <= 48 else 6 if max_hours <= 168 else 24
    tick_format = "%H:%M" if max_hours <= 48 else "%Y-%m-%d %H:%M" if max_hours <= 168 else "%Y-%m-%d"
    ticks = list(range(0, int(max_hours) + 1, tick_interval))
    ticklabels = [(base_time + timedelta(hours=tick)).strftime(tick_format) for tick in ticks]

    fig.update_layout(
        title=t(f"Depot {depot}"),
        xaxis=dict(
            title=t("Time"),
            tickvals=ticks,
            ticktext=ticklabels,
            tickangle=45,
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(title=t("Track")),
        barmode='stack',
        height=400,
        margin=dict(l=40, r=40, t=40, b=80)
    )
    return fig

import plotly.express as px
import pandas as pd

def creer_graphique_requirements_par_jour(requirements_par_jour, t):
    """
    Crée un graphique en barres groupées des besoins en ressources par jour.

    Args:
        requirements_par_jour: Dictionnaire des besoins par jour.
        t: Fonction de traduction.

    Returns:
        Graphique Plotly.
    """
    if not requirements_par_jour:
        return px.bar(title=t("no_requirements"))

    # Préparer les données pour le graphique
    data = []
    for jour, besoins in sorted(requirements_par_jour.items()):
        data.append({"Date": jour, "Ressource": t("test_drivers"), "Quantité": besoins["test_drivers"]})
        data.append({"Date": jour, "Ressource": t("locomotives"), "Quantité": besoins["locomotives"]})

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    df = df.dropna(subset=["Date"])

    if df.empty:
        return px.bar(title=t("no_requirements"))

    # Créer le graphique en barres groupées
    fig = px.bar(
        df,
        x="Date",
        y="Quantité",
        color="Ressource",
        title=t("requirements_by_day"),
        labels={"Quantité": t("quantity"), "Ressource": t("resource_type")},
        barmode="group",  # Mode groupé pour afficher les barres côte à côte
    )

    # Améliorer l'affichage
    fig.update_layout(
        xaxis_title=t("Date"),
        yaxis_title=t("quantity"),
        legend_title=t("resource_type"),
        xaxis=dict(
            tickformat="%d %b %Y",  # Format lisible pour les dates
            showgrid=True,
            tickangle=45,  # Incliner les étiquettes pour une meilleure lisibilité
        ),
        height=500,
        margin=dict(l=40, r=40, t=40, b=80),
    )

    return fig

def creer_graphique_trains_par_longueur_detaille(simulation, t, plage_debut, plage_fin):
    """
    Crée un graphique détaillé pour visualiser les trains avec des rectangles pour chaque wagon et locomotive,
    en fonction d'une plage temporelle.

    Args:
        simulation: Instance de la simulation contenant les trains et les occupations.
        t: Fonction de traduction.
        plage_debut: Début de la plage temporelle (datetime).
        plage_fin: Fin de la plage temporelle (datetime).

    Returns:
        Graphique Plotly.
    """
    fig = go.Figure()

    # Parcourir les occupations des dépôts A et B
    for depot, occupation, numeros_voies in [
        ("Glostrup", simulation.occupation_a, simulation.numeros_voies_a),
        ("Naestved", simulation.occupation_b, simulation.numeros_voies_b),
    ]:
        for voie_idx, debut, fin, train in occupation:
            # Filtrer les trains en fonction de la plage temporelle
            if fin < plage_debut or debut > plage_fin:
                continue

            voie_label = f"{t('Track')} {numeros_voies[voie_idx]} ({depot})"
            position_actuelle = 0  # Position de départ pour dessiner les rectangles

            # Ajouter la locomotive à gauche si spécifié
            if train.locomotives == 1 and train.locomotive_cote == "left":
                fig.add_trace(go.Bar(
                    x=[19],  # Longueur d'une locomotive
                    y=[voie_label],
                    base=position_actuelle,
                    orientation='h',
                    marker=dict(color="red", line=dict(color="black", width=1)),  # Bordure noire pour la locomotive
                    width=0.3,  # Réduire la hauteur des rectangles
                    name=f"{train.nom} - {t('locomotive')} 1",
                    hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                ))
                position_actuelle += 19  # Avancer la position

            # Ajouter les rectangles pour les wagons
            for i in range(train.wagons):
                fig.add_trace(go.Bar(
                    x=[14],  # Longueur d'un wagon
                    y=[voie_label],
                    base=position_actuelle,
                    orientation='h',
                    marker=dict(color="blue", line=dict(color="black", width=1)),  # Bordure noire pour les wagons
                    width=0.3,  # Réduire la hauteur des rectangles
                    name=f"{train.nom} - {t('wagon')} {i + 1}",
                    hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Wagon {i + 1}<br>Longueur: 14m<extra></extra>"
                ))
                position_actuelle += 14  # Avancer la position

            # Ajouter la locomotive à droite si spécifié
            if train.locomotives == 1 and train.locomotive_cote == "right":
                fig.add_trace(go.Bar(
                    x=[19],  # Longueur d'une locomotive
                    y=[voie_label],
                    base=position_actuelle,
                    orientation='h',
                    marker=dict(color="red", line=dict(color="black", width=1)),  # Bordure noire pour la locomotive
                    width=0.3,  # Réduire la hauteur des rectangles
                    name=f"{train.nom} - {t('locomotive')} 1",
                    hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                ))
                position_actuelle += 19  # Avancer la position

            # Ajouter deux locomotives si présentes
            if train.locomotives == 2:
                # Locomotive à gauche
                fig.add_trace(go.Bar(
                    x=[19],
                    y=[voie_label],
                    base=0,
                    orientation='h',
                    marker=dict(color="red", line=dict(color="black", width=1)),
                    width=0.3,  # Réduire la hauteur des rectangles
                    name=f"{train.nom} - {t('locomotive')} 1",
                    hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                ))
                position_actuelle += 19  # Avancer la position après la locomotive gauche

                # Ajouter les rectangles pour les wagons
                for i in range(train.wagons):
                    fig.add_trace(go.Bar(
                        x=[14],  # Longueur d'un wagon
                        y=[voie_label],
                        base=position_actuelle,
                        orientation='h',
                        marker=dict(color="blue", line=dict(color="black", width=1)),  # Bordure noire pour les wagons
                        width=0.3,  # Réduire la hauteur des rectangles
                        name=f"{train.nom} - {t('wagon')} {i + 1}",
                        hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Wagon {i + 1}<br>Longueur: 14m<extra></extra>"
                    ))
                    position_actuelle += 14  # Avancer la position

                # Locomotive à droite
                fig.add_trace(go.Bar(
                    x=[19],
                    y=[voie_label],
                    base=position_actuelle,
                    orientation='h',
                    marker=dict(color="red", line=dict(color="black", width=1)),
                    width=0.3,  # Réduire la hauteur des rectangles
                    name=f"{train.nom} - {t('locomotive')} 2",
                    hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                ))
                position_actuelle += 19  # Avancer la position après la locomotive droite

    # Configurer l'affichage du graphique
    fig.update_layout(
        title=t("train_length_by_track"),
        xaxis_title=t("length"),
        yaxis_title=t("Track"),
        legend_title=t("train_type"),
        height=600,
        margin=dict(l=40, r=40, t=40, b=80),
        barmode='stack',  # Empiler les rectangles pour chaque train
    )

    return fig