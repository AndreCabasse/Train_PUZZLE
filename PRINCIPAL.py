# -*- coding: utf-8 -*-
"""
PRINCIPAL.py
============

FR : Application principale Streamlit pour la simulation d'occupation des voies de dépôt ferroviaire.
EN : Main Streamlit application for railway depot track occupation simulation.

FR :
- Permet d'ajouter, modifier, supprimer des trains.
- Visualise l'occupation des voies, les statistiques et les besoins en ressources.
- Gère la langue de l'interface (français, anglais, danois).
- Propose un mini-jeu de gestion de wagons.

EN :
- Allows adding, modifying, and deleting trains.
- Visualizes track occupation, statistics, and resource requirements.
- Manages interface language (French, English, Danish).
- Offers a wagon management mini-game.

FR : Modules utilisés :
EN : Modules used:
- Simulation : logique métier et gestion des trains/voies. / business logic and train/track management
- Traduction : gestion multilingue. / multilingual support
- Interface : composants d'interface utilisateur. / user interface components
- Stats : calculs statistiques et requirements. / statistics and requirements calculations
- Plots : graphiques Plotly pour la visualisation. / Plotly charts for visualization

Auteur : andre
Date de création : 02/05/2025
"""

import streamlit as st
from datetime import datetime, timedelta
from Simulation import Simulation
from Traduction import t, get_translation
from Interface import (
    afficher_formulaire_ajout, 
    afficher_tableau_trains, 
    afficher_modification_train, 
    afficher_suppression_train
)
from Stats import (
    calculer_temps_moyen_attente, 
    calculer_taux_occupation, 
    calculer_statistiques_globales, 
    calculer_requirements, 
    regrouper_requirements_par_jour
)
from Plots import (
    creer_graphique_occupation_depot,
    creer_graphique_requirements_par_jour,
    creer_graphique_trains_par_longueur_detaille,
    creer_gantt_occupation_depot
)
import pandas as pd
import io
import re
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

def plotly_double_fig_to_pdf(fig1, legend_html1, fig2, legend_html2):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def add_fig(fig, legend_html, y_offset):
        # Convertit la figure Plotly en image PNG
        img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
        img = Image.open(io.BytesIO(img_bytes))
        aspect = img.width / img.height
        img_width = width - 40
        img_height = img_width / aspect
        if img_height > (height - 120) / 2:
            img_height = (height - 120) / 2
            img_width = img_height * aspect
        img = img.resize((int(img_width), int(img_height)))
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)
        c.drawImage(ImageReader(img_io), 20, y_offset - img_height, width=img_width, height=img_height)  # <-- Correction ici
        # Ajoute la légende si fournie
        if legend_html:
            from reportlab.lib.utils import simpleSplit
            legend_text = re.sub('<[^<]+?>', '', legend_html)  # retire les balises HTML
            legend_lines = simpleSplit(legend_text, "Helvetica", 12, width-40)
            y = y_offset - img_height - 20
            for line in legend_lines:
                c.drawString(30, y, line)
                y -= 15
        return y_offset - img_height - 40

    y_offset = height - 40
    y_offset = add_fig(fig1, legend_html1, y_offset)
    y_offset = add_fig(fig2, legend_html2, y_offset)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
# ---------------------------------------------------------------------------
# FR : CONFIGURATION DE LA PAGE ET INITIALISATION DE LA SIMULATION
# EN : PAGE CONFIGURATION AND SIMULATION INITIALIZATION
# ---------------------------------------------------------------------------

# FR : Configuration de la page Streamlit (largeur étendue)
# EN : Set Streamlit page layout to wide
st.set_page_config(
    page_title="Simulation d'occupation des voies",
    layout="wide",
    page_icon="🚄"
)

# --- CSS personnalisé pour un look moderne ---
st.markdown("""
    <style>
    /* Bandeau logo : padding haut/bas augmenté, logo centré verticalement */
    .logo-bandeau {
        width:100%;
        background:linear-gradient(90deg,#1976d2 0%,#4fc3f7 100%);
        padding:48px 0 32px 0; /* padding-top et padding-bottom augmentés */
        margin-bottom:18px;
        display:flex;
        justify-content:center;
        align-items:center;
        box-shadow:0 2px 8px #0002;
        min-height:120px;
    }
    .logo-bandeau img {
        max-height:80px;
        height:auto;
        object-fit:contain;
        margin-top:0;
        margin-bottom:0;
    }

    /* Contraste pour TOUS les champs de formulaire, même dans les colonnes */
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTimeInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox input {
        background: #f7fafc !important;
        border: 2px solid #b0bec5 !important;
        border-radius: 8px !important;
        color: #222 !important;
        box-shadow: 0 1px 2px #0001;
    }
    /* Contraste pour les labels */
    label, .stTextInput label, .stNumberInput label, .stDateInput label, .stTimeInput label {
        color: #1976d2 !important;
        font-weight: 500;
    }
    /* Contraste pour les DataFrames et tables */
    .stDataFrame, .stTable {
        background: #f7fafc !important;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 2px 8px #0001;
        border: 1.5px solid #b0bec5;
    }
    .stButton>button {
        background-color: #1976d2;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5em 1.5em;
        border: none;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background-color: #125ea2;
    }
    .stMetric {
        background: #e0eafc;
        border-radius: 8px;
        padding: 8px 0;
        margin-bottom: 8px;
    }
    .stSidebar .stSlider, .stSidebar .stSelectbox, .stSidebar .stButton {
        background: #f0f0f5;
        border-radius: 8px;
    }
    .stDivider { margin: 1.5em 0; }
    h2, .stSubheader { color: #1976d2 !important; }
    .block-container { padding-top: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# --- Bandeau logo modernisé avec nouvelle classe ---
import base64
logo_path = "DSB1.png"
def get_base64_logo(logo_path):
    with open(logo_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
logo_base64 = get_base64_logo(logo_path)
st.markdown(
    f"""
    <div class="logo-bandeau">
        <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="height:80px;">
    </div>
    """,
    unsafe_allow_html=True,
)

# FR : Initialisation de la simulation et de l'heure de base dans la session Streamlit
# EN : Initialize simulation and base time in Streamlit session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()
    st.session_state.base_time = datetime.combine(datetime.now().date(), datetime.min.time())

# ---------------------------------------------------------------------------
# FR : GESTION DE LA LANGUE
# EN : LANGUAGE SELECTION
# ---------------------------------------------------------------------------

# FR : Sélecteur de langue dans la barre latérale
# EN : Sidebar language selector
lang = st.sidebar.selectbox("Langue", ["fr", "en", "da"])
t_dict = get_translation(lang)

# ---------------------------------------------------------------------------
# FR : TITRE PRINCIPAL ET PARAMÈTRES DE SÉCURITÉ
# EN : MAIN TITLE AND SAFETY PARAMETERS
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <h1 style="text-align:center; margin-top:0; margin-bottom:0.5em; color:#2C3E50;">
        {t('title', lang)}
    </h1>
    """,
    unsafe_allow_html=True,
)
st.divider()
# FR : Délai de sécurité entre deux trains sur une même voie (slider dans la sidebar)
# EN : Safety delay between two trains on the same track (slider in sidebar)
st.sidebar.subheader(t("security_settings", lang))
delai_securite = st.sidebar.slider(
    t("security_delay", lang), min_value=0, max_value=30, value=10, step=1
)
st.session_state.simulation.delai_securite = delai_securite

# FR : Bouton pour réinitialiser la simulation
# EN : Button to reset the simulation
if st.sidebar.button(t("reset", lang)):
    st.session_state.simulation.reset()
    st.success(t("simulation_reset", lang))
    st.rerun()

# ---------------------------------------------------------------------------
# FR : CALCUL DES STATISTIQUES GLOBALES
# EN : GLOBAL STATISTICS CALCULATION
# ---------------------------------------------------------------------------

stats = calculer_statistiques_globales(st.session_state.simulation)

# ---------------------------------------------------------------------------
# FR : ORGANISATION EN ONGLETS PRINCIPAUX
# EN : MAIN TABS ORGANIZATION
# ---------------------------------------------------------------------------
# FR : tab1 : Ajout/Modification/Suppression de trains
#      tab2 : Liste des trains par dépôt
#      tab3 : Visualisations graphiques (occupation, export, Gantt, etc.)
#      tab4 : Statistiques globales
#      tab5 : Besoins en ressources (requirements)
#      tab6 : Mini-jeu de gestion des voies
# EN : tab1: Add/Modify/Delete trains
#      tab2: List of trains by depot
#      tab3: Visualizations (occupation, export, Gantt, etc.)
#      tab4: Global statistics
#      tab5: Resource requirements
#      tab6: Wagon management mini-game

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "➕ " + t("add_train", lang),
    "📋 " + t("train_list", lang),
    "📊 " + t("graph_title", lang),
    "📈 " + t("Statistiques", lang),
    "🛠️ " + t("requirements", lang),
    "🎮 " + t("Gestion des voies", lang)
])

# ---------------------------------------------------------------------------
# FR : ONGLET 1 : AJOUT / MODIFICATION / SUPPRESSION DE TRAINS
# EN : TAB 1: ADD / MODIFY / DELETE TRAINS
# ---------------------------------------------------------------------------

with tab1:
    sous_tab_ajout, sous_tab_modif, sous_tab_suppr = st.tabs([
        t("add_train", lang),
        t("modify_train", lang),
        t("delete_train", lang)
    ])
    with sous_tab_ajout:
        # FR : Formulaire d'ajout d'un train
        # EN : Form to add a new train
        afficher_formulaire_ajout(st.session_state.simulation, lang, t)
    with sous_tab_modif:
        # FR : Formulaire de modification d'un train existant
        # EN : Form to modify an existing train
        afficher_modification_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)
    with sous_tab_suppr:
        # FR : Formulaire de suppression d'un train
        # EN : Form to delete a train
        afficher_suppression_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)

# ---------------------------------------------------------------------------
# FR : ONGLET 2 : LISTE DES TRAINS PAR DÉPÔT
# EN : TAB 2: LIST OF TRAINS BY DEPOT
# ---------------------------------------------------------------------------

with tab2:
    # FR : Tableau pour le dépôt A (Glostrup)
    # EN : Table for depot A (Glostrup)
    st.subheader(t("Depot de Glostrup", lang))
    afficher_tableau_trains(
        [train for train in st.session_state.simulation.trains if train.depot == "Glostrup"],
        st.session_state.simulation, t, lang
    )

    # FR : Tableau pour le dépôt B (Naestved)
    # EN : Table for depot B (Naestved)
    st.subheader(t("Depot de Naestved", lang))
    afficher_tableau_trains(
        [train for train in st.session_state.simulation.trains if train.depot == "Naestved"],
        st.session_state.simulation, t, lang
    )
    
# ---------------------------------------------------------------------------
# FR : ONGLET 3 : VISUALISATIONS GRAPHIQUES
# EN : TAB 3: VISUALIZATIONS (OCCUPATION, EXPORT, GANTT, ETC.)
# ---------------------------------------------------------------------------
with tab3:
    sous_tab_occ, sous_tab_export, sous_tab_instant, sous_tab_gantt_a, sous_tab_gantt_b = st.tabs([
        t("graph_title", lang),
        "Export",
        t("train_length_by_track", lang),
        f"Gantt {t('Depot de Glostrup', lang)}",
        f"Gantt {t('Depot de Naestved', lang)}"
    ])
    
    # FR : Visualisation occupation des voies pour chaque dépôt
    # EN : Occupation visualization for each depot
    with sous_tab_occ:
        st.subheader(t("Depot de Glostrup", lang))
        fig_a = creer_graphique_occupation_depot(
            st.session_state.simulation, "Glostrup", st.session_state.base_time, t, lang
        )
        st.plotly_chart(fig_a, use_container_width=True)

        st.subheader(t("Depot Naestved", lang))
        fig_b = creer_graphique_occupation_depot(
            st.session_state.simulation, "Naestved", st.session_state.base_time, t, lang
        )
        st.plotly_chart(fig_b, use_container_width=True)
        
    # FR : Export des occupations (CSV, Excel, JSON)
    # EN : Export occupation data (CSV, Excel, JSON)
    with sous_tab_export:
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
        csv = df_occ.to_csv(index=False, sep=";").encode('utf-8')
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
    
    # FR : Visualisation instantanée de la composition des trains
    # EN : Instant visualization of train composition
    with sous_tab_instant:
        col1, col2 = st.columns(2)
        with col1:
            date_instant = st.date_input(t("base_date", lang), st.session_state.base_time.date(), key="date_instant")
        with col2:
            heure_instant = st.time_input(t("base_time", lang), st.session_state.base_time.time(), key="heure_instant")
        instant = datetime.combine(date_instant, heure_instant)
        fig_trains_instant = creer_graphique_trains_par_longueur_detaille(
            st.session_state.simulation, t, instant, lang
        )
        st.plotly_chart(fig_trains_instant, use_container_width=True)

    # FR : Gantt Glostrup
    # EN : Gantt chart for Glostrup
    with sous_tab_gantt_a:
        st.markdown(f"### {t('Planning', lang)} - {t('Depot de Glostrup', lang)}")
        fig_gantt_a = creer_gantt_occupation_depot(
            st.session_state.simulation, "Glostrup", t, lang
        )
        st.plotly_chart(fig_gantt_a, use_container_width=True)
        # Export Gantt Glostrup
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
        csv_gantt_a = df_gantt_a.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button(
            label="📥 Télécharger le planning Gantt Glostrup (CSV)",
            data=csv_gantt_a,
            file_name="planning_gantt_glostrup.csv",
            mime="text/csv"
        )

    # FR : Gantt Naestved
    # EN : Gantt chart for Naestved
    with sous_tab_gantt_b:
        st.markdown(f"### {t('Planning', lang)} - {t('Depot de Naestved', lang)}")
        fig_gantt_b = creer_gantt_occupation_depot(
            st.session_state.simulation, "Naestved", t, lang
        )
        st.plotly_chart(fig_gantt_b, use_container_width=True)
        # Export Gantt Naestved
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
        csv_gantt_b = df_gantt_b.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button(
            label="📥 Télécharger le planning Gantt Naestved (CSV)",
            data=csv_gantt_b,
            file_name="planning_gantt_naestved.csv",
            mime="text/csv"
        )
    legend_items = [
        (t("testing", lang), "red"),
        (t("storage", lang), "blue"),
        (t("pit", lang), "green"),
        (t("electric_train", lang), "black", "x"),
    ]
    def make_legend_html(legend_items):
        html = ""
        for label, color, *pattern in legend_items:
            style = f"background:{color};border:1px solid #333;width:20px;height:20px;display:inline-block;margin-right:8px;"
            if pattern:
                style += "background-image: repeating-linear-gradient(45deg, #fff 0, #fff 2px, #000 2px, #000 4px);"
            html += f'<span style="{style}"></span>{label} &nbsp; '
        return html
    
    legend_html_a = make_legend_html(legend_items)
    legend_html_b = make_legend_html(legend_items)
    
    # --- Génération et téléchargement du PDF pour les deux plannings ---
            
    if 'pdf_gantt_both' not in st.session_state:
        st.session_state.pdf_gantt_both = None
    
    def generate_pdf():
        try:
            return plotly_double_fig_to_pdf(fig_gantt_a, legend_html_a, fig_gantt_b, legend_html_b)
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF : {e}")
            return None
    
    if st.button("📄 " + t("generate_pdf", lang)):
        with st.spinner(t("generating_pdf", lang)):
            pdf = generate_pdf()
            if pdf:
                st.session_state.pdf_gantt_both = pdf
                st.success(t("pdf_ready", lang))
            else:
                st.session_state.pdf_gantt_both = None
    
    if st.session_state.pdf_gantt_both:
        st.download_button(
            label="⬇️ " + t("download_pdf", lang),
            data=st.session_state.pdf_gantt_both.getvalue(),  # <-- Ajoute .getvalue() ici
            file_name="planning_gantt_complet.pdf",
            mime="application/pdf"
        )

# ---------------------------------------------------------------------------
# FR : ONGLET 4 : STATISTIQUES GLOBALES
# EN : TAB 4: GLOBAL STATISTICS
# ---------------------------------------------------------------------------

with tab4:
    st.subheader(t("Statistiques globales", lang))

    # FR : Affichage sous forme de colonnes de métriques
    # EN : Display as metric columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=t("train_list", lang), value=stats['total_trains'])
        st.metric(label=t("Depot de Glostrup", lang), value=stats['trains_glostrup'])
        st.metric(label=t("Depot de Naestved", lang), value=stats['trains_naestved'])
    with col2:
        st.metric(label=t("electric_train", lang), value=stats['trains_electriques'])
        st.metric(label=t("average_wait", lang), value=f"{stats['temps_moyen_attente']} min")
    with col3:
        st.metric(label=t("occupancy_rate", lang), value=f"{stats['taux_occupation_global']}%")
        st.metric(label=f"{t('Depot de Glostrup', lang)}", value=f"{stats['taux_occupation_glostrup']}%")
        st.metric(label=f"{t('Depot de Naestved', lang)}", value=f"{stats['taux_occupation_naestved']}%")

    # FR : Graphique de répartition des trains par dépôt
    # EN : Pie chart of trains by depot
    import plotly.express as px
    depot_counts = [
        {"Depot": t("Depot de Glostrup", lang), "Trains": stats['trains_glostrup']},
        {"Depot": t("Depot de Naestved", lang), "Trains": stats['trains_naestved']}
    ]
    fig_depot = px.pie(
        depot_counts,
        names="Depot",
        values="Trains",
        title=t("train_list", lang),
        color_discrete_sequence=["#1976d2", "#4fc3f7"]
    )
    fig_depot.update_traces(
        textinfo='percent+label',
        pull=[0.05, 0],
        marker=dict(line=dict(color='#fff', width=2))
    )
    fig_depot.update_layout(
        title=dict(
            font=dict(size=22, family="Segoe UI, Arial"),
            x=0.5
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="#b0bec5",
            borderwidth=1
        ),
        plot_bgcolor="#f7fafc",
        paper_bgcolor="#f0f0f5",
        font=dict(family="Segoe UI, Arial", size=14, color="#222"),
        margin=dict(l=40, r=40, t=90, b=90)
    )
    st.plotly_chart(fig_depot, use_container_width=True)

    # Bar chart by train type
    type_counts = {}
    for train in st.session_state.simulation.trains:
        type_label = t(train.type, lang)
        type_counts[type_label] = type_counts.get(type_label, 0) + 1
    if type_counts:
        fig_type = px.bar(
            x=list(type_counts.keys()),
            y=list(type_counts.values()),
            labels={"x": t("train_type", lang), "y": t("train_list", lang)},
            title=t("train_type", lang),
            color=list(type_counts.keys()),
            color_discrete_sequence=["#1976d2", "#e74c3c", "#27ae60", "#f39c12", "#8e44ad"]
        )
        fig_type.update_traces(
            marker_line_color='#222',
            marker_line_width=2,
            opacity=0.85
        )
        fig_type.update_layout(
            title=dict(
                font=dict(size=22, family="Segoe UI, Arial"),
                x=0.5
            ),
            plot_bgcolor="#f7fafc",
            paper_bgcolor="#f0f0f5",
            font=dict(family="Segoe UI, Arial", size=14, color="#222"),
            margin=dict(l=40, r=40, t=90, b=90),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#e0eafc"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="left",
                x=0,
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="#b0bec5",
                borderwidth=1
                ),
            )
        st.plotly_chart(fig_type, use_container_width=True)
    
# ---------------------------------------------------------------------------
# FR : ONGLET 5 : REQUIREMENTS (BESOINS EN RESSOURCES)
# EN : TAB 5: REQUIREMENTS (RESOURCE NEEDS)
# ---------------------------------------------------------------------------

with tab5:
    st.subheader(t("requirements", lang))
    requirements = calculer_requirements(st.session_state.simulation.trains, t, lang)
    requirements_par_jour = regrouper_requirements_par_jour(st.session_state.simulation.trains, t, lang)

    # FR : Affichage global des besoins
    # EN : Global requirements display
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=t("test_drivers", lang), value=requirements["test_drivers"])
    with col2:
        st.metric(label=t("locomotives", lang), value=requirements["locomotives"])

    # FR : Détail par type de train
    # EN : Details by train type
    st.markdown("#### " + t("details", lang))
    details = []
    for train in st.session_state.simulation.trains:
        if train.type == "testing":
            details.append({
                t("train_name", lang): train.nom,
                t("train_type", lang): t(train.type, lang),
                t("arrival_time", lang): train.arrivee.strftime("%Y-%m-%d %H:%M"),
                t("departure_time", lang): train.depart.strftime("%Y-%m-%d %H:%M"),
                t("test_drivers", lang): 1,
                t("locomotives", lang): 2
            })
        # FR : Ajouter ici d'autres types si besoin
        # EN : Add other types here if needed

    if details:
        st.dataframe(pd.DataFrame(details), use_container_width=True)
    else:
        st.info(t("no_requirements", lang))

    # FR : Affichage par jour (déjà présent)
    # EN : Display by day (already present)
    if requirements_par_jour:
        st.write(f"### {t('requirements_by_day', lang)}")
        fig = creer_graphique_requirements_par_jour(requirements_par_jour, t, lang)
        fig_depot.update_layout(
            title=dict(
                text=t("train_list", lang),
                font=dict(size=22, family="Segoe UI, Arial"),
                x=0.5
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="left",
                x=0,
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="#b0bec5",
                borderwidth=1
            ),
            plot_bgcolor="#f7fafc",
            paper_bgcolor="#f0f0f5",
            font=dict(family="Segoe UI, Arial", size=14, color="#222"),
            margin=dict(l=40, r=40, t=90, b=80)
        )
        fig.update_traces(
            marker_line_color='#222',
            marker_line_width=2,
            opacity=0.9
        )
        st.plotly_chart(fig, use_container_width=True)
        # FR : Tableau exportable par jour
        # EN : Exportable table by day
        export_data = []
        for jour, besoins in sorted(requirements_par_jour.items()):
            for detail in besoins["details"]:
                export_data.append({
                    "Date": jour.strftime("%Y-%m-%d"),
                    t("train_name", lang): detail["train_name"],
                    t("arrival_time", lang): detail["start_time"],
                    t("departure_time", lang): detail["end_time"],
                    t("test_drivers", lang): besoins["test_drivers"],
                    t("locomotives", lang): besoins["locomotives"]
                })
        df_export = pd.DataFrame(export_data)
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False, sep=";", encoding="utf-8")
        st.download_button(
            label="📥 Télécharger les besoins (CSV)",
            data=csv_buffer.getvalue().encode("utf-8"),
            file_name="besoins_trains.csv",
            mime="text/csv"
        )
    else:
        st.info(t("no_requirements", lang))
        
# ---------------------------------------------------------------------------
# FR : ONGLET 6 : MINI-JEU DE GESTION DES VOIES
# EN : TAB 6: WAGON MANAGEMENT MINI-GAME
# ---------------------------------------------------------------------------

with tab6:
    import Jeu
    Jeu.main(lang)





