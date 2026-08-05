import json
import time
import urllib.request
import urllib.error

import pandas as pd
import streamlit as st


# ============================================================
# WUZZLER LIVE – Zuschaueranzeige
# ============================================================

GITHUB_OWNER = "juergen-jjj"
GITHUB_REPO = "Wuzzler-LIVE"
GITHUB_BRANCH = "main"
GITHUB_DATA_PATH = "live_data/turnier_live.json"


st.set_page_config(
    page_title="Wuzzler Live",
    page_icon="🏆",
    layout="wide",
)


# ============================================================
# GITHUB
# ============================================================

def github_raw_url():
    return (
        f"https://raw.githubusercontent.com/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"{GITHUB_BRANCH}/{GITHUB_DATA_PATH}"
    )


def load_live_data():
    """
    Lädt die JSON jedes Mal frisch von GitHub.
    Kein Streamlit-Cache, damit Live-Änderungen sofort erkannt werden.
    """

    # Cache-Busting
    url = f"{github_raw_url()}?t={int(time.time())}"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Wuzzler-Live-Viewer",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        raw = response.read().decode("utf-8")

    return json.loads(raw)


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def rows_to_df(rows):
    if not rows:
        return pd.DataFrame()

    if not isinstance(rows, list):
        return pd.DataFrame()

    if len(rows) == 0:
        return pd.DataFrame()

    headers = [
        str(x) if x not in (None, "") else f"Spalte {i + 1}"
        for i, x in enumerate(rows[0])
    ]

    data = []

    for row in rows[1:]:
        if not isinstance(row, list):
            continue

        values = list(row)

        while len(values) < len(headers):
            values.append("")

        data.append(values[:len(headers)])

    df = pd.DataFrame(data, columns=headers)

    if not df.empty:
        df = df.loc[
            ~df.apply(
                lambda r: all(str(v).strip() == "" for v in r),
                axis=1,
            )
        ]

    return df.reset_index(drop=True)


def get_sheet(data, name):
    sheets = data.get("sheets", {})

    if not isinstance(sheets, dict):
        return pd.DataFrame()

    return rows_to_df(sheets.get(name, []))


def text(value):
    if value is None:
        return ""

    value = str(value)

    if value.lower() == "nan":
        return ""

    return value.strip()


def get_value(row, *names):
    for name in names:
        if name in row.index:
            value = text(row[name])
            if value:
                return value

    return ""


def status_normalized(value):
    return text(value).lower().strip()


# ============================================================
# SPIELSTATUS
# ============================================================

def is_live_status(status):
    status = status_normalized(status)

    return status in [
        "offen",
        "läuft",
        "laeuft",
        "laufend",
        "live",
        "aktiv",
        "gestartet",
        "in bearbeitung",
        "in_bearbeitung",
    ]


def is_finished_status(status):
    status = status_normalized(status)

    return status in [
        "beendet",
        "fertig",
        "abgeschlossen",
        "erledigt",
        "geschlossen",
    ]


# ============================================================
# AKTUELLES SPIEL
# ============================================================

def find_current_game(matches):
    if matches.empty:
        return None

    if "Status" not in matches.columns:
        return None

    # 1. Laufendes Spiel suchen
    for _, row in matches.iterrows():
        status = get_value(row, "Status")

        if is_live_status(status):
            return row

    return None


def find_next_game(matches):
    if matches.empty:
        return None

    if "Status" not in matches.columns:
        return None

    # Erstes nicht beendetes Spiel
    for _, row in matches.iterrows():
        status = get_value(row, "Status")

        if not is_finished_status(status):
            return row

    return None


# ============================================================
# GROSSE LIVE-ANZEIGE
# ============================================================

def show_live_match(matches):

    current = find_current_game(matches)

    # --------------------------------------------------------
    # AKTUELLES SPIEL
    # --------------------------------------------------------

    if current is not None:

        team1 = get_value(current, "Team 1", "Team1", "Heimteam")
        team2 = get_value(current, "Team 2", "Team2", "Gastteam")

        score = get_value(
            current,
            "Ergebnis",
            "Score",
            "Spielstand",
        )

        game_no = get_value(
            current,
            "Spiel",
            "Spielnummer",
            "Nr.",
        )

        phase = get_value(
            current,
            "Phase/Runde",
            "Phase",
            "Runde",
        )

        group = get_value(
            current,
            "Gruppe",
        )

        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #111827, #1f2937);
                padding: 28px;
                border-radius: 18px;
                margin-bottom: 20px;
                color: white;
            ">
                <div style="
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 18px;
                ">
                    🟢 LIVE – AKTUELLES SPIEL
                </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([4, 2, 4])

        with c1:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:32px;
                    font-weight:800;
                    padding:15px 5px;
                ">
                    {team1 or "Team 1"}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:42px;
                    font-weight:900;
                    padding:10px 0;
                ">
                    {score or "– : –"}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:32px;
                    font-weight:800;
                    padding:15px 5px;
                ">
                    {team2 or "Team 2"}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        info = []

        if phase:
            info.append(f"🏁 {phase}")

        if group:
            info.append(f"👥 Gruppe {group}")

        if game_no:
            info.append(f"🎮 Spiel {game_no}")

        if info:
            st.caption("   ·   ".join(info))

        return

    # --------------------------------------------------------
    # KEIN LIVE-SPIEL
    # --------------------------------------------------------

    next_game = find_next_game(matches)

    if next_game is not None:

        team1 = get_value(next_game, "Team 1", "Team1")
        team2 = get_value(next_game, "Team 2", "Team2")

        game_no = get_value(
            next_game,
            "Spiel",
            "Spielnummer",
            "Nr.",
        )

        phase = get_value(
            next_game,
            "Phase/Runde",
            "Phase",
            "Runde",
        )

        st.info("🟡 Aktuell läuft kein Spiel")

        c1, c2, c3 = st.columns([4, 2, 4])

        with c1:
            st.markdown(f"### {team1 or 'Team 1'}")

        with c2:
            st.markdown("### **VS**")

        with c3:
            st.markdown(f"### {team2 or 'Team 2'}")

        info = []

        if phase:
            info.append(phase)

        if game_no:
            info.append(f"Spiel {game_no}")

        if info:
            st.caption(" · ".join(info))

    else:
        st.info("Noch keine Spiele vorhanden.")


# ============================================================
# TURNIERÜBERSICHT
# ============================================================

def show_overview(overview):

    if overview.empty or len(overview.columns) < 2:
        return

    values = {}

    for _, row in overview.iterrows():
        key = text(row.iloc[0])

        if key:
            values[key] = text(row.iloc[1])

    st.markdown("### 📌 Turnierübersicht")

    cols = st.columns(5)

    cols[0].metric(
        "Teams",
        values.get("Teams", "–"),
    )

    cols[1].metric(
        "Phase",
        values.get("Phase", "–"),
    )

    cols[2].metric(
        "Spiele pro Team",
        values.get("Spiele pro Team", "–"),
    )

    cols[3].metric(
        "Turnier gestartet",
        values.get("Turnier gestartet", "–"),
    )

    cols[4].metric(
        "Spiele",
        values.get("Spiele", "–"),
    )


# ============================================================
# GRUPPENTABELLE
# ============================================================

def show_group_table(groups):

    st.markdown("### 🏆 Gruppentabelle")

    if groups.empty:
        st.info("Noch keine Gruppentabelle vorhanden.")
        return

    display_cols = [
        "Gruppe",
        "Rang",
        "Team",
        "Punkte",
        "Tore",
        "Gegentore",
        "Tordifferenz",
        "Spiele",
        "Siege",
        "Unentschieden",
        "Niederlagen",
    ]

    display_cols = [
        col for col in display_cols
        if col in groups.columns
    ]

    table = groups[display_cols] if display_cols else groups

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SPRITZERWERTUNG
# ============================================================

def show_spritzer(spritzer):

    st.markdown("### 💦 Spritzerwertung")

    if spritzer.empty:
        st.info("Noch keine Spritzerwertung vorhanden.")
        return

    display_cols = [
        "Rang",
        "Name",
        "Spritzer-Punkte",
    ]

    display_cols = [
        col for col in display_cols
        if col in spritzer.columns
    ]

    table = spritzer[display_cols] if display_cols else spritzer

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SPIELPLAN
# ============================================================

def show_match_schedule(matches):

    st.markdown("### 📋 Spielplan")

    if matches.empty:
        st.info("Noch keine Spiele vorhanden.")
        return

    display_cols = [
        "Phase/Runde",
        "Gruppe",
        "Spiel",
        "Team 1",
        "Ergebnis",
        "Team 2",
        "Sieger",
        "Status",
    ]

    display_cols = [
        col for col in display_cols
        if col in matches.columns
    ]

    table = matches[display_cols] if display_cols else matches

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# NÄCHSTE SPIELE
# ============================================================

def show_next_games(matches):

    if matches.empty or "Status" not in matches.columns:
        return

    upcoming = []

    for _, row in matches.iterrows():

        status = get_value(row, "Status")

        if is_finished_status(status):
            continue

        team1 = get_value(row, "Team 1", "Team1")
        team2 = get_value(row, "Team 2", "Team2")

        if not team1 and not team2:
            continue

        upcoming.append(row)

        if len(upcoming) >= 5:
            break

    if not upcoming:
        return

    st.markdown("### ⏭️ Als Nächstes")

    cols = st.columns(min(len(upcoming), 3))

    for i, row in enumerate(upcoming[:3]):

        team1 = get_value(row, "Team 1", "Team1")
        team2 = get_value(row, "Team 2", "Team2")

        game = get_value(
            row,
            "Spiel",
            "Spielnummer",
        )

        with cols[i]:
            st.markdown(
                f"""
                **Spiel {game or "–"}**

                {team1 or "Team 1"}

                **vs.**

                {team2 or "Team 2"}
                """
            )


# ============================================================
# HAUPTANZEIGE
# ============================================================

def render():

    try:
        data = load_live_data()

    except urllib.error.HTTPError as exc:
        st.error(
            f"Live-Daten nicht erreichbar "
            f"(HTTP {exc.code})."
        )
        return

    except Exception as exc:
        st.error("Die Live-Daten sind noch nicht verfügbar.")
        st.caption(str(exc))
        return

    overview = get_sheet(
        data,
        "Turnierübersicht",
    )

    groups = get_sheet(
        data,
        "Gruppentabelle",
    )

    matches = get_sheet(
        data,
        "Spiele",
    )

    spritzer = get_sheet(
        data,
        "Spritzerwertung",
    )

    # ========================================================
    # HEADER
    # ========================================================

    st.title("🏆 Wuzzler Live")

    updated = data.get(
        "updated_at",
        "unbekannt",
    )

    st.caption(
        f"🔄 Letzte Übertragung: {updated} "
        f"· Live-Aktualisierung alle 2 Sekunden"
    )

    # ========================================================
    # AKTUELLES SPIEL
    # ========================================================

    show_live_match(matches)

    st.divider()

    # ========================================================
    # ÜBERSICHT
    # ========================================================

    show_overview(overview)

    st.divider()

    # ========================================================
    # NÄCHSTE SPIELE
    # ========================================================

    show_next_games(matches)

    st.divider()

    # ========================================================
    # TABELLEN
    # ========================================================

    left, right = st.columns([2, 1])

    with left:
        show_group_table(groups)

    with right:
        show_spritzer(spritzer)

    st.divider()

    # ========================================================
    # SPIELPLAN
    # ========================================================

    show_match_schedule(matches)

    # ========================================================
    # DETAILS
    # ========================================================

    with st.expander("🔧 Technische Turnierdetails"):

        st.write(
            f"GitHub: `{GITHUB_OWNER}/{GITHUB_REPO}`"
        )

        st.write(
            f"Datei: `{GITHUB_DATA_PATH}`"
        )

        st.write(
            f"JSON aktualisiert: `{updated}`"
        )

        st.write(
            f"Spiele geladen: `{len(matches)}`"
        )

        st.write(
            f"Teams in Tabelle: `{len(groups)}`"
        )


# ============================================================
# LIVE-MODUS
# ============================================================

if hasattr(st, "fragment"):

    @st.fragment(run_every="2s")
    def live_view():
        render()

    live_view()

else:
    render()
