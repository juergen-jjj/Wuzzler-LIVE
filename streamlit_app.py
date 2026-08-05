import base64
import json

import pandas as pd
import requests
import streamlit as st


# ============================================================
# GITHUB-ZUGANG
# ============================================================

GITHUB_OWNER = "juergen-jjj"
GITHUB_REPO = "Wuzzler-LIVE"
GITHUB_BRANCH = "main"
GITHUB_FILE = "live_data/turnier_live.json"

# TOKEN HIER EINFÜGEN
# Beispiel:
# GITHUB_TOKEN = "github_pat_xxxxxxxxxxxxxxxxx"
GITHUB_TOKEN = "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"


# ============================================================
# STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Wuzzler LIVE",
    page_icon="⚽",
    layout="wide",
)


# ============================================================
# GITHUB-API
# ============================================================

@st.cache_data(ttl=3)
def load_live_data():

    api_url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/"
        f"{GITHUB_REPO}/"
        f"contents/"
        f"{GITHUB_FILE}"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(
        api_url,
        params={
            "ref": GITHUB_BRANCH
        },
        headers=headers,
        timeout=20,
    )

    # Bei Fehler wird die genaue GitHub-Antwort angezeigt
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub-API-Fehler: "
            f"HTTP {response.status_code}\n\n"
            f"{response.text}"
        )

    github_file = response.json()

    encoded_content = (
        github_file
        .get("content", "")
        .replace("\n", "")
        .replace("\r", "")
    )

    if not encoded_content:
        raise RuntimeError(
            "GitHub hat keinen Dateiinhalt geliefert."
        )

    decoded_content = (
        base64
        .b64decode(encoded_content)
        .decode("utf-8")
    )

    return json.loads(decoded_content)


# ============================================================
# DATEN LADEN
# ============================================================

st.title("⚽ WUZZLER LIVE")

try:

    data = load_live_data()

except Exception as error:

    st.error(
        "Die Live-Daten konnten nicht geladen werden."
    )

    st.code(
        str(error)
    )

    st.stop()


# ============================================================
# JSON AUSLESEN
# ============================================================

live = data.get(
    "live_view",
    {}
)

current_match = live.get(
    "current_match",
    {}
)

next_match = live.get(
    "next_match",
    {}
)

upcoming_matches = live.get(
    "upcoming_matches",
    []
)

standings = live.get(
    "standings",
    []
)

spritzer = live.get(
    "spritzer",
    []
)


# ============================================================
# TEST-STATUS
# ============================================================

st.success(
    "GitHub-API-Verbindung erfolgreich"
)

st.write(
    "Letzte Aktualisierung:",
    data.get(
        "updated_at",
        "unbekannt"
    )
)

st.write(
    "JSON-Format:",
    data.get(
        "format_version",
        "unbekannt"
    )
)


# ============================================================
# AKTUELLES SPIEL
# ============================================================

st.header(
    "🔴 JETZT AUF DEM TISCH"
)

if current_match:

    team1 = current_match.get(
        "team1",
        "?"
    )

    team2 = current_match.get(
        "team2",
        "?"
    )

    score1 = current_match.get(
        "score1",
        0
    )

    score2 = current_match.get(
        "score2",
        0
    )

    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:35px;
            border-radius:20px;
            background:#12324a;
            color:white;
        ">

            <div style="
                font-size:18px;
                color:#8fd3ff;
            ">
                {current_match.get("phase", "")}
            </div>

            <div style="
                font-size:50px;
                font-weight:bold;
                margin-top:15px;
            ">
                {team1}
            </div>

            <div style="
                font-size:25px;
                color:#ffd34e;
            ">
                GEGEN
            </div>

            <div style="
                font-size:50px;
                font-weight:bold;
            ">
                {team2}
            </div>

            <div style="
                font-size:60px;
                color:#7fffd4;
                font-weight:bold;
                margin-top:15px;
            ">
                {score1} : {score2}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.warning(
        "Kein aktuelles Spiel "
        "in live_view vorhanden."
    )


# ============================================================
# NÄCHSTES SPIEL
# ============================================================

st.header(
    "➡️ ALS NÄCHSTES"
)

if next_match:

    st.subheader(
        f'{next_match.get("team1", "?")} '
        f'gegen '
        f'{next_match.get("team2", "?")}'
    )

    st.caption(
        next_match.get(
            "phase",
            ""
        )
    )

else:

    st.info(
        "Kein nächstes Spiel vorhanden."
    )


# ============================================================
# KOMMENDE SPIELE
# ============================================================

st.header(
    "📅 KOMMENDE SPIELE"
)

if upcoming_matches:

    for match in upcoming_matches:

        st.write(
            f'**Spiel {match.get("order", "")}:** '
            f'{match.get("team1", "?")} '
            f'gegen '
            f'{match.get("team2", "?")}'
        )

else:

    st.info(
        "Keine kommenden Spiele vorhanden."
    )


# ============================================================
# TURNIERSTAND
# ============================================================

st.header(
    "🏆 TURNIERSTAND"
)

if standings:

    for group in standings:

        st.subheader(
            group.get(
                "group",
                "Tabelle"
            )
        )

        teams = group.get(
            "teams",
            []
        )

        if teams:

            table = pd.DataFrame(
                teams
            )

            table = table.rename(
                columns={
                    "rank": "Rang",
                    "team": "Team",
                    "points": "Punkte",
                    "goals": "Tore",
                    "against": "Gegentore",
                    "games": "Spiele",
                }
            )

            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True,
            )

else:

    st.info(
        "Kein Turnierstand vorhanden."
    )


# ============================================================
# SPRITZERWERTUNG
# ============================================================

st.header(
    "🍹 SPRITZERWERTUNG"
)

if spritzer:

    spritzer_table = pd.DataFrame(
        spritzer
    )

    spritzer_table = (
        spritzer_table.rename(
            columns={
                "rank": "Rang",
                "team": "Team",
                "score": "Spritzer",
            }
        )
    )

    st.dataframe(
        spritzer_table,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "Keine Spritzerdaten vorhanden."
    )


# ============================================================
# AKTUALISIEREN
# ============================================================

if st.button(
    "🔄 Daten neu laden"
):

    st.cache_data.clear()

    st.rerun()
