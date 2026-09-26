#!/usr/bin/env python3

import os
from datetime import datetime
import subprocess

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

##########
# CONFIG #
##########

K8SNODENAME = os.environ.get("K8SNODENAME", "localhost.home.arpa")
EXCEL_PATH  = f"YahooFinanceHistory-{K8SNODENAME}.xlsx"
PDF_PATH    = f"YahooFinanceHistory-{K8SNODENAME}.pdf"
FROM_DATE   = "2025-01-01"

TICKERS = [
    # NAC - VARIABLE
    ## IPSA
    'SPIPSA.SN',                #       - S&P IPSA Index
    'CFMITNIPSA.SN',            # 99.44 - ETF/ITAU IPSA
    'CFIETFIPSA.SN',            # 94.44 - ETF/Singular IPSA
    'CFIBTGIPSA.SN',            # 00.00 - ETF/BTG IPSA
    ## Acciones Nacionales
    'CFMLVENFR.SN',             # 67.78 - CFM/LarrainVial Enfoque - NO-YAHOO
    'CFIPIONERO.SN',            # 80.00 - CFI/Moneda Pionero

    # NAC - FIJA - Corto
    'CFIETFCD.SN',              #100.00 - ETF/Singular Corto Duracion
    'CFIAMSLPA.SN',             # 45.00 - CFI/Ameris Corto Plazo
    # NAC - FIJA - Mediano
    'CFIETFCC.SN',              #100.00 - ETF/Singular Chile Corporativo
    'CFIBTETFMP.SN',            # 77.22 - ETF/BTG Medio Plazo
    # NAC - FIJA - Largo
    'CFIETFLP.SN',              # 94.44 - ETF/Singular Largo Plazo
    'CFIETFRFLP.SN',            # 00.00 - ETF/BTG Largo Plazo
    'CFIFALCFIG.SN',            # 96.11 - CFI/Falcon Fixed Income
    'CFIMRCLP.SN',              # 99.44 - CFI/Moneda Renta CLP
    'CFIMBIDA-A.SN',            # 71.11 - CFI/MBI Deuda Alternativa
    # NAC - Mixto
    'CFIMBIRF-A.SN',            # 97.78 - CFI/MBI Deuda Plus 15 variable 85 fijo
    'CFI4060ETF.SN',            # 31.11 - ETF/Singular 40 variable 60 fija

    # NAC - ALTERNATIVA
    'CFINRENTAS.SN',            # 79.44 - CFI/Independencia Rentas Inmobiliarias

    # INT - VARIABLE
    ## Total World
    'GEISAC.FGI',               #       - Global / World Equity Index
    'ACWI',                     #       - iShares MSCI ACWI ETF
    'VT',                       #       - Vanguard Total World Stock ETF
    'CFIETFGE.SN',              #100.00 - ETF/Singular Global Equity
    'CFIBTETFTW.SN',            # 00.00 - ETF/BTG Total World
    ## S&P-500
    '^GSPC',                    #       - S&P 500 Index
    'ES=F',                     #       - E-mini S&P 500 Future
    'CFISPETF.SN',              # 99.44 - ETF/Singular S&P-500
    'CFIETFUSA.SN',             # 00.00 - ETF/BTG USA
    ## Nasdaq
    '^IXIC',                    #       - Nasdaq Composite Index
    '^NDX',                     #       - Nasdaq-100 Index
    'NQ=F',                     #       - E-mini Nasdaq-100 Future
    'CFINASDAQ.SN',             # 86.67 - ETF/Singular Nasdaq
    ## Russell
    '^RUT',                     #       - Russell 2000 Index
    ## Dow Jones
    '^DJI',                     #       - Dow Jones Industrial Average
    ## Europe
    '^STOXX50E',                #       - EURO STOXX 50 Index
    'CFIETFEUR.SN',             # 00.00 - ETF/Singular Europe
    'CFIETFEUE.SN',             # 00.00 - ETF/BTG Europe
    ## Asia
    '^N225',                    #       - Nikkei 225
    '^HSI',                     #       - Hang Seng Index
    ## Emerging Markets
    'IEMG',                     #       - iShares Core MSCI Emerging Markets ETF
    'CFIETFEM.SN',              # 00.00 - ETF/Singular Emerging Markets
    'CFIETFGEM.SN',             # 00.00 - ETF/BTG Emerging Markets
    ## Latin America
    'EWZ',                      #       - iShares MSCI Brazil ETF
    'CFIETFBRE.SN',             # 00.00 - ETF/Singular Brazil
    'CFIETFLAT.SN',             # 00.00 - ETF/BTG Latin America
    ## DVA
    'CFIAMDVASC.SN',            # 90.00 - CFI/AmerisDVA Silicon
    'CFIADVAEFA.SN',            # 00.00 - CFI/AmerisDVA EFA
    'CFIAMDVATA.SN',            # 00.00 - CFI/AmerisDVA MedTech

    # INT - FIJA
    'CFIGC.SN',                 # 47.78 - ETF/Singular Global Corporate
    'CFIETFBRL.SN',             # 29.44 - ETF/Singular Fixed Income BRL
    'CFIETFHY.SN',              # 00.00 - ETF/Singular High Yield

    # INT - ALTERNATIVA
    'BTC-USD',                  # 00.00 - Bitcoin to USD
    'CFIETFBTC.SN',             # 00.00 - ETF/Singular Bitcoin

    # MACRO / FX / RISK
    'CLP=X',                    #       - USD/CLP
    'DX-Y.NYB',                 #       - U.S. Dollar Index (DXY)
    '^VIX',                     #       - CBOE Volatility Index
    'EURUSD=X',                 #       - EUR/USD
    'EURCLP=X',                 #       - EUR/CLP
    'BRL=X',                    #       - USD/BRL
    'BRLCLP=X',                 #       - BRL/CLP

    # RATES
    '^FVX',                     #       - U.S.  5Y Treasury Yield
    '^TNX',                     #       - U.S. 10Y Treasury Yield
    '^TYX',                     #       - U.S. 30Y Treasury Yield

    # COMMODITIES
    'HG=F',                     #       - Copper Future
    'GC=F',                     #       - Gold Future
    'CL=F',                     #       - WTI Crude Oil Future
    'BZ=F',                     #       - Brent Crude Oil Future
    'NG=F',                     #       - Natural Gas Future
]

def load_existing_data(path: str) -> dict:
    data = {}
    if os.path.exists(path):
        print("[LOAD] Loading existing Excel")
        xls = pd.ExcelFile(path)
        for sheet in xls.sheet_names:
            data[sheet] = pd.read_excel(
                xls, sheet_name=sheet, index_col=0, parse_dates=True
            )

    return data

def update_data(existing_data: dict, tickers: list) -> dict:
    updated = {}
    for ticker in tickers:
        print(f"[DUMP] {ticker}")
        df_new = yf.Ticker(ticker).history(period="5d", interval="1d")[["Open", "Low", "High", "Close"]]

        if df_new.empty:
            print(f"[WARN] No data for {ticker}")

        df_new.index = pd.to_datetime(df_new.index).tz_localize(None)

        if ticker in existing_data:
            df = pd.concat([existing_data[ticker], df_new])
            df = df[~df.index.duplicated(keep="last")]
            df.sort_index(inplace=True)
        else:
            df = df_new

        updated[ticker] = df
    return updated

def save_excel(data: dict, path: str) -> None:
    print("[SAVE] Writing Excel")
    with pd.ExcelWriter(path, engine="openpyxl", mode="w") as writer:
        for ticker, df in data.items():
            df.to_excel(writer, sheet_name=ticker)

def plot_to_pdf(data: dict, path: str, from_date: str) -> None:
    print("[PLOT] Generating PDF")

    dffx = data.get("CLP=X")
    if dffx is None:
        raise RuntimeError("CLP=X required for FX normalization")

    dffx = dffx[dffx.index >= from_date]

    with PdfPages(path) as pdf:
        for ticker, df in data.items():
            print(f"[PLOT] {ticker}")

            df = df[df.index >= from_date].copy()
            if df.empty:
                continue

            df[['Open', 'Low', 'High', 'Close']] = df[['Open', 'Low', 'High', 'Close']].astype(float)
            df["Close"] = df["Close"].replace(0.0, np.nan).ffill()

            for c in ['Open', 'Low', 'High']:
                df.loc[df[c].isna() | (df[c] == 0), c] = df['Close']

            df['LogReturn'] = np.log(df['Close'] / df['Close'].shift(20))

            fig, ax1 = plt.subplots(figsize=(10, 6))
            ax1.plot(df.index, df["Low"], label="Low")
            ax1.plot(df.index, df["High"], label="High")
            ax1.set_ylabel("Precio")
            ax1.grid(alpha=0.3)

            ax2 = ax1.twinx()
            ax2.plot(df.index, df["LogReturn"], linestyle=":", color="grey", label="LogReturn-20")
            ax2.set_ylabel("LogReturn")
            ax2q = df['LogReturn'].abs().quantile(0.9)
            if np.isnan(ax2q):
                print(f"[WARN] LogReturn quantile 90% NaN para {ticker}")
                ax2q = 0.05
            ax2.set_ylim(-ax2q, ax2q)

            lines = ax1.get_lines() + ax2.get_lines()
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc="best")

            ax1.set_title(f"High, Low y LogReturn - {ticker}")

            gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fig.text(0.9, 0.1, f"Generado: {gen_time}",ha="right", va="bottom", fontsize=10)

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

def rclone_copy(src: str, dst: str) -> None:
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            print("[SKIP] rclone disabled in IPython")
            return
    except ImportError:
        pass

    if not os.path.exists(src):
        raise FileNotFoundError(src)    
    print(f"[UPLOAD] {src} -> {dst}")
    result = subprocess.run(["rclone", "copy", src, dst],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())

def main():
    existing = load_existing_data(EXCEL_PATH)
    updated = update_data(existing, TICKERS)
    save_excel(updated, EXCEL_PATH)
    plot_to_pdf(updated, PDF_PATH, FROM_DATE)
    rclone_copy(EXCEL_PATH, "dropbox:local-m0net/docs-stocks/")
    rclone_copy(PDF_PATH,   "dropbox:local-m0net/docs-stocks/")

if __name__ == "__main__":
    main()

# eof
