import base64
import json
import urllib.request
import urllib.error

import pandas as pd
import streamlit as st

# ============================================================
# WUZZLER LIVE – Streamlit-Zuschaueranzeige
# ============================================================
# Diese App ist NUR Anzeige. Sie verändert niemals den Turnierstand.
# Das Wuzzler-Programm schreibt live_data/turnier_live.json nach GitHub.

GITHUB_OWNER = "juergen-jjj"
GITHUB_REPO = "Wuzzler-LIVE"
GITHUB_BRANCH = "main"
GITHUB_DATA_PATH = "live_data/turnier_live.json"

st.set_page_config(
    page_title="Wuzzler Live",
    page_icon="🏆",
    layout="wide",
)


def github_raw_url():
    return (
        f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"{GITHUB_BRANCH}/{GITHUB_DATA_PATH}"
    )


@st.cache_data(ttl=2, show_spinner=False)
def load_live_data():
    url = github_raw_url()
    request = urllib.request.Request(url, headers={"User-Agent": "Wuzzler-Live-Viewer"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def rows_to_df(rows):
    if not rows or len(rows) < 1:
        return pd.DataFrame()
    headers = [str(x) if x not in (None, "") else f"Spalte {i+1}" for i, x in enumerate(rows[0])]
    data = []
    for row in rows[1:]:
        values = list(row) + [""] * (len(headers) - len(row))
        data.append(values[:len(headers)])
    df = pd.DataFrame(data, columns=headers)
    if not df.empty:
        df = df.loc[~df.apply(lambda r: all(str(v).strip() == "" for v in r), axis=1)]
    return df


def get_sheet(data, name):
    return rows_to_df(data.get("sheets", {}).get(name, []))


def show_current_match(matches):
    if matches.empty or "Status" not in matches.columns:
        st.info("Noch keine Spiele vorhanden.")
        return
    open_games = matches[matches["Status"].astype(str).str.lower() == "offen"]
    if open_games.empty:
        st.success("Alle aktuell übertragenen Spiele sind beendet.")
        return
    game = open_games.iloc[0]
    st.markdown("### 🎯 Aktuelles / nächstes Spiel")
    c1, c2, c3 = st.columns([4, 1.5, 4])
    with c1:
        st.markdown(f"## {game.get('Team 1', '')}")
    with c2:
        st.markdown("## **vs.**")
    with c3:
        st.markdown(f"## {game.get('Team 2', '')}")
    st.caption(f"{game.get('Phase/Runde', '')} · Spiel {game.get('Spiel', '')}")


def render():
    try:
        data = load_live_data()
    except urllib.error.HTTPError as exc:
        st.error(f"Live-Daten nicht erreichbar (HTTP {exc.code}).")
        st.stop()
    except Exception as exc:
        st.error("Die Live-Daten sind noch nicht verfügbar.")
        st.caption(str(exc))
        st.stop()

    overview = get_sheet(data, "Turnierübersicht")
    groups = get_sheet(data, "Gruppentabelle")
    matches = get_sheet(data, "Spiele")
    spritzer = get_sheet(data, "Spritzerwertung")

    st.title("🏆 Wuzzler Live")
    st.caption(f"Letzte Übertragung: {data.get('updated_at', 'unbekannt')} · automatische Aktualisierung alle 2 Sekunden")

    show_current_match(matches)

    if not overview.empty and len(overview.columns) >= 2:
        values = {str(row.iloc[0]): row.iloc[1] for _, row in overview.iterrows()}
        cols = st.columns(4)
        cols[0].metric("Teams", values.get("Teams", "–"))
        cols[1].metric("Phase", values.get("Phase", "–"))
        cols[2].metric("Spiele pro Team", values.get("Spiele pro Team", "–"))
        cols[3].metric("Turnier gestartet", values.get("Turnier gestartet", "–"))

    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.subheader("📊 Gruppentabelle")
        if groups.empty:
            st.info("Noch keine Gruppentabelle vorhanden.")
        else:
            display_cols = [c for c in ["Gruppe", "Rang", "Team", "Punkte", "Tore", "Gegentore", "Tordifferenz", "Spiele"] if c in groups.columns]
            st.dataframe(groups[display_cols] if display_cols else groups, use_container_width=True, hide_index=True)

    with right:
        st.subheader("💦 Spritzerwertung")
        if spritzer.empty:
            st.info("Noch keine Spritzerwertung vorhanden.")
        else:
            display_cols = [c for c in ["Rang", "Name", "Spritzer-Punkte"] if c in spritzer.columns]
            st.dataframe(spritzer[display_cols] if display_cols else spritzer, use_container_width=True, hide_index=True)

    st.subheader("📋 Spielplan")
    if matches.empty:
        st.info("Noch keine Spiele vorhanden.")
    else:
        display_cols = [c for c in ["Phase/Runde", "Gruppe", "Spiel", "Team 1", "Ergebnis", "Team 2", "Sieger", "Status"] if c in matches.columns]
        st.dataframe(matches[display_cols] if display_cols else matches, use_container_width=True, hide_index=True)

    with st.expander("Turnierdetails"):
        if not overview.empty:
            st.dataframe(overview, use_container_width=True, hide_index=True)


# Streamlit führt diesen Bereich automatisch alle 2 Sekunden neu aus.
if hasattr(st, "fragment"):
    @st.fragment(run_every="2s")
    def live_view():
        render()
    live_view()
else:
    render()
