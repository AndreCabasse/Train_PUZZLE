# -*- coding: utf-8 -*-
"""
Created on Fri May  2 11:02:51 2025

@author: andre
"""

import plotly.graph_objects as go
from datetime import timedelta
import plotly.express as px
import pandas as pd

def creer_graphique_trains_par_longueur_detaille(simulation, t, instant, lang, depot=None):
    """
    FR : Crée un graphique détaillé représentant chaque wagon et locomotive d'un train à un instant donné.
    EN : Create a detailed chart showing each wagon and locomotive of a train at a given instant.

    Args:
        simulation: FR : Instance Simulation. / EN : Simulation instance.
        t: FR : Fonction de traduction. / EN : Translation function.
        instant: FR : Instant à visualiser (datetime). / EN : Instant to visualize (datetime).
        lang: FR : Langue. / EN : Language.
        depot: FR : Nom du dépôt à filtrer (optionnel). / EN : Depot name to filter (optional).

    Returns:
        FR : Figure Plotly. / EN : Plotly Figure.
    """
    fig = go.Figure()

    # FR : Parcourt les occupations des dépôts
    # EN : Loop through occupations of depots
    depots_to_show = []
    if depot is not None:
        if depot in simulation.depots:
            depots_to_show = [(depot, simulation.depots[depot]["occupation"], simulation.depots[depot]["numeros_voies"])]
    else:
        depots_to_show = [
            (d, simulation.depots[d]["occupation"], simulation.depots[d]["numeros_voies"])
            for d in simulation.depots
        ]

    for depot_name, occupation, numeros_voies in depots_to_show:
        for voie_idx, debut, fin, train in occupation:
            if debut <= instant <= fin:
                voie_label = f"{t('Track', lang)} {numeros_voies[voie_idx]} ({depot_name})"
                position_actuelle = 0
                # ...existing code for drawing bars...
                # (copie le code déjà présent ici pour les wagons/locomotives)
                if train.locomotives == 1:
                    if getattr(train, "locomotive_cote", None) == "left":
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
                    else:
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

    fig.update_layout(
        plot_bgcolor="#fff8f8",
        paper_bgcolor="#fbe9e7",
        font=dict(family="Segoe UI, Arial", size=14, color="#b71c1c"),
        title=t("train_length_by_track", lang),
        xaxis_title=t("length", lang),
        yaxis_title=t("Track", lang),
        legend_title=t("train_type", lang),
        height=600,
        margin=dict(l=40, r=40, t=40, b=80),
        barmode='stack',
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
        plot_bgcolor="#fff8f8",
        paper_bgcolor="#fbe9e7",
        font=dict(family="Segoe UI, Arial", size=14, color="#b71c1c"),
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
    occupation = simulation.depots[depot]["occupation"]
    numeros_voies = simulation.depots[depot]["numeros_voies"]

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
            plot_bgcolor="#fff8f8",
            paper_bgcolor="#fbe9e7",
            font=dict(family="Segoe UI, Arial", size=14, color="#b71c1c"),
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
        plot_bgcolor="#fff8f8",
        paper_bgcolor="#fbe9e7",
        font=dict(family="Segoe UI, Arial", size=14, color="#b71c1c"),
        margin=dict(l=40, r=40, t=40, b=80),
        xaxis_title=t("Time", lang),
        yaxis_title=t("Track", lang),
    )
    return fig

def creer_graphique_occupation_depot(simulation, depot, base_time, t, lang):
    """
    FR : Crée un graphique d'occupation des voies pour un dépôt donné.
    EN : Create a track occupation chart for a given depot.

    Args:
        simulation: Instance Simulation.
        depot: Nom du dépôt (str).
        base_time: Heure de base (datetime).
        t: Fonction de traduction.
        lang: Langue.

    Returns:
        Figure Plotly.
    """
    import plotly.graph_objects as go
    depot_data = simulation.depots[depot]
    occupation = depot_data["occupation"]
    numeros_voies = depot_data["numeros_voies"]

    fig = go.Figure()
    colors = ["#1976d2", "#e74c3c", "#27ae60", "#f39c12", "#8e44ad", "#34495e", "#9b59b6"]

    for idx, voie in enumerate(numeros_voies):
        occs = [occ for occ in occupation if occ[0] == idx]
        for occ in occs:
            _, debut, fin, train = occ
            color = colors[idx % len(colors)]
            fig.add_trace(go.Bar(
                x=[(fin - debut).total_seconds() / 3600],
                y=[f"{t('Track', lang)} {voie}"],
                base=(debut - base_time).total_seconds() / 3600,
                orientation='h',
                marker=dict(color=color, line=dict(color="black", width=1)),
                name=train.nom,
                hovertemplate=f"Train: {train.nom}<br>Type: {t(train.type, lang)}<br>Début: {debut.strftime('%Y-%m-%d %H:%M')}<br>Fin: {fin.strftime('%Y-%m-%d %H:%M')}<extra></extra>"
            ))

    fig.update_layout(
        title=f"{t('graph_title', lang)} - {depot}",
        xaxis_title=t("Time", lang) + " (h)",
        yaxis_title=t("Track", lang),
        barmode='stack',
        plot_bgcolor="#fff8f8",
        paper_bgcolor="#fbe9e7",
        font=dict(family="Segoe UI, Arial", size=14, color="#b71c1c"),
        height=400,
        margin=dict(l=40, r=40, t=40, b=80),
        legend_title=t("train_name", lang),
    )
    return fig