import base64
import html
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
# GITHUB TOKEN AUS STREAMLIT SECRETS
# ============================================================

try:
    GITHUB_TOKEN = str(
        st.secrets["GITHUB_TOKEN"]
    ).strip()

except Exception:
    st.error(
        "Der GitHub-Token wurde nicht in den "
        "Streamlit Secrets gefunden."
    )
    st.info(
        "Öffne in Streamlit Cloud: "
        "Settings → Secrets"
    )
    st.code(
        'GITHUB_TOKEN = "github_pat_DEIN_TOKEN"'
    )
    st.stop()


# ============================================================
# GITHUB-DATEN LADEN
# ============================================================

@st.cache_data(
    ttl=3,
    show_spinner=False,
)
def load_live_data():

    api_url = (
        "https://api.github.com/repos/"
        f"{GITHUB_OWNER}/"
        f"{GITHUB_REPO}/"
        f"contents/"
        f"{GITHUB_FILE}"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Cache-Control": "no-cache",
    }

    response = requests.get(
        api_url,
        params={
            "ref": GITHUB_BRANCH,
        },
        headers=headers,
        timeout=20,
    )

    if response.status_code != 200:
        raise RuntimeError(
            "GitHub-API-Fehler\n\n"
            f"HTTP-Status: {response.status_code}\n\n"
            f"GitHub-Antwort:\n{response.text}"
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

    try:
        decoded_content = (
            base64
            .b64decode(encoded_content)
            .decode("utf-8")
        )

        return json.loads(
            decoded_content
        )

    except Exception as error:
        raise RuntimeError(
            "Die GitHub-Datei konnte nicht "
            "als JSON gelesen werden.\n\n"
            f"{error}"
        )


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def safe_text(
    value,
    fallback="",
):

    if value is None:
        return fallback

    return html.escape(
        str(value)
    )


def safe_number(
    value,
    fallback=0,
):

    try:
        return int(value)

    except (
        TypeError,
        ValueError,
    ):
        return fallback


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
        "Die Live-Daten konnten nicht "
        "geladen werden."
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

left_column, middle_column, right_column = (
    st.columns(
        [
            2,
            3,
            1,
        ]
    )
)

with left_column:
    st.success(
        "🟢 LIVE AKTIV"
    )

with middle_column:
    st.caption(
        "Letzte Aktualisierung: "
        + str(
            data.get(
                "updated_at",
                "unbekannt",
            )
        )
    )

with right_column:

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
st.header("🔴 Aktuelles Spiel")

if current_match:
    team1 = safe_text(current_match.get("team1", "?"))
    team2 = safe_text(current_match.get("team2", "?"))
    phase = safe_text(current_match.get("phase", "Turnier"))

    # HTML ohne Einrückungen innerhalb des f-Strings
    html_current = f"""<div style="text-align: center; padding: 35px; border-radius: 20px; background: #12324a; color: white;">
    <div style="font-size: 20px; color: #8fd3ff; font-weight: bold; margin-bottom: 18px;">{phase}</div>
    <div style="font-size: 48px; font-weight: bold; overflow-wrap: anywhere;">{team1}</div>
    <div style="font-size: 24px; color: #ffd34e; margin: 12px 0;">⚽ GEGEN ⚽</div>
    <div style="font-size: 48px; font-weight: bold; overflow-wrap: anywhere;">{team2}</div>
</div>"""

    st.markdown(html_current, unsafe_allow_html=True)
else:
    st.warning("Aktuell ist kein Spiel gestartet.")


# ============================================================
# NÄCHSTES SPIEL
# ============================================================
st.header("➡️ ALS NÄCHSTES")

if next_match:
    next_team1 = safe_text(next_match.get("team1", "?"))
    next_team2 = safe_text(next_match.get("team2", "?"))
    next_phase = safe_text(next_match.get("phase", "Vorrunde"))

    # HTML ohne Einrückungen innerhalb des f-Strings
    html_next = f"""<div style="text-align: center; padding: 22px; border-radius: 15px; border: 2px solid #2c78a0;">
    <div style="font-size: 30px; font-weight: bold; overflow-wrap: anywhere;">
        {next_team1} <span style="color: #e6a800; margin: 0 12px;">gegen</span> {next_team2}
    </div>
    <div style="margin-top: 12px; color: #777; font-size: 17px;">{next_phase}</div>
</div>"""

    st.markdown(html_next, unsafe_allow_html=True)
else:
    st.info("Kein nächstes Spiel vorhanden.")
# ============================================================
# KOMMENDE SPIELE
# ============================================================

st.header(
    "📅 KOMMENDE SPIELE"
)

if upcoming_matches:

    for match in upcoming_matches:

        order = safe_text(
            match.get(
                "order",
                "",
            )
        )

        team1 = safe_text(
            match.get(
                "team1",
                "?",
            )
        )

        team2 = safe_text(
            match.get(
                "team2",
                "?",
            )
        )

        phase = safe_text(
            match.get(
                "phase",
                "",
            )
        )

        st.write(
            f"**Spiel {order}:** "
            f"{team1} gegen {team2}"
        )

        if phase:
            st.caption(
                phase
            )

else:
    st.info(
        "Keine kommenden Spiele vorhanden."
    )


# ============================================================
# TURNIERSTAND
# NUR: RANG, TEAM, PUNKTE
# ============================================================

st.header(
    "🏆 TURNIERSTAND"
)

if standings:

    for group in standings:

        group_name = safe_text(
            group.get(
                "group",
                "Tabelle",
            )
        )

        teams = group.get(
            "teams",
            [],
        )

        st.subheader(
            group_name
        )

        if teams:

            table_rows = []

            for team in teams:

                table_rows.append(
                    {
                        "Rang": safe_number(
                            team.get(
                                "rank",
                                0,
                            )
                        ),
                        "Team": str(
                            team.get(
                                "team",
                                "?",
                            )
                        ),
                        "Punkte": safe_number(
                            team.get(
                                "points",
                                0,
                            )
                        ),
                    }
                )

            table = pd.DataFrame(
                table_rows,
                columns=[
                    "Rang",
                    "Team",
                    "Punkte",
                ],
            )

            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info(
                "Für diese Gruppe sind "
                "noch keine Teams vorhanden."
            )

else:
    st.info(
        "Noch kein Turnierstand vorhanden."
    )


# ============================================================
# SPRITZERWERTUNG
# ============================================================

st.header(
    "🍹 SPRITZERWERTUNG"
)

if spritzer:

    spritzer_rows = []

    for entry in spritzer:

        spritzer_rows.append(
            {
                "Rang": safe_number(
                    entry.get(
                        "rank",
                        0,
                    )
                ),
                "Team": str(
                    entry.get(
                        "team",
                        "?",
                    )
                ),
                "Spritzer": safe_number(
                    entry.get(
                        "score",
                        0,
                    )
                ),
            }
        )

    spritzer_table = pd.DataFrame(
        spritzer_rows,
        columns=[
            "Rang",
            "Team",
            "Spritzer",
        ],
    )

    st.dataframe(
        spritzer_table,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "Noch keine Spritzerdaten vorhanden."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚽ Wuzzler LIVE"
)
