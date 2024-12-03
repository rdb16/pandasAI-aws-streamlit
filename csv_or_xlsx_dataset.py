import os

import urllib3
import certifi
import streamlit as st
from PIL import Image
import boto3
from pandasai import SmartDataframe
from pandasai.llm import BedrockClaude
from pandasai.schemas.df_config import Config
import pandas as pd
from fpdf import FPDF
from pdf_utils import create_kai_pdf

# Définir le profil utilisateur pour AWS
user = 'bedrock_user'

# Créer une session boto3 avec le profil utilisateur
session = boto3.Session(profile_name=user)
bedrock_client = session.client('bedrock-runtime', region_name='eu-west-3')

# Configurer le modèle LLM Claude sur Bedrock
llm = BedrockClaude(
    bedrock_runtime_client=bedrock_client,
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    maxtokens=4000,
    temperature=0
)

# Configurer pandasAI
config = Config(
    llm=llm,
    save_charts=True,
    save_charts_path="./exports/charts"
)

# Configuration de la page
st.set_page_config(page_title="SNTP Capitalisation", page_icon="\U0001F4B0", layout="centered")

# Initialiser session_state pour session_data et les indicateurs de questions ajoutées
if 'session_data' not in st.session_state:
    st.session_state.session_data = []

if 'added_overview' not in st.session_state:
    st.session_state.added_overview = False

if 'added_summary' not in st.session_state:
    st.session_state.added_summary = False

if 'show_new_question_button' not in st.session_state:
    st.session_state.show_new_question_button = False

if 'show_envoyer_button' not in st.session_state:
    st.session_state.show_envoyer_button = True

if 'input_value' not in st.session_state:
    st.session_state.input_value = ""


# Fonction pour nettoyer le champ d'input
def clear_input():
    st.session_state.input_text = ""
    st.session_state.show_new_question_button = False
    st.session_state.show_envoyer_button = True


# Fonction pour traiter la question
def handle_question(prompt1, sdf1):
    with st.spinner(text='En attente de la réponse !!'):
        resp1 = sdf1.chat(prompt1)
        st.write(resp1)
        st.session_state.session_data.append({"question": prompt, "answer": resp1})
        st.session_state.show_new_question_button = True
        st.session_state.show_envoyer_button = False


# Chargement de l'image du logo
logo = Image.open("img/sntpk-ia-logo.jpeg")
# Insertion du logo réduit à la taille d'une icône
st.image(logo, width=140, caption=None)
# Titre en bleu roi
st.markdown("""
    <h1 style='text-align: center; color: royalblue;'>
        POC pour PandasAI <br> sur claude 3 dans Bedrock
    </h1>
""", unsafe_allow_html=True)

# Appliquer du style CSS au bouton "Envoyer"
st.markdown("""
    <style>
    .stButton>button {
        background-color: blue;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: darkblue;
    }
    </style>
""", unsafe_allow_html=True)

# Votre contenu principal ici
st.write("""Bienvenue sur notre plateforme""")
st.write(
    """Ici, vous allez pouvoir analyser votre Dataset, provenant soit d'un fichier csv ou (xsl | xslx).""")

# Footer avec les droits réservés
st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            color: black;
            text-align: center;
            padding: 10px;
        }
    </style>
    <div class="footer">
        &copy; 2024-2025 SNTP Capitalisation. Tous droits réservés.
    </div>
""", unsafe_allow_html=True)

# Choix du fichier à télécharger
uploaded_file = st.file_uploader("Choisissez un fichier (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    # Vérifier l'extension du fichier et charger le dataset
    data = None
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xls") or uploaded_file.name.endswith(".xlsx"):
        data = pd.read_excel(uploaded_file)
    else:
        st.error("Format de fichier non supporté.")

    if not st.session_state.added_overview:
        # Afficher un extrait du dataset
        st.markdown("""
                <h3 style='text-align: left; color: royalblue;'>
                <br>Aperçu du Dataset:<br> 
                </h3>
            """, unsafe_allow_html=True)
        if not data.empty:
            resp = data.head(3)
            # print(resp)
            st.write(resp)
            st.session_state.session_data.append({"question": "Aperçu du Dataset", "answer": resp})
            st.session_state.added_overview = True

    # Créer un SmartDataframe
    sdf = SmartDataframe(data, config=config)
    # Afficher un aperçu du Dataset
    if not st.session_state.added_summary:
        st.markdown("""
            <h3 style='text-align: left; color: royalblue;'>
            <br>
                Résumé du Dataset sélectionné :<br> 
            </h3>
        """, unsafe_allow_html=True)

        with st.spinner("En attente du résumé de ce dataset !!"):
            resp = sdf.chat("Merci de donner un résumé de ce dataset.")
            st.write(resp)
            st.session_state.session_data.append({"question": "Résumé du Dataset", "answer": resp})
            st.session_state.added_summary = True

    # Saisie du prompt
    st.markdown("""
            <h3 style='text-align: left; color: royalblue;'>
            <br>Maintenant, entrer vos questions ?  :<br> 
            </h3>
        """, unsafe_allow_html=True)
    prompt = st.text_area("Entrer votre prompt et cliquer sur envoyer!!", value=st.session_state.input_value,
                          key="input_text")

    # affichage des boutons das une ligne
    col1, col2 = st.columns([2, 1])
    with col1:
        # Bouton envoyer
        if st.session_state.show_envoyer_button:
            if st.button("Envoyer", key="envoyer"):
                if prompt.strip():
                    handle_question(prompt, sdf)

    with col2:
        # Bouton Nouvelle question (visible seulement après la réponse)
        if st.session_state.show_new_question_button:
            if st.button("Nouvelle question", key="nouvelle_question", help="Poser une nouvelle question",
                         use_container_width=True, on_click=clear_input):
                pass

    # JavaScript pour soumettre avec la touche "Enter"
    st.markdown("""
        <script>
        const textarea = document.querySelector("textarea");
        textarea.addEventListener("keydown", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                document.getElementById("envoyer-button").click();
            }
        });
        </script>
    """, unsafe_allow_html=True)

    # Bouton Archiver pour générer un PDF
    if st.button("Archiver", key="archiver", help="Générer un PDF", use_container_width=True):
        csv_name = os.path.basename(uploaded_file.name)
        pdf_path = create_kai_pdf(csv_name, sdf, st.session_state.session_data)

        st.success(f"PDF généré avec succès : {pdf_path}")
        st.write(f"[Télécharger le PDF]({pdf_path})")
