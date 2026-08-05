import base64
import json

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ============================================================
# STREAMLIT EINSTELLUNGEN
# ============================================================

st.set_page_config(
    page_title="Wuzzler LIVE",
    page_icon="⚽",
    layout="wide",
)

# Automatische Aktualisierung alle 10 Sekunden
st_autorefresh(interval=10_000, key="live_refresh")

# ============================================================
# GITHUB EINSTELLUNGEN
# ============================================================

GITHUB_OWNER = "juergen-jjj"
GITHUB_REPO = "Wuzzler-LIVE"
GITHUB_BRANCH = "main"
GITHUB_FILE = "live_data/turnier_live.json"


# ============================================================
# GITHUB TOKEN AUS STREAMLIT SECRETS LADEN
# ============================================================

try:

    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

except Exception:

    st.error(
        "Der GitHub-Token wurde nicht gefunden."
    )

    st.info(
        "Lege in Streamlit unter "
        "Settings → Secrets den Eintrag "
        "GITHUB_TOKEN an."
    )

    st.stop()


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
        "Authorization": (
            f"Bearer {GITHUB_TOKEN}"
        ),
        "X-GitHub-Api-Version": (
            "2022-11-28"
        ),
    }

    response = requests.get(
        api_url,
        params={
            "ref": GITHUB_BRANCH
        },
        headers=headers,
        timeout=20,
    )

    if response.status_code != 200:

        raise RuntimeError(
            "GitHub-API-Fehler\n\n"
            f"HTTP-Status: "
            f"{response.status_code}\n\n"
            f"Antwort:\n"
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
            "GitHub hat keinen "
            "Dateiinhalt geliefert."
        )

    try:

        decoded_content = (
            base64
            .b64decode(
                encoded_content
            )
            .decode(
                "utf-8"
            )
        )

    except Exception as error:

        raise RuntimeError(
            "Der GitHub-Dateiinhalt "
            "konnte nicht entschlüsselt "
            "werden.\n\n"
            f"{error}"
        )

    try:

        return json.loads(
            decoded_content
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Die Datei enthält "
            "ungültiges JSON.\n\n"
            f"{error}"
        )


# ============================================================
# HILFSFUNKTION
# ============================================================

def safe_dataframe(
    rows,
    columns,
):

    dataframe = pd.DataFrame(
        rows
    )

    for column in columns:

        if column not in dataframe.columns:

            dataframe[
                column
            ] = ""

    return dataframe[
        columns
    ]


# ============================================================
# TITEL
# ============================================================

st.title(
    "⚽ WUZZLER LIVE"
)


# ============================================================
# DATEN LADEN
# ============================================================

try:

    data = load_live_data()

except Exception as error:

    st.error(
        "Die Live-Daten konnten "
        "nicht geladen werden."
    )

    st.code(
        str(error)
    )

    if st.button(
        "🔄 Erneut versuchen"
    ):

        st.cache_data.clear()

        st.rerun()

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
# STATUSZEILE
# ============================================================

status_column, update_column, button_column = (
    st.columns(
        [
            2,
            3,
            1,
        ]
    )
)

with status_column:

    st.success(
        "🟢 LIVE-VERBINDUNG AKTIV"
    )

with update_column:

    st.write(
        "Letzte Aktualisierung:"
    )

    st.caption(
        data.get(
            "updated_at",
            "unbekannt"
        )
    )

with button_column:

    if st.button(
        "🔄 Neu laden",
        use_container_width=True,
    ):

        st.cache_data.clear()

        st.rerun()


st.divider()


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

    phase = current_match.get(
        "phase",
        ""
    )

    st.markdown(
        f"""
        <div
            style="
                text-align: center;
                padding: 35px;
                border-radius: 20px;
                background:
                    linear-gradient(
                        135deg,
                        #12324a,
                        #1f587c
                    );
                color: white;
                box-shadow:
                    0 5px 20px
                    rgba(
                        0,
                        0,
                        0,
                        0.25
                    );
            "
        >

            <div
                style="
                    font-size: 20px;
                    color: #8fd3ff;
                    font-weight: bold;
                "
            >
                {phase}
            </div>

            <div
                style="
                    font-size: 48px;
                    font-weight: bold;
                    margin-top: 20px;
                    word-break:
                        break-word;
                "
            >
                {team1}
            </div>

            <div
                style="
                    font-size: 24px;
                    color: #ffd34e;
                    margin:
                        10px 0;
                "
            >
                ⚽ GEGEN ⚽
            </div>

            <div
                style="
                    font-size: 48px;
                    font-weight: bold;
                    word-break:
                        break-word;
                "
            >
                {team2}
            </div>

            <div
                style="
                    font-size: 70px;
                    color: #7fffd4;
                    font-weight: bold;
                    margin-top: 20px;
                "
            >
                {score1} : {score2}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.warning(
        "Aktuell ist kein Spiel "
        "gestartet."
    )


# ============================================================
# NÄCHSTES SPIEL
# ============================================================

st.header(
    "➡️ ALS NÄCHSTES"
)


if next_match:

    next_team1 = (
        next_match.get(
            "team1",
            "?"
        )
    )

    next_team2 = (
        next_match.get(
            "team2",
            "?"
        )
    )

    next_phase = (
        next_match.get(
            "phase",
            ""
        )
    )

    st.markdown(
        f"""
        <div
            style="
                text-align: center;
                padding: 20px;
                border-radius: 15px;
                border:
                    2px solid
                    #2c78a0;
            "
        >

            <div
                style="
                    font-size: 28px;
                    font-weight: bold;
                "
            >
                {next_team1}
                <span
                    style="
                        color: #e6a800;
                    "
                >
                    gegen
                </span>
                {next_team2}
            </div>

            <div
                style="
                    margin-top: 10px;
                    color: #777;
                "
            >
                {next_phase}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.info(
        "Kein nächstes Spiel "
        "vorhanden."
    )


# ============================================================
# KOMMENDE SPIELE
# ============================================================

st.header(
    "📅 KOMMENDE SPIELE"
)


if upcoming_matches:

    for match in upcoming_matches:

        order = match.get(
            "order",
            ""
        )

        team1 = match.get(
            "team1",
            "?"
        )

        team2 = match.get(
            "team2",
            "?"
        )

        phase = match.get(
            "phase",
            ""
        )

        st.write(
            f"**Spiel {order}:** "
            f"{team1} "
            f"gegen "
            f"{team2}"
        )

        if phase:

            st.caption(
                phase
            )

else:

    st.info(
        "Keine weiteren Spiele "
        "vorhanden."
    )


# ============================================================
# TURNIERSTAND
# ============================================================

st.header(
    "🏆 TURNIERSTAND"
)


if standings:

    for group in standings:

        group_name = group.get(
            "group",
            "Tabelle"
        )

        teams = group.get(
            "teams",
            []
        )

        st.subheader(
            group_name
        )

        if teams:

            table = safe_dataframe(
                teams,
                [
                    "rank",
                    "team",
                    "points",
                    "goals",
                    "against",
                    "games",
                ],
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
                "Für diese Gruppe "
                "sind noch keine "
                "Teams vorhanden."
            )

else:

    st.info(
        "Noch kein Turnierstand "
        "vorhanden."
    )


# ============================================================
# SPRITZERWERTUNG
# ============================================================

st.header(
    "🍹 SPRITZERWERTUNG"
)


if spritzer:

    spritzer_table = (
        safe_dataframe(
            spritzer,
            [
                "rank",
                "team",
                "score",
            ],
        )
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
        "Noch keine "
        "Spritzerdaten vorhanden."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚽ Wuzzler LIVE"
)
