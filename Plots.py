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
    fig = go.Figure()
    if depot == "Glostrup":
        occupation = simulation.occupation_a
        numeros_voies = simulation.numeros_voies_a
    else:
        occupation = simulation.occupation_b
        numeros_voies = simulation.numeros_voies_b

    # Couleurs pour les types de trains
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
        debut_heure = (debut - base_time).total_seconds() / 3600
        fin_heure = (fin - base_time).total_seconds() / 3600
        voie_num = numeros_voies[voie_idx]
        nom_train = f"{train.nom} ⚡" if train.electrique else f"{train.nom}"
        couleur = couleurs.get(train.type, "gray")  # Couleur par défaut si le type n'est pas défini
        pattern_shape = patterns.get(train.type, "") if train.electrique else None  # Appliquer un motif uniquement pour les trains électriques

        fig.add_trace(go.Bar(
            x=[fin_heure - debut_heure],
            y=[f"{t('Track', lang)} {voie_num}"],
            base=debut_heure,
            orientation='h',
            marker=dict(
                color=couleur,
                pattern=dict(shape=pattern_shape)  # Ajouter le motif pour les trains électriques
            ),
            name=f"{nom_train} ({t(train.type, lang)})",
            hovertemplate=f"Train {nom_train}<br>Type: {t(train.type, lang)}<br>Début: {debut}<br>Fin: {fin}<extra></extra>"
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

import plotly.express as px
import pandas as pd

def creer_graphique_requirements_par_jour(requirements_par_jour, t, lang):
    """
    Crée un graphique en barres groupées des besoins en ressources par jour.

    Args:
        requirements_par_jour: Dictionnaire des besoins par jour.
        t: Fonction de traduction.

    Returns:
        Graphique Plotly.
    """
    if not requirements_par_jour:
        return px.bar(title=t("no_requirements", lang))

    # Préparer les données pour le graphique
    data = []
    for jour, besoins in sorted(requirements_par_jour.items()):
        data.append({"Date": jour, "Ressource": t("test_drivers", lang), "Quantité": besoins["test_drivers"]})
        data.append({"Date": jour, "Ressource": t("locomotives", lang), "Quantité": besoins["locomotives"]})

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    df = df.dropna(subset=["Date"])

    if df.empty:
        return px.bar(title=t("no_requirements", lang))

    # Créer le graphique en barres groupées
    fig = px.bar(
        df,
        x="Date",
        y="Quantité",
        color="Ressource",
        title=t("requirements_by_day", lang),
        labels={"Quantité": t("quantity", lang), "Ressource": t("resource_type", lang)},
        barmode="group",  # Mode groupé pour afficher les barres côte à côte
    )

    # Améliorer l'affichage
    fig.update_layout(
        xaxis_title=t("Date", lang),
        yaxis_title=t("quantity", lang),
        legend_title=t("resource_type", lang),
        xaxis=dict(
            tickformat="%d %b %Y",  # Format lisible pour les dates
            showgrid=True,
            tickangle=45,  # Incliner les étiquettes pour une meilleure lisibilité
        ),
        height=500,
        margin=dict(l=40, r=40, t=40, b=80),
    )

    return fig

def creer_graphique_trains_par_longueur_detaille(simulation, t, instant, lang):
    """
    Crée un graphique détaillé pour visualiser les trains avec des rectangles pour chaque wagon et locomotive,
    en fonction d'une plage temporelle.

    Args:
        simulation: Instance de la simulation contenant les trains et les occupations.
        t: Fonction de traduction.
        instant: Instant spécifique (datetime).

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
            # Filtrer les trains présents à l'instant donné
            if debut <= instant <= fin:
                voie_label = f"{t('Track', lang)} {numeros_voies[voie_idx]} ({depot})"
                position_actuelle = 0  # Position de départ pour dessiner les rectangles

                # Cas 1 locomotive : placer à gauche ou à droite selon train.locomotive_cote
                if train.locomotives == 1:
                    if getattr(train, "locomotive_cote", None) == "left":
                        # Locomotive à gauche
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
                        # Puis wagons
                        for i in range(train.wagons):
                            fig.add_trace(go.Bar(
                                x=[14],
                                y=[voie_label],
                                base=position_actuelle,
                                orientation='h',
                                marker=dict(color="blue", line=dict(color="black", width=1)),
                                width=0.3,
                                name=f"{train.nom} - {t('wagon')} {i + 1}",
                                hovertemplate=f"Train: {train.nom}<br>Type: {train.type}<br>Wagon {i + 1}<br>Longueur: 14m<extra></extra>"
                            ))
                            position_actuelle += 14
                    else:
                        # Wagons d'abord
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
                        # Locomotive à droite
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

                # Cas 2 locomotives : une à chaque extrémité
                elif train.locomotives == 2:
                    # Locomotive gauche
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
                    # Wagons
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
                    # Locomotive droite
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

                # Cas 0 locomotive
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

    # Configurer l'affichage du graphique
    fig.update_layout(
        title=t("train_length_by_track", lang),
        xaxis_title=t("length", lang),
        yaxis_title=t("Track", lang),
        legend_title=t("train_type", lang),
        height=600,
        margin=dict(l=40, r=40, t=40, b=80),
        barmode='stack',  # Empiler les rectangles pour chaque train
    )

    return fig

def creer_gantt_occupation_depot(simulation, depot, t, lang):
    if depot == "Glostrup":
        occupation = simulation.occupation_a
        numeros_voies = simulation.numeros_voies_a
    else:
        occupation = simulation.occupation_b
        numeros_voies = simulation.numeros_voies_b

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

    # Correction ici : toujours créer un DataFrame avec les bonnes colonnes
    columns = ["Voie", "Début", "Fin", "Train", "Type", "Électrique"]
    df = pd.DataFrame(data, columns=columns)

    if df.empty:
        # Crée un graphique vide mais valide
        fig = px.timeline(df, x_start="Début", x_end="Fin", y="Voie", title=t(f"Planning {depot}", lang))
        fig.update_layout(
            height=200,
            xaxis_title=t("Time", lang),
            yaxis_title=t("Track", lang),
        )
        return fig

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