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
        
        # Trading Economicsin nykyinen hintaelementti löytyy divistä, jonka id on 'market_price'
        hinta_elementti = soup.find("div", {"id": "market_price"})
        
        if not hinta_elementti:
            # Varavaihtoehto: etsitään datataulukon solusta
            hinta_elementti = soup.find("div", {"class": "table-responsive"})
            
        if hinta_elementti:
            # Puhdistetaan teksti: otetaan pelkkä ensimmäinen sana (itse hinta) ja poistetaan tyhjät välit
            raaka_teksti = hinta_elementti.text.strip().split()[0]
            # Poistetaan tuhansien erottimet (pilkut) ja muutetaan numeroksi
            hinta = float(raaka_teksti.replace(',', ''))
            print(f"Haettu {tuote_nimi}: {hinta}")
            return hinta
        else:
            print(f"Hintaelementtiä ei löytynyt tuotteelle {tuote_nimi}")
            return None
            
    except Exception as e:
        print(f"Virhe tuotteen {tuote_nimi} kohdalla: {e}")
        return None

# Tuotteet ja niiden viralliset URL-osoitteet
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

# Varmistetaan, että tiedosto luodaan aina, vaikka jokin haku epäonnistuisi
if not data_rivit:
    print("Kaikki haut epäonnistuivat, luodaan tyhjä rivi virheen estämiseksi.")
    data_rivit.append({
        "Aikaleima": nykyhetki,
        "Tuote": "VIRHE - Dataa ei saatu",
        "Hinta": 0.0
    })

uusi_df = pd.DataFrame(data_rivit)
tiedosto = "energiatietueet.csv"

if os.path.exists(tiedosto):
    vanha_df = pd.read_csv(tiedosto)
    yhdistetty_df = pd.concat([vanha_df, uusi_df], ignore_index=True)
    yhdistetty_df.to_csv(tiedosto, index=False)
else:
    uusi_df.to_csv(tiedosto, index=False)
    
print("Tiedosto 'energiatietueet.csv' käsitelty onnistuneesti!")
