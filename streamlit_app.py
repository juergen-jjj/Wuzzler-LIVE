import html
import time

import pandas as pd
import requests
import streamlit as st

# ============================================================

# STREAMLIT EINSTELLUNGEN

# ============================================================

st.set_page_config(
page_title="Wuzzler LIVE",
page_icon="⚽",
layout="wide",
)

# ============================================================

# GITHUB EINSTELLUNGEN

# ============================================================

GITHUB_OWNER = "juergen-jjj"
GITHUB_REPO = "Wuzzler-LIVE"
GITHUB_BRANCH = "main"
GITHUB_FILE = "live_data/turnier_live.json"

# ============================================================

# AUTOMATISCHE AKTUALISIERUNG

# ============================================================

REFRESH_SECONDS = 5

if "last_refresh" not in st.session_state:

```
st.session_state.last_refresh = (
    time.time()
)
```

# ============================================================

# GITHUB-DATEN LADEN

# ============================================================

@st.cache_data(
ttl=3,
show_spinner=False,
)
def load_live_data():

```
raw_url = (
    "https://raw.githubusercontent.com/"
    f"{GITHUB_OWNER}/"
    f"{GITHUB_REPO}/"
    f"{GITHUB_BRANCH}/"
    f"{GITHUB_FILE}"
)

response = requests.get(
    raw_url,
    timeout=20,
    headers={
        "Cache-Control": "no-cache",
    },
)

if response.status_code != 200:

    raise RuntimeError(
        "GitHub-Datei konnte "
        "nicht geladen werden.\n\n"
        f"HTTP-Status: "
        f"{response.status_code}\n\n"
        f"Antwort:\n"
        f"{response.text}"
    )

try:

    return response.json()

except Exception as error:

    raise RuntimeError(
        "Die GitHub-Datei enthält "
        "kein gültiges JSON.\n\n"
        f"{error}"
    )
```

# ============================================================

# HILFSFUNKTIONEN

# ============================================================

def safe_text(
value,
fallback="",
):

```
if value is None:

    return fallback

return html.escape(
    str(value)
)
```

def safe_number(
value,
fallback=0,
):

```
try:

    return int(
        value
    )

except (
    TypeError,
    ValueError,
):

    return fallback
```

def create_table(
rows,
columns,
):

```
table = pd.DataFrame(
    rows
)

for column in columns:

    if column not in table.columns:

        table[
            column
        ] = ""

return table[
    columns
]
```

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

```
data = load_live_data()
```

except Exception as error:

```
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
```

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

```
st.success(
    "🟢 LIVE-VERBINDUNG AKTIV"
)
```

with update_column:

```
st.write(
    "Letzte Aktualisierung:"
)

st.caption(
    data.get(
        "updated_at",
        "unbekannt"
    )
)
```

with button_column:

```
if st.button(
    "🔄 Neu laden",
    use_container_width=True,
):

    st.cache_data.clear()

    st.rerun()
```

st.divider()

# ============================================================

# AKTUELLES SPIEL

# ============================================================

st.header(
"🔴 JETZT AUF DEM TISCH"
)

if current_match:

```
team1 = safe_text(
    current_match.get(
        "team1",
        "?"
    )
)

team2 = safe_text(
    current_match.get(
        "team2",
        "?"
    )
)

score1 = safe_number(
    current_match.get(
        "score1",
        0
    )
)

score2 = safe_number(
    current_match.get(
        "score2",
        0
    )
)

phase = safe_text(
    current_match.get(
        "phase",
        ""
    )
)

st.markdown(
    f"""
    <div style="
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
    ">

        <div style="
            font-size: 20px;
            color: #8fd3ff;
            font-weight: bold;
            margin-bottom: 18px;
        ">
            {phase}
        </div>

        <div style="
            font-size: 48px;
            font-weight: bold;
            overflow-wrap: anywhere;
        ">
            {team1}
        </div>

        <div style="
            font-size: 24px;
            color: #ffd34e;
            margin: 12px 0;
        ">
            ⚽ GEGEN ⚽
        </div>

        <div style="
            font-size: 48px;
            font-weight: bold;
            overflow-wrap: anywhere;
        ">
            {team2}
        </div>

        <div style="
            font-size: 70px;
            color: #7fffd4;
            font-weight: bold;
            margin-top: 22px;
        ">
            {score1} : {score2}
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)
```

else:

```
st.warning(
    "Aktuell ist kein Spiel "
    "gestartet."
)
```

# ============================================================

# NÄCHSTES SPIEL

# ============================================================

st.header(
"➡️ ALS NÄCHSTES"
)

if next_match:

```
next_team1 = safe_text(
    next_match.get(
        "team1",
        "?"
    )
)

next_team2 = safe_text(
    next_match.get(
        "team2",
        "?"
    )
)

next_phase = safe_text(
    next_match.get(
        "phase",
        ""
    )
)

st.markdown(
    f"""
    <div style="
        text-align: center;
        padding: 22px;
        border-radius: 15px;
        border:
            2px solid
            #2c78a0;
        background:
            rgba(
                44,
                120,
                160,
                0.08
            );
    ">

        <div style="
            font-size: 30px;
            font-weight: bold;
            overflow-wrap: anywhere;
        ">

            {next_team1}

            <span style="
                color: #e6a800;
                margin:
                    0 12px;
            ">
                gegen
            </span>

            {next_team2}

        </div>

        <div style="
            margin-top: 12px;
            color: #777;
            font-size: 17px;
        ">

            {next_phase}

        </div>

    </div>
    """,
    unsafe_allow_html=True,
)
```

else:

```
st.info(
    "Kein nächstes Spiel "
    "vorhanden."
)
```

# ============================================================

# KOMMENDE SPIELE

# ============================================================

st.header(
"📅 KOMMENDE SPIELE"
)

if upcoming_matches:

```
for match in upcoming_matches:

    order = safe_text(
        match.get(
            "order",
            ""
        )
    )

    team1 = safe_text(
        match.get(
            "team1",
            "?"
        )
    )

    team2 = safe_text(
        match.get(
            "team2",
            "?"
        )
    )

    phase = safe_text(
        match.get(
            "phase",
            ""
        )
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
```

else:

```
st.info(
    "Keine weiteren Spiele "
    "vorhanden."
)
```

# ============================================================

# TURNIERSTAND

# ============================================================

st.header(
"🏆 TURNIERSTAND"
)

if standings:

```
for group in standings:

    group_name = safe_text(
        group.get(
            "group",
            "Tabelle"
        )
    )

    teams = group.get(
        "teams",
        []
    )

    st.subheader(
        group_name
    )

    if teams:

        table = create_table(
            teams,
            [
                "rank",
                "team",
                "points",
            ],
        )

        table = table.rename(
            columns={
                "rank": "Rang",
                "team": "Team",
                "points": "Punkte",
            }
        )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rang": (
                    st.column_config.NumberColumn(
                        "Rang",
                        width="small",
                    )
                ),
                "Team": (
                    st.column_config.TextColumn(
                        "Team",
                        width="large",
                    )
                ),
                "Punkte": (
                    st.column_config.NumberColumn(
                        "Punkte",
                        width="small",
                    )
                ),
            },
        )

    else:

        st.info(
            "Für diese Gruppe "
            "sind noch keine "
            "Teams vorhanden."
        )
```

else:

```
st.info(
    "Noch kein Turnierstand "
    "vorhanden."
)
```

# ============================================================

# SPRITZERWERTUNG

# ============================================================

st.header(
"🍹 SPRITZERWERTUNG"
)

if spritzer:

```
spritzer_table = (
    create_table(
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
    column_config={
        "Rang": (
            st.column_config.NumberColumn(
                "Rang",
                width="small",
            )
        ),
        "Team": (
            st.column_config.TextColumn(
                "Team",
                width="large",
            )
        ),
        "Spritzer": (
            st.column_config.NumberColumn(
                "Spritzer",
                width="small",
            )
        ),
    },
)
```

else:

```
st.info(
    "Noch keine "
    "Spritzerdaten vorhanden."
)
```

# ============================================================

# FOOTER

# ============================================================

st.divider()

st.caption(
"⚽ Wuzzler LIVE"
)
