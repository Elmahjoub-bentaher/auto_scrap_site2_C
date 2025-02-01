import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import random
import os

# Création du dossier Links s'il n'existe pas
if not os.path.exists("Links"):
    os.makedirs("Links")

# Configuration de Selenium
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Mode headless (facultatif)
options.add_argument("--disable-blink-features=AutomationControlled")  # Désactiver la détection d'automatisation
options.add_argument("--no-sandbox")  # Utile pour GitHub Actions
options.add_argument("--disable-dev-shm-usage")  # Évite les erreurs de mémoire partagée
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(10)

# Configuration
target_hrefs = 500  # Nombre total de liens à scraper par catégorie
categories = {
    "Smartphone": "smartphone",
    "Ordinateur": "ordinateur+portable",
    "Moniteur": "moniteur",
    "Disque_dur": "disque+dur"
}

def scrape_hrefs(request, target_hrefs):
    """Scrape les liens de la catégorie demandée."""
    hrefs = []
    page = 1 
    retries = 3  # Nombre d'essais en cas d'erreur

    while len(hrefs) < target_hrefs:
        url = f"https://www.cdiscount.com/search/10/{request}.html?&page={page}"
        try:
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lpBloc > li.abLabel > div > div > form > div.prdtBILDetails > a"))
            )
        except (TimeoutException, Exception) as e:
            print(f"Erreur lors du chargement de la page {page} pour {request}: {e}")
            if retries > 0:
                print(f"Tentative de rechargement ({retries} essais restants)...")
                retries -= 1
                time.sleep(random.uniform(3, 6))
                continue  
            else:
                print(f"Passage forcé à la page suivante après plusieurs échecs ({page}).")
                page += 1
                retries = 3  # Réinitialiser pour la page suivante
                continue  

        # Récupération des liens
        elements = driver.find_elements(By.CSS_SELECTOR, "#lpBloc > li.abLabel > div > div > form > div.prdtBILDetails > a")
        for element in elements:
            href = element.get_attribute("href")
            if href and href not in hrefs:
                hrefs.append(href)
                if len(hrefs) >= target_hrefs:
                    break
        
        try:
            driver.find_element(By.XPATH, "//div[@class='pgLightPrevNext']/input[@value='Page suivante']")
        except NoSuchElementException:
            print(f"📌 Fin des pages pour {request} (page {page}).")
            break  

        page += 1
        retries = 3  # Réinitialiser les essais pour la nouvelle page
        time.sleep(random.uniform(2, 5))

    time.sleep(random.uniform(6, 8))
    return hrefs


# Scraper chaque catégorie et sauvegarder séparément
today_date = datetime.today().strftime('%Y-%m-%d')

for category, request in categories.items():
    print(f"Scraping {category}...")
    hrefs = scrape_hrefs(request, target_hrefs)

    if hrefs:
        df = pd.DataFrame(hrefs, columns=["Lien"])
        filename = f"Links/Cdiscount_Liens_{category}_{today_date}.csv"
        df.to_csv(filename, index=False)
        print(f"{len(hrefs)} liens sauvegardés dans {filename}.")
    else:
        print(f"Aucun lien trouvé pour {category}.")

# Fermer Selenium
driver.quit()
print("Scraping terminé pour toutes les catégories.")
