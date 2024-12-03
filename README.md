## structure
mkdir exports
mkdir Results
## aws
ce code utilise le service Bedrock AWS. Placer les credentials à la racine du /home dans le dossier .aws
## export est donné dans la config de pandasai pour l'export des graphes
pandasAI retourne à l'app le chemin du fichier et place le png directement dans ce rep
## streamlit est stateless; mais on peut lui donner un objet session pour suivre l'historique.
## Nota chaque évènement utilisateur rejoue la totalité du code
##