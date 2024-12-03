import certifi
import streamlit as st
import urllib3


# Exemple de requête HTTPS utilisant un contexte certifi si nécessaire
def send_ext_request(url):
    try:
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        response = http.request('GET', url)
        if response.status == 200:
            st.write("Requête réussie vers un serveur externe !")
        else:
            st.error(f"Requête vers {url} a échoué avec le statut: {response.status}")
    except Exception as e:
        st.error(f"Erreur lors de la connexion à {url}: {e}")


url = "https://example.com"
send_ext_request(url)
