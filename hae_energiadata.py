import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def hae_hinta(url, tuote_nimi):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Virhe haettaessa tuotetta {tuote_nimi}: Status {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Haetaan päänumero divistä, jonka id on 'market_price'
        hinta_elementti = soup.find("div", {"id": "market_price"})
        
        if not hinta_elementti:
            hinta_elementti = soup.find("div", {"class": "table-responsive"})
        
        # Puhdistetaan teksti ja poistetaan tyhjät välit
        hinta_teksti = hinta_elementti.text.strip().split()[0]
        # Korvataan pilkut ja muutetaan numeroksi
        hinta = float(hinta_teksti.replace(',', ''))
        return hinta
    except Exception as e:
        print(f"Virhe tuotteen {tuote_nimi} kohdalla: {e}")
        return None

# Tuotteet ja niiden Trading Economics URL-osoitteet
tuotteet = {
    "EUA Carbon (Päästöoikeus)": "https://tradingeconomics.com",
    "WTI Crude Oil (Öljy)": "https://tradingeconomics.com",
    "Brent Crude Oil (Öljy)": "https://tradingeconomics.com",
    "API2 Coal (Hiili)": "https://tradingeconomics.com",
    "Dutch TTF Gas (Kaasu)": "https://tradingeconomics.com"
}

data_rivit = []
nykyhetki = datetime.now().strftime("%Y-%m-%d %H:%M")

for nimi, url in tuotteet.items():
    hinta = hae_hinta(url, nimi)
    if hinta is not None:
        data_rivit.append({
            "Aikaleima": nykyhetki,
            "Tuote": nimi,
            "Hinta": hinta
        })

if data_rivit:
    # KORJATTU: Muuttujan nimi on nyt yhtenäisesti uusi_df pienellä alkukirjaimella
    uusi_df = pd.DataFrame(data_rivit)
    tiedosto = "energiatietueet.csv"
    
    # Jos tiedosto on olemassa, lisätään uudet rivit vanhojen jatkoksi
    if os.path.exists(tiedosto):
        vanha_df = pd.read_csv(tiedosto)
        yhdistetty_df = pd.concat([vanha_df, uusi_df], ignore_index=True)
        yhdistetty_df.to_csv(tiedosto, index=False)
    else:
        uusi_df.to_csv(tiedosto, index=False)
        
    print("Markkinahinnat päivitetty onnistuneesti tiedostoon!")
else:
    print("Yhtään hintaa ei pystytty noutamaan.")
