import base64
import html
import json

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Wuzzler LIVE", page_icon="⚽", layout="wide")

GITHUB_OWNER = "juergen-jjj"
GITHUB_REPO = "Wuzzler-LIVE"
GITHUB_BRANCH = "main"
GITHUB_FILE = "live_data/turnier_live.json"

try:
    GITHUB_TOKEN = str(st.secrets["GITHUB_TOKEN"]).strip()
except Exception:
    st.error("Der GitHub-Token wurde nicht in den Streamlit Secrets gefunden.")
    st.info("Streamlit Cloud → Manage app → Settings → Secrets")
    st.code('GITHUB_TOKEN = "github_pat_DEIN_TOKEN"')
    st.stop()


def safe_text(value, fallback=""):
    if value is None:
        return fallback
    return html.escape(str(value))


def safe_number(value, fallback=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def load_live_data():
    api_url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/contents/{GITHUB_FILE}"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Cache-Control": "no-cache",
    }
    response = requests.get(
        api_url,
        params={"ref": GITHUB_BRANCH},
        headers=headers,
        timeout=20,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub-API-Fehler: HTTP {response.status_code}\n{response.text}"
        )
    github_file = response.json()
    encoded = github_file.get("content", "").replace("\n", "").replace("\r", "")
    if not encoded:
        raise RuntimeError("GitHub hat keinen Dateiinhalt geliefert.")
    try:
        return json.loads(base64.b64decode(encoded).decode("utf-8"))
    except Exception as error:
        raise RuntimeError(f"Die GitHub-Datei konnte nicht als JSON gelesen werden.\n{error}")


st.title("⚽ WUZZLER LIVE")


@st.fragment(run_every="10s")
def live_display():
    try:
        data = load_live_data()
    except Exception as error:
        st.error("Die Live-Daten konnten nicht geladen werden.")
        st.code(str(error))
        if st.button("🔄 Erneut versuchen", key="retry_button", use_container_width=True):
            st.rerun()
        return

    live = data.get("live_view", {}) or {}
    current_match = live.get("current_match", {}) or {}
    next_match = live.get("next_match", {}) or {}
    upcoming_matches = live.get("upcoming_matches", []) or []
    standings = live.get("standings", []) or []
    spritzer = live.get("spritzer", []) or []

    left, middle, right = st.columns([2, 3, 1])
    with left:
        st.success("🟢 LIVE AKTIV")
    with middle:
        st.caption("Letzte Aktualisierung: " + str(data.get("updated_at", "unbekannt")))
    with right:
        if st.button("🔄 Neu laden", key="manual_reload", use_container_width=True):
            st.rerun()

    st.divider()
    st.header("🔴 Aktuelles Spiel")

    phase_raw = str(current_match.get("phase", ""))
    phase = safe_text(current_match.get("phase", "Turnier"))
    team1 = safe_text(current_match.get("team1", "?"))
    team2 = safe_text(current_match.get("team2", "?"))
    team3 = safe_text(current_match.get("team3", "?"))

    finished = phase_raw in {"🏆 Turnier beendet", "final_ranking", "finished"}

    if finished:
        html_current = f"""
<div style="text-align:center;padding:42px 25px;border-radius:25px;background:linear-gradient(180deg,#102b40,#07151f);border:4px solid #FFD700;color:white;box-shadow:0 0 30px rgba(255,215,0,.25);">
<div style="font-size:52px;font-weight:bold;color:#FFD700;margin-bottom:8px;">🏆 TURNIER BEENDET 🏆</div>
<div style="font-size:22px;color:#8fd3ff;margin-bottom:28px;letter-spacing:2px;">SIEGEREHRUNG</div>
<div style="background:linear-gradient(135deg,#FFD700,#d4af37);color:#111;padding:22px;border-radius:20px;margin:16px auto;width:88%;box-shadow:0 0 25px rgba(255,215,0,.45);"><div style="font-size:30px;">🥇 1. PLATZ</div><div style="font-size:44px;font-weight:bold;margin-top:8px;overflow-wrap:anywhere;">{team1}</div></div>
<div style="background:linear-gradient(135deg,#eeeeee,#bdbdbd);color:#111;padding:20px;border-radius:19px;margin:16px auto;width:81%;box-shadow:0 0 20px rgba(220,220,220,.35);"><div style="font-size:28px;">🥈 2. PLATZ</div><div style="font-size:38px;font-weight:bold;margin-top:7px;overflow-wrap:anywhere;">{team2}</div></div>
<div style="background:linear-gradient(135deg,#e0a06a,#b96f32);color:white;padding:18px;border-radius:18px;margin:16px auto;width:75%;box-shadow:0 0 20px rgba(205,127,50,.4);"><div style="font-size:26px;">🥉 3. PLATZ</div><div style="font-size:34px;font-weight:bold;margin-top:7px;overflow-wrap:anywhere;">{team3}</div></div>
<div style="margin-top:28px;font-size:21px;color:#8fd3ff;font-weight:bold;">Vielen Dank an alle Teilnehmer! ⚽</div>
</div>"""
        st.markdown(html_current, unsafe_allow_html=True)
    elif current_match:
        html_current = f"""
<div style="text-align:center;padding:32px 20px;border-radius:22px;background:linear-gradient(180deg,#12324a,#0b202f);color:white;border:2px solid #2c78a0;">
<div style="font-size:21px;color:#8fd3ff;font-weight:bold;margin-bottom:20px;">{phase}</div>
<div style="font-size:42px;font-weight:bold;overflow-wrap:anywhere;">{team1}</div>
<div style="font-size:24px;color:#ffd34e;margin:12px 0;">⚽ GEGEN ⚽</div>
<div style="font-size:42px;font-weight:bold;overflow-wrap:anywhere;">{team2}</div>
</div>"""
        st.markdown(html_current, unsafe_allow_html=True)
    else:
        st.info("Aktuell ist kein Spiel gestartet.")

    if not finished:
        st.header("➡️ ALS NÄCHSTES")
        if next_match:
            a = safe_text(next_match.get("team1", "?"))
            b = safe_text(next_match.get("team2", "?"))
            p = safe_text(next_match.get("phase", "Vorrunde"))
            st.markdown(f"""<div style="text-align:center;padding:22px;border-radius:15px;border:2px solid #2c78a0;"><div style="font-size:30px;font-weight:bold;overflow-wrap:anywhere;">{a} <span style="color:#e6a800;margin:0 12px;">gegen</span> {b}</div><div style="margin-top:12px;color:#777;font-size:17px;">{p}</div></div>""", unsafe_allow_html=True)
        else:
            st.info("Kein nächstes Spiel vorhanden.")

        st.header("📅 KOMMENDE SPIELE")
        if upcoming_matches:
            for match in upcoming_matches:
                order = safe_text(match.get("order", ""))
                a = safe_text(match.get("team1", "?"))
                b = safe_text(match.get("team2", "?"))
                p = safe_text(match.get("phase", ""))
                st.write(f"**Spiel {order}:** {a} gegen {b}")
                if p:
                    st.caption(p)
        else:
            st.info("Keine kommenden Spiele vorhanden.")

    st.header("🏆 TURNIERSTAND")
    if standings:
        for group in standings:
            group_name = safe_text(group.get("group", "Tabelle"))
            teams = group.get("teams", []) or []
            st.subheader(group_name)
            if teams:
                rows = [{
                    "Rang": safe_number(t.get("rank", 0)),
                    "Team": str(t.get("team", "?")),
                    "Punkte": safe_number(t.get("points", 0)),
                } for t in teams]
                st.dataframe(pd.DataFrame(rows, columns=["Rang", "Team", "Punkte"]), use_container_width=True, hide_index=True)
            else:
                st.info("Für diese Gruppe sind noch keine Teams vorhanden.")
    else:
        st.info("Noch kein Turnierstand vorhanden.")

    st.header("🍹 SPRITZERWERTUNG")
    if spritzer:
        rows = [{
            "Rang": safe_number(e.get("rank", 0)),
            "Team": str(e.get("team", "?")),
            "Spritzer": safe_number(e.get("score", 0)),
        } for e in spritzer]
        st.dataframe(pd.DataFrame(rows, columns=["Rang", "Team", "Spritzer"]), use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Spritzerdaten vorhanden.")

    st.divider()
    st.caption("⚽ Wuzzler LIVE · automatische Aktualisierung alle 10 Sekunden")


live_display()
