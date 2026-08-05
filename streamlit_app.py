import json
import os
import re
import time
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


# ============================================================
# KONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Wuzzler LIVE",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# GitHub-Datenquelle
GITHUB_OWNER = "juergen-jjj"
GITHUB_REPO = "Wuzzler-LIVE"
GITHUB_BRANCH = "main"
LIVE_DATA_PATH = "live_data/turnier_live.json"

RAW_JSON_URL = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/"
    f"{GITHUB_BRANCH}/{LIVE_DATA_PATH}"
)

AUTO_REFRESH_SECONDS = 10


# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, #173f5f 0%, transparent 38%),
                linear-gradient(145deg, #07111f 0%, #0c1b2b 48%, #07111f 100%);
            color: #f7fbff;
        }

        .block-container {
            max-width: 1450px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: #ffffff !important;
        }

        .live-header {
            text-align: center;
            padding: 1.2rem 1rem 0.7rem 1rem;
            margin-bottom: 1rem;
        }

        .live-title {
            font-size: clamp(2rem, 6vw, 4.8rem);
            font-weight: 900;
            letter-spacing: 0.08em;
            color: #ffffff;
            margin: 0;
            line-height: 1;
        }

        .live-subtitle {
            color: #8fd3ff;
            font-size: 1.05rem;
            margin-top: 0.6rem;
        }

        .status-bar {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin: 1rem 0 1.5rem 0;
        }

        .status-chip {
            background: rgba(255,255,255,0.09);
            border: 1px solid rgba(255,255,255,0.16);
            color: #eaf6ff;
            border-radius: 999px;
            padding: 0.45rem 0.9rem;
            font-size: 0.9rem;
        }

        .section-title {
            color: #8fd3ff;
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin: 1.2rem 0 0.65rem 0;
        }

        .match-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(25, 67, 97, 0.97),
                    rgba(10, 28, 46, 0.98)
                );
            border: 2px solid rgba(91, 192, 235, 0.55);
            border-radius: 24px;
            padding: 1.5rem;
            box-shadow: 0 18px 50px rgba(0,0,0,0.35);
            text-align: center;
            margin-bottom: 1rem;
        }

        .match-phase {
            color: #8fd3ff;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.13em;
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }

        .team-name {
            font-size: clamp(1.7rem, 4vw, 3.7rem);
            font-weight: 900;
            color: #ffffff;
            overflow-wrap: anywhere;
            line-height: 1.08;
        }

        .versus {
            font-size: clamp(1.4rem, 3vw, 2.5rem);
            color: #ffcf4d;
            font-weight: 900;
            padding: 0.3rem 0;
        }

        .score {
            color: #7fffd4;
            font-size: clamp(2.4rem, 7vw, 5.5rem);
            font-weight: 900;
            line-height: 1;
            margin: 0.7rem 0;
        }

        .next-card {
            background: rgba(255,255,255,0.075);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 18px;
            padding: 1.15rem;
            text-align: center;
            min-height: 150px;
        }

        .next-label {
            color: #ffcf4d;
            font-size: 0.82rem;
            font-weight: 900;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }

        .next-teams {
            color: white;
            font-size: clamp(1.15rem, 2.4vw, 2rem);
            font-weight: 800;
            margin-top: 1rem;
            overflow-wrap: anywhere;
        }

        .next-vs {
            color: #8fd3ff;
            padding: 0 0.4rem;
        }

        .upcoming-row {
            background: rgba(255,255,255,0.065);
            border-left: 4px solid #5bc0eb;
            border-radius: 10px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.55rem;
            color: white;
            font-size: 1.05rem;
        }

        .rank-card {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.13);
            border-radius: 15px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.55rem;
        }

        .rank-number {
            color: #ffcf4d;
            font-weight: 900;
            font-size: 1.2rem;
        }

        .rank-name {
            color: white;
            font-weight: 800;
            font-size: 1.15rem;
        }

        .rank-score {
            color: #7fffd4;
            font-size: 1.25rem;
            font-weight: 900;
            text-align: right;
        }

        .empty-card {
            background: rgba(255,255,255,0.06);
            border: 1px dashed rgba(255,255,255,0.22);
            border-radius: 16px;
            padding: 1.3rem;
            color: #b9c8d4;
            text-align: center;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
        }

        .footer {
            text-align: center;
            color: #8396a6;
            margin-top: 2rem;
            font-size: 0.82rem;
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left: 0.7rem;
                padding-right: 0.7rem;
            }

            .match-card {
                padding: 1rem 0.65rem;
                border-radius: 17px;
            }

            .team-name {
                font-size: 1.65rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def clean_text(value):
    """Wandelt Werte sicher in lesbaren Text um."""
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in {"none", "nan", "null"}:
        return ""

    return text


def normalize_key(value):
    """Vereinheitlicht Tabellenüberschriften."""
    text = clean_text(value).lower()
    text = text.replace("ä", "ae")
    text = text.replace("ö", "oe")
    text = text.replace("ü", "ue")
    text = text.replace("ß", "ss")
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text


def safe_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def is_empty_row(row):
    return not any(clean_text(cell) for cell in row)


def html_escape(text):
    text = clean_text(text)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ============================================================
# LIVE-DATEN LADEN
# ============================================================

@st.cache_data(ttl=5, show_spinner=False)
def load_live_data(url):
    response = requests.get(
        url,
        timeout=15,
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    response.raise_for_status()
    return response.json()


def clear_and_reload():
    st.cache_data.clear()
    st.rerun()


try:
    live_data = load_live_data(RAW_JSON_URL)
except Exception as exc:
    st.error("Die Live-Daten konnten momentan nicht geladen werden.")
    st.code(str(exc))
    st.info(
        "Prüfe bitte, ob die Datei "
        "`live_data/turnier_live.json` im GitHub-Repository vorhanden ist."
    )

    if st.button("Erneut laden"):
        clear_and_reload()

    st.stop()


sheets = live_data.get("sheets", {}) or {}
updated_at = clean_text(live_data.get("updated_at"))
format_version = clean_text(live_data.get("format_version", "1"))


# ============================================================
# TABELLEN AUS JSON LESEN
# ============================================================

def rows_to_dataframe(rows):
    """
    Wandelt die aus Excel exportierten JSON-Zeilen in ein DataFrame um.
    Die erste nicht leere Zeile wird als Überschrift verwendet.
    """
    if not isinstance(rows, list):
        return pd.DataFrame()

    cleaned_rows = []

    for row in rows:
        if not isinstance(row, list):
            continue

        values = [clean_text(value) for value in row]

        if not is_empty_row(values):
            cleaned_rows.append(values)

    if not cleaned_rows:
        return pd.DataFrame()

    header_index = 0

    for index, row in enumerate(cleaned_rows):
        if len([value for value in row if value]) >= 2:
            header_index = index
            break

    header = cleaned_rows[header_index]

    while header and not clean_text(header[-1]):
        header.pop()

    if not header:
        return pd.DataFrame()

    unique_headers = []
    used = {}

    for index, value in enumerate(header):
        name = clean_text(value) or f"Spalte {index + 1}"

        if name in used:
            used[name] += 1
            name = f"{name} {used[name]}"
        else:
            used[name] = 1

        unique_headers.append(name)

    data_rows = []

    for row in cleaned_rows[header_index + 1:]:
        values = row[:len(unique_headers)]

        while len(values) < len(unique_headers):
            values.append("")

        if is_empty_row(values):
            continue

        data_rows.append(values)

    return pd.DataFrame(data_rows, columns=unique_headers)


dataframes = {
    sheet_name: rows_to_dataframe(rows)
    for sheet_name, rows in sheets.items()
}


def find_sheet(*keywords):
    """
    Sucht ein Tabellenblatt anhand von Begriffen im Blattnamen.
    """
    normalized_keywords = [
        normalize_key(keyword)
        for keyword in keywords
    ]

    for sheet_name, dataframe in dataframes.items():
        normalized_name = normalize_key(sheet_name)

        if all(keyword in normalized_name for keyword in normalized_keywords):
            return sheet_name, dataframe.copy()

    return None, pd.DataFrame()


def find_column(dataframe, *candidates):
    """
    Sucht eine Spalte über mögliche deutsche Bezeichnungen.
    """
    if dataframe.empty:
        return None

    normalized_columns = {
        normalize_key(column): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        key = normalize_key(candidate)

        if key in normalized_columns:
            return normalized_columns[key]

    for candidate in candidates:
        key = normalize_key(candidate)

        for normalized, original in normalized_columns.items():
            if key in normalized or normalized in key:
                return original

    return None


# ============================================================
# TURNIERÜBERSICHT AUSLESEN
# ============================================================

overview_name, overview_df = find_sheet(
    "Turnier",
    "Übersicht",
)

overview = {}

if not overview_df.empty and len(overview_df.columns) >= 2:
    first_column = overview_df.columns[0]
    second_column = overview_df.columns[1]

    for _, row in overview_df.iterrows():
        key = normalize_key(row[first_column])
        value = clean_text(row[second_column])

        if key:
            overview[key] = value


def overview_value(*names, default=""):
    for name in names:
        key = normalize_key(name)

        if key in overview:
            return overview[key]

    return default


phase = overview_value(
    "Phase",
    default="Turnier"
)

tournament_started = overview_value(
    "Turnier gestartet",
    default=""
)

team_count = overview_value(
    "Teams",
    default=""
)

spritzer_locked = overview_value(
    "Spritzerwertung gesperrt",
    default=""
)

spritzer_timer = overview_value(
    "Spritzer-Endtimer aktiv",
    default=""
)


# ============================================================
# SPIELE UND ERGEBNISSE ERKENNEN
# ============================================================

matches_name, matches_df = find_sheet(
    "Spiele"
)

if matches_df.empty:
    matches_name, matches_df = find_sheet(
        "Begegnungen"
    )


def detect_match_columns(dataframe):
    return {
        "status": find_column(
            dataframe,
            "Status",
            "Spielstatus",
        ),
        "phase": find_column(
            dataframe,
            "Phase",
            "Runde",
            "Gruppe",
            "Bereich",
        ),
        "team1": find_column(
            dataframe,
            "Team 1",
            "Team1",
            "Heimteam",
        ),
        "score": find_column(
            dataframe,
            "Ergebnis",
            "Spielstand",
            "Tore",
            "Score",
        ),
        "team2": find_column(
            dataframe,
            "Team 2",
            "Team2",
            "Gastteam",
        ),
        "winner": find_column(
            dataframe,
            "Sieger",
            "Gewinner",
        ),
    }


match_columns = detect_match_columns(matches_df)


def row_to_match(row):
    if matches_df.empty:
        return None

    team1_column = match_columns["team1"]
    team2_column = match_columns["team2"]

    if not team1_column or not team2_column:
        return None

    team1 = clean_text(row.get(team1_column, ""))
    team2 = clean_text(row.get(team2_column, ""))

    if not team1 or not team2:
        return None

    status = clean_text(
        row.get(match_columns["status"], "")
    ) if match_columns["status"] else ""

    phase_text = clean_text(
        row.get(match_columns["phase"], "")
    ) if match_columns["phase"] else ""

    score = clean_text(
        row.get(match_columns["score"], "")
    ) if match_columns["score"] else ""

    winner = clean_text(
        row.get(match_columns["winner"], "")
    ) if match_columns["winner"] else ""

    return {
        "team1": team1,
        "team2": team2,
        "status": status,
        "phase": phase_text,
        "score": score,
        "winner": winner,
    }


all_matches = []

if not matches_df.empty:
    for _, match_row in matches_df.iterrows():
        match = row_to_match(match_row)

        if match:
            all_matches.append(match)


def status_is_finished(status):
    status = normalize_key(status)

    return any(
        word in status
        for word in (
            "beendet",
            "fertig",
            "gespielt",
            "abgeschlossen",
        )
    )


def status_is_current(status):
    status = normalize_key(status)

    return any(
        word in status
        for word in (
            "aktuell",
            "laeuft",
            "laufend",
            "jetzt",
        )
    )


def status_is_open(status):
    status = normalize_key(status)

    return any(
        word in status
        for word in (
            "offen",
            "ausstehend",
            "geplant",
            "naechst",
        )
    )


finished_matches = [
    match
    for match in all_matches
    if status_is_finished(match["status"])
]

current_match = next(
    (
        match
        for match in all_matches
        if status_is_current(match["status"])
    ),
    None
)

open_matches = [
    match
    for match in all_matches
    if not status_is_finished(match["status"])
    and not status_is_current(match["status"])
]

if current_match is None and open_matches:
    current_match = open_matches[0]
    open_matches = open_matches[1:]


next_match = (
    open_matches[0]
    if open_matches
    else None
)

upcoming_matches = (
    open_matches[1:6]
    if len(open_matches) > 1
    else []
)


# ============================================================
# FALLBACK: AKTUELLES SPIEL AUS TURNIERPHASE
# ============================================================

phase_key = normalize_key(phase)

if current_match is None:
    if "group" in phase_key:
        current_match = {
            "team1": "Aktuelle Begegnung",
            "team2": "wird geladen",
            "status": "Laufend",
            "phase": "Gruppenphase",
            "score": "",
            "winner": "",
        }

    elif "koplay" in phase_key:
        current_match = {
            "team1": "K.O.-Spiel",
            "team2": "wird geladen",
            "status": "Laufend",
            "phase": "K.O.-Phase",
            "score": "",
            "winner": "",
        }

    elif "finalplay" in phase_key:
        current_match = {
            "team1": "Finale",
            "team2": "wird geladen",
            "status": "Laufend",
            "phase": "Finalrunde",
            "score": "",
            "winner": "",
        }


# ============================================================
# SPRITZERWERTUNG ERKENNEN
# ============================================================

spritzer_name, spritzer_df = find_sheet(
    "Spritzer"
)

if spritzer_df.empty:
    for sheet_name, dataframe in dataframes.items():
        if "spritzer" in normalize_key(sheet_name):
            spritzer_name = sheet_name
            spritzer_df = dataframe.copy()
            break


def prepare_spritzer_dataframe(dataframe):
    if dataframe.empty:
        return pd.DataFrame(
            columns=[
                "Platz",
                "Team",
                "Spritzer",
            ]
        )

    name_column = find_column(
        dataframe,
        "Team",
        "Teilnehmer",
        "Name",
        "Spieler",
    )

    score_column = find_column(
        dataframe,
        "Spritzer",
        "Punkte",
        "Anzahl",
        "Gesamt",
        "Score",
    )

    if not name_column or not score_column:
        return pd.DataFrame(
            columns=[
                "Platz",
                "Team",
                "Spritzer",
            ]
        )

    result = dataframe[
        [
            name_column,
            score_column,
        ]
    ].copy()

    result.columns = [
        "Team",
        "Spritzer",
    ]

    result["Team"] = (
        result["Team"]
        .astype(str)
        .str.strip()
    )

    result["Spritzer"] = (
        pd.to_numeric(
            result["Spritzer"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )

    result = result[
        result["Team"] != ""
    ]

    result = (
        result
        .sort_values(
            "Spritzer",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    result.insert(
        0,
        "Platz",
        range(
            1,
            len(result) + 1,
        ),
    )

    return result


spritzer_ranking = prepare_spritzer_dataframe(
    spritzer_df
)


# ============================================================
# GRUPPENTABELLEN ERKENNEN
# ============================================================

def is_group_table(
    sheet_name,
    dataframe,
):
    normalized_name = normalize_key(
        sheet_name
    )

    if "gruppe" in normalized_name:
        return True

    required = {
        "team",
        "punkte",
    }

    available = {
        normalize_key(column)
        for column in dataframe.columns
    }

    return required.issubset(
        available
    )


group_tables = []

for sheet_name, dataframe in dataframes.items():
    if dataframe.empty:
        continue

    if sheet_name in {
        overview_name,
        matches_name,
        spritzer_name,
    }:
        continue

    if is_group_table(
        sheet_name,
        dataframe,
    ):
        group_tables.append(
            (
                sheet_name,
                dataframe.copy(),
            )
        )


# ============================================================
# KOPFBEREICH
# ============================================================

st.markdown(
    """
    <div class="live-header">
        <div class="live-title">
            ⚽ WUZZLER LIVE
        </div>
        <div class="live-subtitle">
            Aktuelle Spiele, Turnierstand und Spritzerwertung
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


status_items = []

if phase:
    status_items.append(
        f"Phase: {html_escape(phase)}"
    )

if team_count:
    status_items.append(
        f"Teams: {html_escape(team_count)}"
    )

if tournament_started:
    status_items.append(
        "Turnier: "
        + html_escape(
            tournament_started
        )
    )

if spritzer_locked:
    status_items.append(
        "Spritzerwertung: "
        + (
            "beendet"
            if normalize_key(
                spritzer_locked
            ) == "ja"
            else "aktiv"
        )
    )

if spritzer_timer:
    if normalize_key(
        spritzer_timer
    ) == "ja":
        status_items.append(
            "Spritzer-Endtimer läuft"
        )

if status_items:
    chips = "".join(
        (
            '<span class="status-chip">'
            + item
            + "</span>"
        )
        for item in status_items
    )

    st.markdown(
        (
            '<div class="status-bar">'
            + chips
            + "</div>"
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# NAVIGATION
# ============================================================

tab_live, tab_table, tab_results, tab_spritzer = st.tabs(
    [
        "🔴 LIVE",
        "🏆 TURNIERSTAND",
        "📋 ERGEBNISSE",
        "🍹 SPRITZERWERTUNG",
    ]
)


# ============================================================
# TAB: LIVE
# ============================================================

with tab_live:

    st.markdown(
        '<div class="section-title">'
        "Jetzt auf dem Tisch"
        "</div>",
        unsafe_allow_html=True,
    )

    if current_match:
        current_phase = (
            current_match["phase"]
            or phase
            or "Aktuelles Spiel"
        )

        score_html = ""

        if current_match["score"]:
            score_html = (
                '<div class="score">'
                + html_escape(
                    current_match[
                        "score"
                    ]
                )
                + "</div>"
            )

        st.markdown(
            f"""
            <div class="match-card">
                <div class="match-phase">
                    {html_escape(current_phase)}
                </div>

                <div class="team-name">
                    {html_escape(
                        current_match[
                            "team1"
                        ]
                    )}
                </div>

                <div class="versus">
                    GEGEN
                </div>

                <div class="team-name">
                    {html_escape(
                        current_match[
                            "team2"
                        ]
                    )}
                </div>

                {score_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            """
            <div class="empty-card">
                Aktuell ist noch keine
                Begegnung eingetragen.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-title">'
        "Als Nächstes"
        "</div>",
        unsafe_allow_html=True,
    )

    if next_match:
        left, right = st.columns(
            [
                1,
                1,
            ]
        )

        with left:
            st.markdown(
                f"""
                <div class="next-card">
                    <div class="next-label">
                        Nächste Begegnung
                    </div>

                    <div class="next-teams">
                        {html_escape(
                            next_match[
                                "team1"
                            ]
                        )}
                        <span class="next-vs">
                            gegen
                        </span>
                        {html_escape(
                            next_match[
                                "team2"
                            ]
                        )}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            if upcoming_matches:
                following = upcoming_matches[0]

                st.markdown(
                    f"""
                    <div class="next-card">
                        <div class="next-label">
                            Danach
                        </div>

                        <div class="next-teams">
                            {html_escape(
                                following[
                                    "team1"
                                ]
                            )}
                            <span class="next-vs">
                                gegen
                            </span>
                            {html_escape(
                                following[
                                    "team2"
                                ]
                            )}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:
                st.markdown(
                    """
                    <div class="next-card">
                        <div class="next-label">
                            Vorschau
                        </div>

                        <div class="next-teams">
                            Noch keine weitere
                            Begegnung geplant
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.markdown(
            """
            <div class="empty-card">
                Keine weitere Begegnung
                verfügbar.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-title">'
        "Weitere kommende Spiele"
        "</div>",
        unsafe_allow_html=True,
    )

    if upcoming_matches:

        for index, match in enumerate(
            upcoming_matches[
                1:
            ],
            start=1,
        ):

            phase_label = (
                match["phase"]
                or "Kommendes Spiel"
            )

            st.markdown(
                f"""
                <div class="upcoming-row">
                    <strong>
                        {index + 1}.
                    </strong>

                    &nbsp;

                    {html_escape(
                        match[
                            "team1"
                        ]
                    )}

                    <strong>
                        gegen
                    </strong>

                    {html_escape(
                        match[
                            "team2"
                        ]
                    )}

                    <span style="
                        float:right;
                        color:#8fd3ff;
                    ">
                        {html_escape(
                            phase_label
                        )}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.caption(
            "Derzeit sind keine weiteren "
            "kommenden Spiele vorhanden."
        )


# ============================================================
# TAB: TURNIERSTAND
# ============================================================

with tab_table:

    if group_tables:

        for sheet_name, dataframe in group_tables:

            st.markdown(
                '<div class="section-title">'
                + html_escape(
                    sheet_name
                )
                + "</div>",
                unsafe_allow_html=True,
            )

            display_df = dataframe.copy()

            for column in display_df.columns:
                numeric = pd.to_numeric(
                    display_df[
                        column
                    ],
                    errors="coerce",
                )

                if (
                    numeric.notna()
                    .sum()
                    >= max(
                        1,
                        len(
                            display_df
                        )
                        // 2,
                    )
                ):
                    display_df[
                        column
                    ] = numeric.fillna(
                        0
                    ).astype(
                        int
                    )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )

    else:

        possible_tables = [
            (
                sheet_name,
                dataframe,
            )
            for sheet_name, dataframe
            in dataframes.items()
            if (
                not dataframe.empty
                and sheet_name
                not in {
                    overview_name,
                    matches_name,
                    spritzer_name,
                }
            )
        ]

        if possible_tables:

            for sheet_name, dataframe in possible_tables:

                st.markdown(
                    '<div class="section-title">'
                    + html_escape(
                        sheet_name
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

                st.dataframe(
                    dataframe,
                    use_container_width=True,
                    hide_index=True,
                )

        else:

            st.markdown(
                """
                <div class="empty-card">
                    Der Turnierstand ist
                    noch nicht verfügbar.
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# TAB: ERGEBNISSE
# ============================================================

with tab_results:

    if finished_matches:

        result_rows = []

        for match in finished_matches:

            result_rows.append(
                {
                    "Phase":
                        match[
                            "phase"
                        ],
                    "Team 1":
                        match[
                            "team1"
                        ],
                    "Ergebnis":
                        match[
                            "score"
                        ],
                    "Team 2":
                        match[
                            "team2"
                        ],
                    "Sieger":
                        match[
                            "winner"
                        ],
                }
            )

        results_df = pd.DataFrame(
            result_rows
        )

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

    elif not matches_df.empty:

        st.dataframe(
            matches_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.markdown(
            """
            <div class="empty-card">
                Es wurden noch keine
                Ergebnisse eingetragen.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TAB: SPRITZERWERTUNG
# ============================================================

with tab_spritzer:

    st.markdown(
        '<div class="section-title">'
        "Aktuelle Rangliste"
        "</div>",
        unsafe_allow_html=True,
    )

    if not spritzer_ranking.empty:

        total_spritzer = int(
            spritzer_ranking[
                "Spritzer"
            ].sum()
        )

        top_three = (
            spritzer_ranking
            .head(3)
        )

        medal_columns = st.columns(
            max(
                1,
                len(
                    top_three
                ),
            )
        )

        medals = [
            "🥇",
            "🥈",
            "🥉",
        ]

        for index, (
            _,
            row,
        ) in enumerate(
            top_three.iterrows()
        ):

            with medal_columns[
                index
            ]:

                st.metric(
                    label=(
                        medals[
                            index
                        ]
                        + " "
                        + str(
                            row[
                                "Team"
                            ]
                        )
                    ),
                    value=(
                        str(
                            row[
                                "Spritzer"
                            ]
                        )
                        + " Spritzer"
                    ),
                )

        st.markdown(
            '<div class="section-title">'
            "Gesamte Spritzerwertung"
            "</div>",
            unsafe_allow_html=True,
        )

        for _, row in (
            spritzer_ranking
            .iterrows()
        ):

            st.markdown(
                f"""
                <div class="rank-card">
                    <div style="
                        display:grid;
                        grid-template-columns:
                        60px 1fr 120px;
                        align-items:center;
                        gap:10px;
                    ">
                        <div class="rank-number">
                            #{int(
                                row[
                                    "Platz"
                                ]
                            )}
                        </div>

                        <div class="rank-name">
                            {html_escape(
                                row[
                                    "Team"
                                ]
                            )}
                        </div>

                        <div class="rank-score">
                            {int(
                                row[
                                    "Spritzer"
                                ]
                            )}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(
            f"Gesamt gezählte Spritzer: "
            f"{total_spritzer}"
        )

    else:

        st.markdown(
            """
            <div class="empty-card">
                Die Spritzerwertung
                wurde noch nicht gestartet
                oder enthält noch keine Daten.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FOOTER UND AKTUALISIERUNG
# ============================================================

if updated_at:

    try:

        display_time = datetime.fromisoformat(
            updated_at
        ).strftime(
            "%d.%m.%Y – %H:%M:%S"
        )

    except ValueError:

        display_time = updated_at

else:

    display_time = "unbekannt"


st.markdown(
    f"""
    <div class="footer">
        Letzte Datenaktualisierung:
        {html_escape(display_time)}
        &nbsp;•&nbsp;
        Datenformat:
        {html_escape(format_version)}
    </div>
    """,
    unsafe_allow_html=True,
)


left, middle, right = st.columns(
    [
        1,
        1,
        1,
    ]
)

with middle:

    if st.button(
        "🔄 Live-Daten neu laden",
        use_container_width=True,
    ):

        clear_and_reload()


# Automatische Aktualisierung der Webseite.
time.sleep(
    AUTO_REFRESH_SECONDS
)

clear_and_reload()
