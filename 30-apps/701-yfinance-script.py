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
'CFMITNIPSA.SN',  # Itau          - ETF It Now Acciones Chile
'CFIETFIPSA.SN',  # Singular      - ETF IPSA
'CFIBTGIPSA.SN',  # Btg Pactual   - ETF Acciones Chilenas IPSA
'CFMLVENFR.SN',   # Larrainvial   - Enfoque
'CFIPIONERO.SN',  # Moneda        - Pionero
'CFIETFCD.SN',    # Singular      - ETF Chile Corta Duracion
'CFIETFCC.SN',    # Singular      - ETF Chile Corporativo
'CFIBTETFMP.SN',  # Btg Pactual   - ETF Renta Fija Chile Mediano Plazo
'CFIETFLP.SN',    # Singular      - ETF Chile Largo Plazo
'CFIETFRFLP.SN',  # Btg Pactual   - ETF Renta Fija Chile Largo Plazo
'CFIFALCFIG.SN',  # Falcom        - Chilean Fixed Income
'CFIAMSLPA.SN',   # Ameris Aatech - Financiamiento Corto Plazo
'CFIMBIDA-A.SN',  # MBI           - Deuda Alternativa
'CFINRENTAS.SN',  # Independencia - Rentas Inmobiliarias
'CFIMRCLP.SN',    # Moneda        - Renta CLP
'CFIMBIRF-A.SN',  # MBI           - Deuda Plus
'CFI4060ETF.SN',  # Singular      - ETF Core 40/60
'CFIETFGE.SN',    # Singular      - ETF Global Equities
'CFIBTETFTW.SN',  # Btg Pactual   - ETF Total World Equities
'CFISPETF.SN',    # Singular      - ETF S&P 500
'CFIETFUSA.SN',   # Btg Pactual   - ETF S&P 500
'CFINASDAQ.SN',   # Singular      - ETF Nasdaq 100
'CFIETFEUR.SN',   # Singular      - ETF Europe
'CFIETFEUE.SN',   # Btg Pactual   - ETF European Equities
'CFIETFEM.SN',    # Singular      - ETF Emerging Markets
'CFIETFGEM.SN',   # Btg Pactual   - ETF Global Emerging Markets Equities
'CFIETFBRE.SN',   # Singular      - ETF Brazil Equities
'CFIETFLAT.SN',   # Btg Pactual   - ETF Latam Equities
'CFIETFJPN.SN',   # Singular      - ETF Japan
'CFIAMDVASC.SN',  # Compass DVA   - Silicon Fund
'CFIADVAEFA.SN',  # Compass DVA   - E-fund
'CFIAMDVATA.SN',  # Compass DVA   - Medtech Fund
'CFIGC.SN',       # Singular      - ETF Global Corporates
'CFIETFHY.SN',    # Singular      - ETF High Yield
'CFIETFBRL.SN',   # Singular      - ETF Fixed Income BRL
'CFIIMDLAT.SN',   # Moneda        - Deuda Latinoamericana
'CFIETFBTC.SN',   # Singular      - ETF Bitcoin
'^RUT',
'^DJI',
'^N225',
'^HSI',
'CLP=X',
'DX-Y.NYB',
'EURUSD=X',
'EURCLP=X',
'HG=F',
'GC=F',
'CL=F',
'BZ=F',
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
