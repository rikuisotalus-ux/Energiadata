import requests
import pandas as pd
from datetime import datetime
import os

def hae_julkisesta_api(symboli, tuote_nimi):
    # KORJATTU: Vinoviiva on nyt varmasti paikoillaan muuttujan edessä
    url = f"https://yahoo.com{symboli}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            json_data = response.json()
            # Haetaan tuorein markkinahinta JSON-rakenteesta
            hinta = json_data['chart']['result'][0]['meta']['regularMarketPrice']
            print(f"Onnistui! {tuote_nimi}: {hinta}")
            return float(hinta)
        else:
            print(f"Rajapintavirhe tuotteelle {tuote_nimi}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Virhe noudettaessa tuotetta {tuote_nimi}: {e}")
        return None

# Pörssisymbolit:
tuotteet = {
    "EUA Carbon (Päästöoikeus)": "CARB.DE",    
    "WTI Crude Oil (Öljy)": "CL=F",            
    "Brent Crude Oil (Öljy)": "BZ=F",          
    "API2 Coal (Hiili)": "MTF=F",              
    "Dutch TTF Gas (Kaasu)": "TTF=F"           
}

data_rivit = []
nykyhetki = datetime.now().strftime("%Y-%m-%d %H:%M")

for nimi, symboli in tuotteet.items():
    hinta = hae_julkisesta_api(symboli, nimi)
    if hinta is not None:
        data_rivit.append({
            "Aikaleima": nykyhetki,
            "Tuote": nimi,
            "Hinta": hinta
        })

# Jos kaikki haut jostain syystä epäonnistuisivat
if not data_rivit:
    data_rivit.append({
        "Aikaleima": nykyhetki,
        "Tuote": "VIRHE - Yhteyttä rajapintaan ei saatu",
        "Hinta": 0.0
    })

uusi_df = pd.DataFrame(data_rivit)
tiedosto = "energiatietueet.csv"

# Tallennetaan tiedot ja kasvatetaan historiadataa
if os.path.exists(tiedosto):
    vanha_df = pd.read_csv(tiedosto)
    yhdistetty_df = pd.concat([vanha_df, uusi_df], ignore_index=True)
    yhdistetty_df.to_csv(tiedosto, index=False)
else:
    uusi_df.to_csv(tiedosto, index=False)

print("Tiedosto 'energiatietueet.csv' päivitetty onnistuneesti!")
