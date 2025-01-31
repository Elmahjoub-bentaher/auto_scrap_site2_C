from lxml import html
from tqdm import tqdm
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

# Fonction pour scraper les données d'une page
def scrape_product_page(url):
    # Initialiser le navigateur Selenium
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Mode headless (facultatif)
    options.add_argument("--disable-blink-features=AutomationControlled")  # Désactiver la détection d'automatisation
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    driver.implicitly_wait(10)
    html_content = driver.page_source
    driver.quit()  # Fermer le navigateur après avoir obtenu le contenu

    # Parser le contenu HTML avec lxml
    tree = html.fromstring(html_content)

    # Initialiser un dictionnaire pour stocker les données
    general_data = {}

    # Liste des clés statiques à rechercher
    static_keys = [
        "Nom du produit", 
        "Catégorie", 
        "Prix", 
        "Site web", 
        "Marque", 
        "Modèle de téléphone", 
        "Référence", 
        "RAM", 
        "Capacité (mémoire)", 
        "Couleur(s)"
    ]

    general_data['Nom du produit'] = tree.xpath("//tr[th[contains(text(),'Nom du produit')]]/td/text()")[0].strip() if tree.xpath("//tr[th[contains(text(),'Nom du produit')]]/td") else np.nan
    general_data['Marque'] = tree.xpath("//tr[th[contains(text(),'Marque')]]/td/a/text()")[0].strip() if tree.xpath("//tr[th[contains(text(),'Marque')]]/td/a/text()") else np.nan
    general_data["RAM"] = tree.xpath("//tr[th[contains(text(),'RAM')]]/td/text()")[0].strip() if tree.xpath("//tr[th[contains(text(),'RAM')]]/td/text()") else np.nan
    general_data["Capacité (mémoire)"] = tree.xpath("//tr[th[contains(text(),'Capacité (mémoire)')]]/td/text()")[0].strip() if tree.xpath("//tr[th[contains(text(),'Capacité (mémoire)')]]/td/text()") else np.nan
    general_data["Couleur(s)"] = tree.xpath("//tr[th[contains(text(),'Couleur(s)')]]/td/text()")[0].strip() if tree.xpath("//tr[th[contains(text(),'Couleur(s)')]]/td/text()") else np.nan
    general_data['Référence'] = tree.xpath("//tr[th[contains(text(),'Référence')]]/td/text()")[0].strip() if tree.xpath("//tr[th[contains(text(),'Référence')]]/td/text()") else np.nan
    general_data["Modèle de téléphone"] = tree.xpath("//tr[th[contains(text(),'Modèle de téléphone')]]/td/text()")[0].strip() if tree.xpath("//tr[th[contains(text(),'Modèle de téléphone')]]/td/text()") else np.nan        
    general_data['Prix'] = tree.xpath("//div[@class='c-buybox__price']/p[1]/span/@content")[0].strip() if tree.xpath("//div[@class='c-buybox__price']/p[1]/span") else np.nan
    general_data['Site web'] = "cdiscount.com"
    general_data['Catégorie'] = "SMARTPHONE"


    return general_data

# Fonction principale pour lire les liens, scraper les données et sauvegarder les résultats
def scrape_and_save(input_csv, output_csv):
    # Lire les liens depuis le fichier CSV
    df_links = pd.read_csv(input_csv)
    links = df_links['Smartphone'].tolist()  # Supposons que la colonne s'appelle "lien"

    # Initialiser une liste pour stocker les données de tous les produits
    all_data = []

    # Scraper chaque lien
    for link in tqdm(links, desc="Scraping progress"):
        # print(f"Scraping {link}...")
        try:
            product_data = scrape_product_page(link)
            all_data.append(product_data)

        except Exception as e:
            print(f"Erreur lors du scraping de {link}: {e}")

    # Convertir la liste de dictionnaires en DataFrame
    df_results = pd.DataFrame(all_data)

    # Sauvegarder les résultats dans un fichier CSV
    df_results.to_csv(output_csv, index=False)
    print(f"Les résultats ont été sauvegardés dans {output_csv}")

today_date = datetime.today().strftime('%Y-%m-%d')
input_csv = f"Links/Cdiscount_Liens_{today_date}.csv"
output_csv = f"Data/Smartphone_Data_Cdiscount_{today_date}.csv"  # Fichier CSV pour sauvegarder les résultats
scrape_and_save(input_csv, output_csv)
