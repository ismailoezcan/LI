import datetime
import logging
import time
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import regex as re

import os, sys

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("data/images"):
    os.makedirs("data/images")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

while True:
    try:
        logging.info("Loading data and saving it to kickbase.csv")

        url = "https://www.ligainsider.de/stats/kickbase/marktwerte/gesamt/"
        r = requests.get(url)

        html_table = BeautifulSoup(r.text, features="lxml").find("table")
        r.close()

        df = pd.read_html(str(html_table))[0]
        regex = re.compile(r".*\/\d+\/")

        df["Link"] = [
            "https://www.ligainsider.de" + link.get("href")
            for link in html_table.find_all("a")
            if not regex.search(link.get("href")[-8:])
        ]

        # gesamt = pd.read_html(
        #     "https://www.ligainsider.de/stats/kickbase/marktwerte/gesamt/"
        # )[0]

        gesamt = df

        verlierer_t = pd.read_html(
            "https://www.ligainsider.de/stats/kickbase/marktwerte/tag/verlierer/"
        )[0].drop(columns=["Verein", "Position", "Rang", "Punkte Gesamt", "Marktwert"])
        verlierer_w = pd.read_html(
            "https://www.ligainsider.de/stats/kickbase/marktwerte/woche/verlierer/"
        )[0].drop(columns=["Verein", "Position", "Rang", "Punkte Gesamt", "Marktwert"])
        verlierer_m = pd.read_html(
            "https://www.ligainsider.de/stats/kickbase/marktwerte/monat/verlierer/"
        )[0].drop(columns=["Verein", "Position", "Rang", "Punkte Gesamt", "Marktwert"])

        gewinner_t = pd.read_html(
            "https://www.ligainsider.de/stats/kickbase/marktwerte/tag/gewinner/"
        )[0].drop(columns=["Verein", "Position", "Rang", "Punkte Gesamt", "Marktwert"])
        gewinner_w = pd.read_html(
            "https://www.ligainsider.de/stats/kickbase/marktwerte/woche/gewinner/"
        )[0].drop(columns=["Verein", "Position", "Rang", "Punkte Gesamt", "Marktwert"])
        gewinner_m = pd.read_html(
            "https://www.ligainsider.de/stats/kickbase/marktwerte/monat/gewinner/"
        )[0].drop(columns=["Verein", "Position", "Rang", "Punkte Gesamt", "Marktwert"])

        # add suffix _gewinner_t to Wachstum and Differenz columns
        verlierer_t.columns = verlierer_t.columns.map(lambda x: str(x) + "_verlierer_t")
        verlierer_w.columns = verlierer_w.columns.map(lambda x: str(x) + "_verlierer_w")
        verlierer_m.columns = verlierer_m.columns.map(lambda x: str(x) + "_verlierer_m")
        gewinner_t.columns = gewinner_t.columns.map(lambda x: str(x) + "_gewinner_t")
        gewinner_w.columns = gewinner_w.columns.map(lambda x: str(x) + "_gewinner_w")
        gewinner_m.columns = gewinner_m.columns.map(lambda x: str(x) + "_gewinner_m")

        gesamt = gesamt.merge(
            verlierer_t,
            left_on="Spieler",
            right_on="Spieler_verlierer_t",
            how="left",
            suffixes=("_gesamt", "_verlierer_t"),
        )
        gesamt = gesamt.merge(
            verlierer_w,
            left_on="Spieler",
            right_on="Spieler_verlierer_w",
            how="left",
            suffixes=("_gesamt", "_verlierer_w"),
        )
        gesamt = gesamt.merge(
            verlierer_m,
            left_on="Spieler",
            right_on="Spieler_verlierer_m",
            how="left",
            suffixes=("_gesamt", "_verlierer_m"),
        )
        gesamt = gesamt.merge(
            gewinner_t,
            left_on="Spieler",
            right_on="Spieler_gewinner_t",
            how="left",
            suffixes=("_gesamt", "_gewinner_t"),
        )
        gesamt = gesamt.merge(
            gewinner_w,
            left_on="Spieler",
            right_on="Spieler_gewinner_w",
            how="left",
            suffixes=("_gesamt", "_gewinner_w"),
        )
        gesamt = gesamt.merge(
            gewinner_m,
            left_on="Spieler",
            right_on="Spieler_gewinner_m",
            how="left",
            suffixes=("_gesamt", "_gewinner_m"),
        )

        gesamt = gesamt.drop(
            columns=["Rang"]
            + [col for col in gesamt.columns if col.startswith("Spieler_")]
        )

        # merge col wachstum_verlierer_t with wachstum_gewinner_t and rename to wachstum_t etc. and keep only column which is not NaN
        gesamt["Wachstum_t"] = gesamt["Wachstum_verlierer_t"].fillna(
            gesamt["Wachstum_gewinner_t"]
        )
        gesamt["Wachstum_w"] = gesamt["Wachstum_verlierer_w"].fillna(
            gesamt["Wachstum_gewinner_w"]
        )
        gesamt["Wachstum_m"] = gesamt["Wachstum_verlierer_m"].fillna(
            gesamt["Wachstum_gewinner_m"]
        )
        gesamt["Differenz_t"] = gesamt["Differenz_verlierer_t"].fillna(
            gesamt["Differenz_gewinner_t"]
        )
        gesamt["Differenz_w"] = gesamt["Differenz_verlierer_w"].fillna(
            gesamt["Differenz_gewinner_w"]
        )
        gesamt["Differenz_m"] = gesamt["Differenz_verlierer_m"].fillna(
            gesamt["Differenz_gewinner_m"]
        )

        gesamt = gesamt.drop(
            columns=[
                "Wachstum_verlierer_t",
                "Wachstum_verlierer_w",
                "Wachstum_verlierer_m",
                "Wachstum_gewinner_t",
                "Wachstum_gewinner_w",
                "Wachstum_gewinner_m",
                "Differenz_verlierer_t",
                "Differenz_verlierer_w",
                "Differenz_verlierer_m",
                "Differenz_gewinner_t",
                "Differenz_gewinner_w",
                "Differenz_gewinner_m",
            ]
        )

        # convert all cols to string
        # gesamt = gesamt.astype(str)

        gesamt["Spieler"] = gesamt["Spieler"].astype(str)
        gesamt["Verein"] = gesamt["Verein"].astype(str)
        gesamt["Position"] = gesamt["Position"].astype(str)
        gesamt["Gesamtpunkte"] = (
            gesamt["Gesamtpunkte"].astype(str).str.replace(".", "").astype(int)
        )

        gesamt["Einsätze"] = (
            gesamt["Einsätze"].fillna(0).astype(str).str.replace(".", "").astype(int)
            / 10
        )

        gesamt["Einsätze"] = gesamt["Einsätze"].astype(int)

        # calculate average points per game
        gesamt["Punkteschnitt"] = (gesamt["Gesamtpunkte"] / gesamt["Einsätze"]).astype(
            float
        )

        # replace % with nothing and convert to float and divide by 100 to get decimal for wachstum
        gesamt["Wachstum_t"] = (
            gesamt["Wachstum_t"]
            .str.replace("%", "")
            .str.replace(",", ".")
            .astype(float)
            / 100
        )
        gesamt["Wachstum_w"] = (
            gesamt["Wachstum_w"]
            .str.replace("%", "")
            .str.replace(",", ".")
            .astype(float)
            / 100
        )
        gesamt["Wachstum_m"] = (
            gesamt["Wachstum_m"]
            .str.replace("%", "")
            .str.replace(",", ".")
            .astype(float)
            / 100
        )

        gesamt["Differenz_t"] = (
            gesamt["Differenz_t"]
            .fillna(0)
            .astype(str)
            .str.replace(".", "")
            .str.replace("€", "")
            .astype(int)
        )
        gesamt["Differenz_t"] = gesamt["Differenz_t"].astype(int)

        gesamt["Differenz_w"] = (
            gesamt["Differenz_w"]
            .fillna(0)
            .astype(str)
            .str.replace(".", "")
            .str.replace("€", "")
            .astype(int)
        )
        gesamt["Differenz_w"] = gesamt["Differenz_w"].astype(int)

        gesamt["Differenz_m"] = (
            gesamt["Differenz_m"]
            .fillna(0)
            .astype(str)
            .str.replace(".", "")
            .str.replace("€", "")
            .astype(int)
        )
        gesamt["Differenz_m"] = gesamt["Differenz_m"].astype(int)

        gesamt.fillna(0)

        gesamt.to_json("data/kickbase.json", orient="records")

        # get images for players

        gesamt = pd.read_html(
            "https://www.ligainsider.de/stats/kickbase/marktwerte/gesamt/",
            extract_links="all",
        )[0]

        # drop all columns except for (Spieler, None)
        gesamt = gesamt.iloc[:, [1]]

        # loop through all players and create a dict with name as key and image as value
        players = {}
        for i in range(len(gesamt)):
            players[gesamt.iloc[i, 0][0]] = gesamt.iloc[i, 0][1]

        # loop through all players and http get http://www.ligainsider.de + image url
        i = 0
        for player_key, player_value in players.items():
            i += 1
            if os.path.exists(f"data/images/{player_key}.jpg"):
                logging.info(
                    f"Image for {player_key} already exists ({i}/{len(players)})"
                )
                continue
            logging.info(f"Getting image for {player_key} ({i}/{len(players)})")
            time.sleep(1)
            r = requests.get("https://www.ligainsider.de" + player_value)
            reg = "https:\/\/cdn.ligainsider\.de\/images\/player.*jpg"
            img_url = re.findall(reg, r.text)
            if len(img_url) > 0:
                # write image to file
                with open(f"data/images/{player_key}.jpg", "wb") as f:
                    f.write(requests.get(img_url[0]).content)
    except Exception as e:
        logging.error(e)

    # wait for next hour to start again, calculate time to wait
    now = datetime.datetime.now()
    if now.hour + 1 == 24:
        next_hour = now.replace(hour=0, minute=5, second=0, microsecond=0)
    else:
        next_hour = now.replace(hour=now.hour + 1, minute=5, second=0, microsecond=0)
    time_to_wait = (next_hour - now).seconds

    # use tqdm to show the progress bar and counter
    for i in tqdm(range(time_to_wait), desc="Waiting", unit="s"):
        time.sleep(1)

    logging.info("Done waiting!")
