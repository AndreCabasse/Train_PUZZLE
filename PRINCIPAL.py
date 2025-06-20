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
from streamlit_option_menu import option_menu
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

def plotly_multi_fig_to_pdf(figs, legends_html):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y_offset = height - 40

    for fig, legend_html in zip(figs, legends_html):
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
        c.drawImage(ImageReader(img_io), 20, y_offset - img_height, width=img_width, height=img_height)
        # Ajoute la légende si fournie
        from reportlab.lib.utils import simpleSplit
        legend_text = re.sub('<[^<]+?>', '', legend_html)
        legend_lines = simpleSplit(legend_text, "Helvetica", 12, width-40)
        y = y_offset - img_height - 20
        for line in legend_lines:
            c.drawString(30, y, line)
            y -= 15
        y_offset = y - 40
        if y_offset < 100:
            c.showPage()
            y_offset = height - 40
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

#----------------------------------------------------
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
# --- Fond gris clair pour toute l'app ---
st.markdown("""
    <style>
    body, .stApp, .block-container {
        background-color: #f4f6f8 !important;
    }
    </style>
""", unsafe_allow_html=True)
# --- CSS personnalisé pour un look moderne ---
st.markdown("""
    <style>
    /* --- Bandeau logo modernisé --- */
    .logo-bandeau {
        width:100%;
        background:linear-gradient(90deg,#ffffff 0%,#d32f2f 100%);
        padding:48px 0 32px 0;
        margin-bottom:18px;
        display:flex;
        justify-content:center;
        align-items:center;
        min-height:120px;
        border: 2px solid #e0e0e0;         /* Ajoute une bordure grise claire */
        border-radius: 18px;                /* Coins arrondis pour effet card */
    }
    .logo-bandeau img {
        max-height:80px;
        height:auto;
        object-fit:contain;
        margin-top:0;
        margin-bottom:0;
        filter: drop-shadow(0 2px 8px #b71c1c44);
    }

    /* --- Champs de formulaire --- */
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTimeInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox input {
        background: #fff8f8 !important;
        border: 2px solid #d32f2f !important;
        border-radius: 10px !important;
        color: #222 !important;
        box-shadow: 0 1px 4px #b71c1c11;
        font-size: 1.05em;
    }
    label, .stTextInput label, .stNumberInput label, .stDateInput label, .stTimeInput label {
        color: #b71c1c !important;
        font-weight: 600;
        letter-spacing: 0.01em;
    }
    /* ...autres styles... */

    /* Force un contour sur les time_input */
    .stTimeInput, .stTimeInput input, .stTimeInput div[data-baseweb="input"] {
        border: 2px solid #d32f2f !important;
        border-radius: 8px !important;
        background: #fff !important;
        box-shadow: 0 1px 2px #0001;
    }
    .stTimeInput:focus-within, .stTimeInput input:focus, .stTimeInput div[data-baseweb="input"]:focus-within {
        border: 2.5px solid #d32f2f !important;
        box-shadow: 0 0 0 2px #90caf9;
        outline: none !important;
    }

    /* --- DataFrames et tables --- */
    .stDataFrame, .stTable {
        background: #fff8f8 !important;
        border-radius: 14px;
        padding: 12px;
        box-shadow: 0 2px 12px #b71c1c11;
        border: 2px solid #d32f2f;
    }

    /* --- Tabs modernisés --- */
    .stTabs [data-baseweb="tab-list"] {
        background: #fbe9e7;
        border-radius: 10px;
        padding: 0.5em;
        border: 1.5px solid #d32f2f;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 700;
        color: #b71c1c;
        border-radius: 8px 8px 0 0;
        margin-right: 6px;
        font-size: 1.08em;
        transition: background 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #d32f2f !important;
        color: white !important;
        box-shadow: 0 2px 8px #b71c1c22;
    }

    /* --- Titres et sous-titres --- */
    h1, h2, h3, .stSubheader {
        color: #b71c1c !important;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 800;
        letter-spacing: 0.01em;
    }

    /* --- Boutons --- */
    .stButton>button {
        background-color: #d32f2f;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.6em 1.7em;
        border: none;
        font-size: 1.08em;
        box-shadow: 0 2px 8px #b71c1c22;
        transition: background 0.2s, box-shadow 0.2s;
    }
    .stButton>button:hover {
        background-color: #b71c1c;
        box-shadow: 0 4px 16px #b71c1c33;
    }

    /* --- Metrics --- */
    .stMetric {
        background: #fbe9e7;
        border-radius: 10px;
        padding: 10px 0;
        margin-bottom: 10px;
        border: 1.5px solid #d32f2f;
        color: #b71c1c !important;
        font-weight: 700;
    }

    /* --- Sidebar --- */
    .stSidebar .stSlider, .stSidebar .stSelectbox, .stSidebar .stButton {
        background: #fff8f8;
        border-radius: 10px;
        border: 1.5px solid #d32f2f;
    }
    .stSidebar .stSlider .st-cg {
        background: #d32f2f !important;
    }
    .stSidebar .stSlider .st-cg .st-ch {
        background: #b71c1c !important;
    }

    /* --- Divers --- */
    .stDivider { margin: 1.5em 0; }
    .block-container { padding-top: 1.5rem; }
    .stAlert {
        border-radius: 10px !important;
        border: 2px solid #d32f2f !important;
        background: #fff8f8 !important;
        color: #b71c1c !important;
    }
    </style>
""", unsafe_allow_html=True)


if st.session_state.get("dark_mode"):
    st.markdown("""
    <style>
    body, .stApp, .block-container {
        background: #181c24 !important;
        color: #e0e6ef !important;
    }
    .stDataFrame, .stTable {
        background: #232936 !important;
        color: #e0e6ef !important;
        border-color: #333 !important;
    }
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea {
        background: #232936 !important;
        color: #e0e6ef !important;
        border: 2px solid #333 !important;
    }
    label, .stTextInput label, .stNumberInput label, .stDateInput label, .stTimeInput label {
        color: #90caf9 !important;
    }
    .stButton>button {
        background: #232936 !important;
        color: #90caf9 !important;
        border: 1px solid #90caf9 !important;
    }
    .stButton>button:hover {
        background: #1976d2 !important;
        color: #fff !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #232936 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1976d2 !important;
        color: #fff !important;
    }
    .stSidebar {
        background: #181c24 !important;
    }
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
lang = st.sidebar.selectbox("Language", ["fr", "en", "da"], help="Choose the language")
t_dict = get_translation(lang)
st.sidebar.divider()

dark_mode = st.sidebar.toggle("🌙 Mode sombre", key="dark_mode")

with st.sidebar:
    selected_tab = option_menu(
        "Menu",
        [
            "➕ " + t("add_train", lang),
            "📋 " + t("train_list", lang),
            "📊 " + t("graph_title", lang),
            "📈 " + t("Statistiques", lang),
            "🛠️ " + t("requirements", lang),
            "🎮 " + t("Gestion des voies", lang),
            "🗺️ " + t("Carte", lang),
        ],
        icons=["plus", "list", "bar-chart", "graph-up", "tools", "controller", "map"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f0f5"},
            "icon": {"color": "#1976d2", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#e3f2fd"},
            "nav-link-selected": {"background-color": "#1976d2", "color": "white"},
        }
    )
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
st.sidebar.subheader(t("security_settings", lang), help=t("security_delay_tooltip",lang))
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
    
import pickle

st.sidebar.markdown("---")
st.sidebar.subheader(t("save_restore", lang))

# Export
if st.sidebar.button(t("export_simulation", lang), help=t( "export_simulation_tooltip",lang)):
    buffer = io.BytesIO()
    pickle.dump(st.session_state.simulation, buffer)
    buffer.seek(0)
    st.sidebar.download_button(
        label=t("download_simulation", lang),
        data=buffer,
        file_name="simulation.pkl",
        mime="application/octet-stream"
    )

# Import
uploaded_sim = st.sidebar.file_uploader(t("import_simulation", lang), type=["pkl"], help=t( "import_simulation_tooltip",lang))
if uploaded_sim:
    if st.sidebar.button(t("load_this_file", lang), help=t("load_this_file_tooltip",lang)):
        try:
            simulation_importee = pickle.load(uploaded_sim)
            st.session_state.simulation = simulation_importee
            st.success(t("import_success_sim", lang))
            st.experimental_set_query_params(imported="1")
            st.rerun()
        except Exception as e:
            st.error(t("import_error_sim", lang, e=e))

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



# ---------------------------------------------------------------------------
# FR : ONGLET 1 : AJOUT / MODIFICATION / SUPPRESSION DE TRAINS
# EN : TAB 1: ADD / MODIFY / DELETE TRAINS
# ---------------------------------------------------------------------------

if selected_tab == "➕ " + t("add_train", lang):
    sous_tab_ajout, sous_tab_modif, sous_tab_suppr = st.tabs([
        t("add_train", lang),
        t("modify_train", lang),
        t("delete_train", lang)
    ])
    with sous_tab_ajout:
        # FR : Formulaire d'ajout d'un train
        # EN : Form to add a new train
        afficher_formulaire_ajout(st.session_state.simulation, lang, t)
        st.divider() 
    with sous_tab_modif:
        # FR : Formulaire de modification d'un train existant
        # EN : Form to modify an existing train
        afficher_modification_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)
        st.divider() 
    with sous_tab_suppr:
        # FR : Formulaire de suppression d'un train
        # EN : Form to delete a train
        afficher_suppression_train(st.session_state.simulation.trains, st.session_state.simulation, t, lang)
        st.divider() 

# ---------------------------------------------------------------------------
# FR : ONGLET 2 : LISTE DES TRAINS PAR DÉPÔT
# EN : TAB 2: LIST OF TRAINS BY DEPOT
# ---------------------------------------------------------------------------

elif selected_tab == "📋 " + t("train_list", lang):
    for depot in st.session_state.simulation.depots.keys():
        st.subheader(depot)
        afficher_tableau_trains(
            [train for train in st.session_state.simulation.trains if train.depot == depot],
            st.session_state.simulation, t, lang
        )
        st.divider()  

# ---------------------------------------------------------------------------
# FR : ONGLET 3 : VISUALISATIONS GRAPHIQUES
# EN : TAB 3: VISUALIZATIONS (OCCUPATION, EXPORT, GANTT, ETC.)
# ---------------------------------------------------------------------------
elif selected_tab == "📊 " + t("graph_title", lang):
    depot_names = list(st.session_state.simulation.depots.keys())
    sous_tabs = [t("graph_title", lang), "Export", t("train_length_by_track", lang), "Gantt"]
    sous_tabs_objs = st.tabs(sous_tabs)
    sous_tab_occ, sous_tab_export, sous_tab_instant, sous_tab_gantt = sous_tabs_objs
    
    # FR : Visualisation occupation des voies pour chaque dépôt
    # EN : Occupation visualization for each depot
    with sous_tab_occ:
        for depot in depot_names:
            st.subheader(depot)
            fig = creer_graphique_occupation_depot(
                st.session_state.simulation, depot, st.session_state.base_time, t, lang
            )
            st.plotly_chart(fig, use_container_width=True)
            st.divider() 
        
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
        # Ajout du selectbox pour choisir le dépôt à afficher
        depot_select = st.selectbox("Dépôt à afficher", depot_names, key="depot_select_longueur")
        st.subheader(depot_select)
        fig_trains_instant = creer_graphique_trains_par_longueur_detaille(
            st.session_state.simulation, t, instant, lang, depot=depot_select
        )
        st.plotly_chart(fig_trains_instant, use_container_width=True) 

    with sous_tab_gantt:
        depot_gantt = st.selectbox("Dépôt à afficher", depot_names, key="depot_select_gantt")
        st.markdown(f"### {t('Planning', lang)} - {depot_gantt}")
        fig_gantt = creer_gantt_occupation_depot(
            st.session_state.simulation, depot_gantt, t, lang
        )
        st.plotly_chart(fig_gantt, use_container_width=True)
        # Export Gantt
        occupation = st.session_state.simulation.depots[depot_gantt]["occupation"]
        numeros_voies = st.session_state.simulation.depots[depot_gantt]["numeros_voies"]
        data_gantt = []
        for voie_idx, debut, fin, train in occupation:
            data_gantt.append({
                "Voie": numeros_voies[voie_idx],
                "Début": debut.strftime("%Y-%m-%d %H:%M"),
                "Fin": fin.strftime("%Y-%m-%d %H:%M"),
                "Train": train.nom,
                "Type": t(train.type, lang) if hasattr(train, "type") else "",
                "Électrique": "⚡" if getattr(train, "electrique", False) else "",
            })
        df_gantt = pd.DataFrame(data_gantt)
        csv_gantt = df_gantt.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button(
            label=f"📥 Télécharger le planning Gantt {depot_gantt} (CSV)",
            data=csv_gantt,
            file_name=f"planning_gantt_{depot_gantt.lower()}.csv",
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
        
    figs_gantt = []
    legends_html = []
    for depot in depot_names:
        fig = creer_gantt_occupation_depot(st.session_state.simulation, depot, t, lang)
        figs_gantt.append(fig)
        legends_html.append(make_legend_html(legend_items))
        
    def generate_pdf():
        try:
            return plotly_multi_fig_to_pdf(figs_gantt, legends_html)
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

elif selected_tab == "📈 " + t("Statistiques", lang):
    st.subheader(t("Statistiques globales", lang))

    # FR : Affichage sous forme de colonnes de métriques
    # EN : Display as metric columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=t("train_list", lang), value=stats['total_trains'])
        st.metric(label=t("electric_train", lang), value=stats['trains_electriques'])
    with col2:
        st.metric(label=t("average_wait", lang), value=f"{stats['temps_moyen_attente']} min")
        st.metric(label=t("occupancy_rate", lang), value=f"{stats['taux_occupation_global']}%")
    with col3:
        for depot, depot_stats in stats['stats_par_depot'].items():
            st.metric(label=f"{depot}", value=f"{depot_stats['trains']} trains / {depot_stats['taux_occupation']}%")
    st.divider()
    # FR : Graphique de répartition des trains par dépôt
    # EN : Pie chart of trains by depot
    import plotly.express as px
    depot_counts = [
        {"Depot": depot, "Trains": depot_stats["trains"]}
        for depot, depot_stats in stats['stats_par_depot'].items()
    ]
    if depot_counts:
        fig_depot = px.pie(
            depot_counts,
            names="Depot",
            values="Trains",
            title=t("train_list", lang),
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_depot, use_container_width=True)
    st.divider()
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

elif selected_tab == "🛠️ " + t("requirements", lang):
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
    st.divider()
    # Affichage des besoins par dépôt
    if "by_depot" in requirements and requirements["by_depot"]:
        st.markdown("###  " + t("Besoins par dépôt", lang))
        for depot, besoins in requirements["by_depot"].items():
            st.write(f"**{depot}** : {besoins['test_drivers']} {t('test_drivers', lang)}, {besoins['locomotives']} {t('locomotives', lang)}")
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
                t("locomotives", lang): 2,
                t("Dépôt", lang): train.depot
            })
        # FR : Ajouter ici d'autres types si besoin
        # EN : Add other types here if needed

    if details:
        st.dataframe(pd.DataFrame(details), use_container_width=True)
    else:
        st.info(t("no_requirements", lang))
    st.divider()
    # FR : Affichage par jour (déjà présent)
    # EN : Display by day (already present)
    if requirements_par_jour:
        st.write(f"### {t('requirements_by_day', lang)}")
        fig = creer_graphique_requirements_par_jour(requirements_par_jour, t, lang)
        # Remplace fig_depot.update_layout(...) par fig.update_layout(...)
        fig.update_layout(
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
elif selected_tab == "🎮 " + t("Gestion des voies", lang):
    import Jeu
    Jeu.main(lang)   
# ---------------------------------------------------------------------------
# FR : ONGLET 7 : Carte du Danemark
# EN : TAB 7: Denmark map
# ---------------------------------------------------------------------------
elif selected_tab == "🗺️ " + t("Carte", lang):
    from Carte import afficher_carte_depots
    from Carte import afficher_carte_etat_trains_heure
    st.subheader(t("Carte des dépôts", lang))
    afficher_carte_depots(st.session_state.simulation, t, lang)
    st.divider()
    afficher_carte_etat_trains_heure(st.session_state.simulation, t, lang)
