# -*- coding: utf-8 -*-
"""
Created on Fri May  2 11:02:51 2025

@author: andre
"""

import plotly.graph_objects as go
from datetime import timedelta
import plotly.express as px
import pandas as pd

def creer_graphique_occupation_depot(simulation, depot, base_time, t, lang):
    """
    FR : Crée un graphique d'occupation des voies pour un dépôt donné.
    EN : Create a track occupation chart for a given depot.

    Args:
        simulation: FR : Instance de Simulation. / EN : Simulation instance.
        depot: FR : Nom du dépôt ("Glostrup" ou "Naestved"). / EN : Depot name.
        base_time: FR : Heure de référence pour l'axe X. / EN : Reference time for X axis.
        t: FR : Fonction de traduction. / EN : Translation function.
        lang: FR : Langue. / EN : Language.

    Returns:
        FR : Figure Plotly. / EN : Plotly Figure.
    """
    fig = go.Figure()
    # FR : Sélectionne les occupations et numéros de voies selon le dépôt
    # EN : Select occupation and track numbers according to depot
    if depot == "Glostrup":
        occupation = simulation.occupation_a
        numeros_voies = simulation.numeros_voies_a
    else:
        occupation = simulation.occupation_b
        numeros_voies = simulation.numeros_voies_b

    # FR : Couleurs et motifs selon le type de train
    # EN : Colors and patterns by train type
    couleurs = {
        "testing": "red",
        "storage": "blue",
        "pit": "green"
    }
    patterns = {
        "testing": "x",
        "storage": "/",
        "pit": "\\"
    }
    for voie_idx, debut, fin, train in occupation:
        # FR : Calcule la position en heures sur l'axe X
        # EN : Compute position in hours on X axis
        debut_heure = (debut - base_time).total_seconds() / 3600
        fin_heure = (fin - base_time).total_seconds() / 3600
        voie_num = numeros_voies[voie_idx]
        nom_train = f"{train.nom} ⚡" if train.electrique else f"{train.nom}"
        couleur = couleurs.get(train.type, "gray")  # FR : Couleur par défaut si type inconnu / EN : Default color if type unknown
        pattern_shape = patterns.get(train.type, "") if train.electrique else None  # FR : Motif si train électrique / EN : Pattern if electric train

        # FR : Ajoute une barre horizontale pour chaque occupation de voie
        # EN : Add a horizontal bar for each track occupation
        fig.add_trace(go.Bar(
            x=[fin_heure - debut_heure],
            y=[f"{t('Track', lang)} {voie_num}"],
            base=debut_heure,
            orientation='h',
            marker=dict(
                color=couleur,
                pattern=dict(shape=pattern_shape)  # FR : Motif pour les trains électriques / EN : Pattern for electric trains
            ),
            name=f"{nom_train} ({t(train.type, lang)})",
            hovertemplate=f"Train {nom_train}<br>Type: {t(train.type, lang)}<br>Début: {debut}<br>Fin: {fin}<extra></extra>"
        ))

    # FR : Configuration de l'axe X (heures, labels, etc.)
    # EN : X axis configuration (hours, labels, etc.)
    if occupation:
        max_hours = max((fin - base_time).total_seconds() / 3600 for _, _, fin, _ in occupation)
    else:
        max_hours = 24

    tick_interval = 1 if max_hours <= 48 else 6 if max_hours <= 168 else 24
    tick_format = "%H:%M" if max_hours <= 48 else "%Y-%m-%d %H:%M" if max_hours <= 168 else "%Y-%m-%d"
    ticks = list(range(0, int(max_hours) + 1, tick_interval))
    ticklabels = [(base_time + timedelta(hours=tick)).strftime(tick_format) for tick in ticks]

    fig.update_layout(
        title=t(f"Depot {depot}", lang),
        xaxis=dict(
            title=t("Time", lang),
            tickvals=ticks,
            ticktext=ticklabels,
            tickangle=45,
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(title=t("Track", lang)),
        barmode='stack',
        height=400,
        margin=dict(l=40, r=40, t=40, b=80)
    )
    return fig

def creer_graphique_requirements_par_jour(requirements_par_jour, t, lang):
    """
    FR : Crée un graphique en barres groupées des besoins en ressources par jour.
    EN : Create a grouped bar chart of resource requirements per day.

    Args:
        requirements_par_jour: FR : Dictionnaire des besoins par jour. / EN : Requirements per day dict.
        t: FR : Fonction de traduction. / EN : Translation function.
        lang: FR : Langue. / EN : Language.

    Returns:
        FR : Figure Plotly. / EN : Plotly Figure.
    """
    if not requirements_par_jour:
        return px.bar(title=t("no_requirements", lang))

    # FR : Prépare les données pour le graphique
    # EN : Prepare data for the chart
    data = []
    for jour, besoins in sorted(requirements_par_jour.items()):
        data.append({"Date": jour, "Ressource": t("test_drivers", lang), "Quantité": besoins["test_drivers"]})
        data.append({"Date": jour, "Ressource": t("locomotives", lang), "Quantité": besoins["locomotives"]})

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    df = df.dropna(subset=["Date"])

    if df.empty:
        return px.bar(title=t("no_requirements", lang))

    # FR : Crée le graphique en barres groupées
    # EN : Create grouped bar chart
    fig = px.bar(
        df,
        x="Date",
        y="Quantité",
        color="Ressource",
        title=t("requirements_by_day", lang),
        labels={"Quantité": t("quantity", lang), "Ressource": t("resource_type", lang)},
        barmode="group",
    )

    # FR : Améliore l'affichage (axes, légende, etc.)
    # EN : Improve display (axes, legend, etc.)
    fig.update_layout(
        xaxis_title=t("Date", lang),
        yaxis_title=t("quantity", lang),
        legend_title=t("resource_type", lang),
        xaxis=dict(
            tickformat="%d %b %Y",
            showgrid=True,
            tickangle=45,
        ),
        height=500,
        margin=dict(l=40, r=40, t=40, b=80),
    )

    return fig

def creer_graphique_trains_par_longueur_detaille(simulation, t, instant, lang):
    """
    FR : Crée un graphique détaillé représentant chaque wagon et locomotive d'un train à un instant donné.
    EN : Create a detailed chart showing each wagon and locomotive of a train at a given instant.

    Args:
        simulation: FR : Instance Simulation. / EN : Simulation instance.
        t: FR : Fonction de traduction. / EN : Translation function.
        instant: FR : Instant à visualiser (datetime). / EN : Instant to visualize (datetime).
        lang: FR : Langue. / EN : Language.

    Returns:
        FR : Figure Plotly. / EN : Plotly Figure.
    """
    fig = go.Figure()

    # FR : Parcourt les occupations des deux dépôts
    # EN : Loop through occupations of both depots
    for depot, occupation, numeros_voies in [
        ("Glostrup", simulation.occupation_a, simulation.numeros_voies_a),
        ("Naestved", simulation.occupation_b, simulation.numeros_voies_b),
    ]:
        for voie_idx, debut, fin, train in occupation:
            # FR : Filtre les trains présents à l'instant donné
            # EN : Filter trains present at the given instant
            if debut <= instant <= fin:
                voie_label = f"{t('Track', lang)} {numeros_voies[voie_idx]} ({depot})"
                position_actuelle = 0  # FR : Position de départ pour dessiner / EN : Start position for drawing

                # FR : Cas 1 locomotive, à gauche ou à droite
                # EN : Case 1 locomotive, left or right
                if train.locomotives == 1:
                    if getattr(train, "locomotive_cote", None) == "left":
                        # FR : Locomotive à gauche / EN : Locomotive on the left
                        fig.add_trace(go.Bar(
                            x=[19],
                            y=[voie_label],
                            base=position_actuelle,
                            orientation='h',
                            marker=dict(color="red", line=dict(color="black", width=1)),
                            width=0.3,
                            name=f"{train.nom} - {t('locomotive', lang)} 1",
                            hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                        ))
                        position_actuelle += 19
                        # FR : Puis wagons / EN : Then wagons
                        for i in range(train.wagons):
                            fig.add_trace(go.Bar(
                                x=[14],
                                y=[voie_label],
                                base=position_actuelle,
                                orientation='h',
                                marker=dict(color="blue", line=dict(color="black", width=1)),
                                width=0.3,
                                name=f"{train.nom} - {t('wagon', lang)} {i + 1}",
                                hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Wagon {i + 1}<br>Longueur: 14m<extra></extra>"
                            ))
                            position_actuelle += 14
                    else:
                        # FR : Wagons d'abord, puis locomotive à droite / EN : Wagons first, then locomotive on the right
                        for i in range(train.wagons):
                            fig.add_trace(go.Bar(
                                x=[14],
                                y=[voie_label],
                                base=position_actuelle,
                                orientation='h',
                                marker=dict(color="blue", line=dict(color="black", width=1)),
                                width=0.3,
                                name=f"{train.nom} - {t('wagon', lang)} {i + 1}",
                                hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Wagon {i + 1}<br>Longueur: 14m<extra></extra>"
                            ))
                            position_actuelle += 14
                        fig.add_trace(go.Bar(
                            x=[19],
                            y=[voie_label],
                            base=position_actuelle,
                            orientation='h',
                            marker=dict(color="red", line=dict(color="black", width=1)),
                            width=0.3,
                            name=f"{train.nom} - {t('locomotive', lang)} 1",
                            hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                        ))
                        position_actuelle += 19

                # FR : Cas 2 locomotives, une à chaque extrémité
                # EN : Case 2 locomotives, one at each end
                elif train.locomotives == 2:
                    fig.add_trace(go.Bar(
                        x=[19],
                        y=[voie_label],
                        base=position_actuelle,
                        orientation='h',
                        marker=dict(color="red", line=dict(color="black", width=1)),
                        width=0.3,
                        name=f"{train.nom} - {t('locomotive', lang)} 1",
                        hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                    ))
                    position_actuelle += 19
                    for i in range(train.wagons):
                        fig.add_trace(go.Bar(
                            x=[14],
                            y=[voie_label],
                            base=position_actuelle,
                            orientation='h',
                            marker=dict(color="blue", line=dict(color="black", width=1)),
                            width=0.3,
                            name=f"{train.nom} - {t('wagon', lang)} {i + 1}",
                            hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Wagon {i + 1}<br>Longueur: 14m<extra></extra>"
                        ))
                        position_actuelle += 14
                    fig.add_trace(go.Bar(
                        x=[19],
                        y=[voie_label],
                        base=position_actuelle,
                        orientation='h',
                        marker=dict(color="red", line=dict(color="black", width=1)),
                        width=0.3,
                        name=f"{train.nom} - {t('locomotive', lang)} 2",
                        hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Locomotive<br>Longueur: 19m<extra></extra>"
                    ))
                    position_actuelle += 19

                # FR : Cas 0 locomotive, uniquement des wagons
                # EN : Case 0 locomotive, only wagons
                elif train.locomotives == 0:
                    for i in range(train.wagons):
                        fig.add_trace(go.Bar(
                            x=[14],
                            y=[voie_label],
                            base=position_actuelle,
                            orientation='h',
                            marker=dict(color="blue", line=dict(color="black", width=1)),
                            width=0.3,
                            name=f"{train.nom} - {t('wagon', lang)} {i + 1}",
                            hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Wagon {i + 1}<br>Longueur: 14m<extra></extra>"
                        ))
                        position_actuelle += 14

    # FR : Configuration du graphique (axes, légende, etc.)
    # EN : Chart configuration (axes, legend, etc.)
    fig.update_layout(
        title=t("train_length_by_track", lang),
        xaxis_title=t("length", lang),
        yaxis_title=t("Track", lang),
        legend_title=t("train_type", lang),
        height=600,
        margin=dict(l=40, r=40, t=40, b=80),
        barmode='stack',
    )

    return fig

def creer_gantt_occupation_depot(simulation, depot, t, lang):
    """
    FR : Crée un diagramme de Gantt de l'occupation des voies pour un dépôt.
    EN : Create a Gantt chart of track occupation for a depot.

    Args:
        simulation: FR : Instance Simulation. / EN : Simulation instance.
        depot: FR : Nom du dépôt. / EN : Depot name.
        t: FR : Fonction de traduction. / EN : Translation function.
        lang: FR : Langue. / EN : Language.

    Returns:
        FR : Figure Plotly. / EN : Plotly Figure.
    """
    if depot == "Glostrup":
        occupation = simulation.occupation_a
        numeros_voies = simulation.numeros_voies_a
    else:
        occupation = simulation.occupation_b
        numeros_voies = simulation.numeros_voies_b

    # FR : Prépare les données pour le Gantt
    # EN : Prepare data for Gantt chart
    data = []
    for voie_idx, debut, fin, train in occupation:
        data.append({
            "Voie": f"{numeros_voies[voie_idx]}",
            "Début": debut,
            "Fin": fin,
            "Train": train.nom,
            "Type": t(train.type, lang) if hasattr(train, "type") else "",
            "Électrique": "⚡" if getattr(train, "electrique", False) else "",
        })

    # FR : Toujours créer un DataFrame avec les bonnes colonnes
    # EN : Always create a DataFrame with the right columns
    columns = ["Voie", "Début", "Fin", "Train", "Type", "Électrique"]
    df = pd.DataFrame(data, columns=columns)

    if df.empty:
        # FR : Crée un graphique vide mais valide
        # EN : Create an empty but valid chart
        fig = px.timeline(df, x_start="Début", x_end="Fin", y="Voie", title=t(f"Planning {depot}", lang))
        fig.update_layout(
            height=200,
            xaxis_title=t("Time", lang),
            yaxis_title=t("Track", lang),
        )
        return fig

    # FR : Crée le diagramme de Gantt avec Plotly Express
    # EN : Create the Gantt chart with Plotly Express
    fig = px.timeline(
        df,
        x_start="Début",
        x_end="Fin",
        y="Voie",
        color="Type",
        text="Train",
        title=t(f"Planning {depot}", lang),
        hover_data=["Train", "Début", "Fin", "Électrique"]
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=400,
        margin=dict(l=40, r=40, t=40, b=80),
        xaxis_title=t("Time", lang),
        yaxis_title=t("Track", lang),
    )
    return fig