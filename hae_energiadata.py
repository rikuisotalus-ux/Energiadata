import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Määritetään pörssisymbolit
tuotteet = {
    "EUA Carbon (Päästöoikeus)": "CO2.L",
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
        else:
            print(f"Hintaa ei saatu tuotteelle {nimi}")
            
    except Exception as e:
        print(f"Virhe tuotteen {nimi} kohdalla: {e}")

if data_rivit:
    uusi_df = pd.DataFrame(data_rivit)
    
    # --- TIEODSTO 1: Historiadata (Kasvava tiedosto) ---
    tiedosto_historia = "energiatietueet.csv"
    if os.path.exists(tiedosto_historia):
        vanha_df = pd.read_csv(tiedosto_historia)
        vanha_df = vanha_df[~vanha_df["Tuote"].str.contains("VIRHE", na=False)]
        yhdistetty_df = pd.concat([vanha_df, uusi_df], ignore_index=True)
        yhdistetty_df.to_csv(tiedosto_historia, index=False)
    else:
        uusi_df.to_csv(tiedosto_historia, index=False)
        
    # --- TIEDOSTO 2: Vain viimeisin ajo (Ylikirjoittava tiedosto) ---
    tiedosto_viimeisin = "energiatietueet_viimeisin.csv"
    uusi_df.to_csv(tiedosto_viimeisin, index=False) # Tämä ylikirjoittaa tiedoston aina automaattisesti
    
    print("Molemmat tiedostot päivitetty onnistuneesti!")
else:
    print("Datan nouto epäonnistui, tiedostoja ei päivitetty.")
