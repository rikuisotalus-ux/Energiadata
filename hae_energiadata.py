import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Määritetään pörssisymbolit (Päästöoikeudelle kaksi eri vaihtoehtoa vikasietoisuuden vuoksi)
tuotteet = {
    "WTI Crude Oil (Öljy)": "CL=F",            
    "Brent Crude Oil (Öljy)": "BZ=F",          
    "API2 Coal (Hiili)": "MTF=F",              
    "Dutch TTF Gas (Kaasu)": "TTF=F"           
}

data_rivit = []
nykyhetki = datetime.now().strftime("%Y-%m-%d %H:%M")

# 1. Yritetään hakea EUA Carbon kahdella eri Yahoo-symbolilla
eua_hinta = None
for eua_symboli in ["CARB.L", "WCO2.DE"]:
    try:
        ticker = yf.Ticker(eua_symboli)
        hinta = ticker.info.get('regularMarketPrice')
        if hinta is None:
            historia = ticker.history(period="1d")
            if not historia.empty:
                hinta = historia['Close'].iloc[-1]
        
        if hinta is not None and float(hinta) > 0:
            eua_hinta = float(hinta)
            print(f"Onnistui! EUA Carbon (Päästöoikeus) haettu symbolilla {eua_symboli}: {eua_hinta}")
            break
    except Exception as e:
        print(f"Symboli {eua_symboli} ei toiminut: {e}")

# Lisätään päästöoikeus listalle jos hinta löytyi
if eua_hinta is not None:
    data_rivit.append({
        "Aikaleima": nykyhetki,
        "Tuote": "EUA Carbon (Päästöoikeus)",
        "Hinta": eua_hinta
    })
else:
    print("Hintaa ei saatu tuotteelle EUA Carbon millään symbolilla.")

# 2. Haetaan muut neljä toimivaa tuotetta
for nimi, symboli in tuotteet.items():
    try:
        ticker = yf.Ticker(symboli)
        hinta = ticker.info.get('regularMarketPrice')
        
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
    except Exception as e:
        print(f"Virhe tuotteen {nimi} kohdalla: {e}")

# Tallennetaan tiedot ja kasvatetaan historiadataa
if data_rivit:
    uusi_df = pd.DataFrame(data_rivit)
    tiedosto = "energiatietueet.csv"
    
    if os.path.exists(tiedosto):
        vanha_df = pd.read_csv(tiedosto)
        # Puhdistetaan vanhasta tiedostosta mahdolliset aiemmat "VIRHE"-rivit pois sotkemasta
        vanha_df = vanha_df[vanha_df["Tuote"] != "VIRHE - Dataa ei saatu"]
        yhdistetty_df = pd.concat([vanha_df, uusi_df], ignore_index=True)
        yhdistetty_df.to_csv(tiedosto, index=False)
    else:
        uusi_df.to_csv(tiedosto, index=False)
    print("Tiedosto 'energiatietueet.csv' päivitetty onnistuneesti!")
