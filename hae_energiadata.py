import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Määritetään pörssisymbolit
tuotteet = {
    "EUA Carbon (Päästöoikeus)": "CARB.DE",    
    "WTI Crude Oil (Öljy)": "CL=F",            
    "Brent Crude Oil (Öljy)": "BZ=F",          
    "API2 Coal (Hiili)": "MTF=F",              
    "Dutch TTF Gas (Kaasu)": "TTF=F"           
}

data_rivit = []
nykyhetki = datetime.now().strftime("%Y-%m-%d %H:%M")

# Haetaan hinnat yfinance-kirjaston kautta
for nimi, symboli in tuotteet.items():
    try:
        ticker = yf.Ticker(symboli)
        # Haetaan tuorein regularMarketPrice
        hinta = ticker.info.get('regularMarketPrice')
        
        # Jos info-rakenne on tyhjä, haetaan viimeisin hinta historiadatasta
        if hinta is None:
            historia = ticker.history(period="1d")
            if not historia.empty:
                hinta = historia['Close'].iloc[-1]
                
        if hinta is not None:
            print(f"Onnistui! {nimi}: {hinta}")
            data_rivit.append({
                "Aikaleima": nykyhetki,
                "Tuote": nimi,
                "Hinta": float(hinta)
            })
        else:
            print(f"Hintaa ei saatu tuotteelle {nimi}")
            
    except Exception as e:
        print(f"Virhe tuotteen {nimi} kohdalla: {e}")

# Jos kaikki haut epäonnistuisivat
if not data_rivit:
    data_rivit.append({
        "Aikaleima": nykyhetki,
        "Tuote": "VIRHE - Dataa ei saatu yfinance-kirjastosta",
        "Hinta": 0.0
    })

uusi_df = pd.DataFrame(data_rivit)
tiedosto = "energiatietueet.csv"

# Tallennetaan tai kasvatetaan historiadataa
if os.path.exists(tiedosto):
    vanha_df = pd.read_csv(tiedosto)
    yhdistetty_df = pd.concat([vanha_df, uusi_df], ignore_index=True)
    yhdistetty_df.to_csv(tiedosto, index=False)
else:
    uusi_df.to_csv(tiedosto, index=False)

print("Tiedosto 'energiatietueet.csv' päivitetty onnistuneesti!")
