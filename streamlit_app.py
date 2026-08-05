import streamlit as st
import requests
import pandas as pd
from datetime import datetime


# ============================================================
# STREAMLIT-EINSTELLUNGEN
# ============================================================

st.set_page_config(
    page_title="Wuzzler LIVE",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GITHUB-DATENQUELLE
# ============================================================

JSON_URL = (
    "https://raw.githubusercontent.com/"
    "juergen-jjj/"
    "Wuzzler-LIVE/"
    "main/"
    "live_data/"
    "turnier_live.json"
)


# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            linear-gradient(
                135deg,
                #07111f,
                #102b42,
                #07111f
            );
        color: white;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: white !important;
    }

    .title-box {
        text-align: center;
        margin-bottom: 1rem;
    }

    .main-title {
        font-size: clamp(
            2.5rem,
            7vw,
            5rem
        );
        font-weight: 900;
        color: white;
        letter-spacing: 0.08em;
    }

    .sub-title {
        color: #8fd3ff;
        font-size: 1.1rem;
    }

    .status-box {
        text-align: center;
        background:
            rgba(
                255,
                255,
                255,
                0.08
            );
        border-radius: 18px;
        padding: 0.8rem;
        margin-bottom: 1rem;
        color: #9fe7ff;
        font-weight: 700;
    }

    .section-title {
        color: #8fd3ff;
        font-size: 1.15rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
    }

    .live-card {
        text-align: center;
        padding: 1.8rem;
        border-radius: 25px;

        background:
            linear-gradient(
                145deg,
                #17476a,
                #0a2035
            );

        border:
            2px solid
            rgba(
                91,
                192,
                235,
                0.7
            );

        box-shadow:
            0 18px 50px
            rgba(
                0,
                0,
                0,
                0.4
            );
    }

    .phase {
        color: #8fd3ff;
        font-size: 1rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    .team {
        color: white;

        font-size:
            clamp(
                2rem,
                5vw,
                4.5rem
            );

        font-weight: 900;
        overflow-wrap: anywhere;
    }

    .gegen {
        color: #ffd34e;

        font-size:
            clamp(
                1.5rem,
                3vw,
                2.5rem
            );

        font-weight: 900;
        margin: 0.4rem;
    }

    .score {
        color: #7fffd4;

        font-size:
            clamp(
                3rem,
                8vw,
                6rem
            );

        font-weight: 900;
        margin-top: 0.8rem;
    }

    .next-card {
        text-align: center;

        padding: 1.3rem;

        border-radius: 18px;

        background:
            rgba(
                255,
                255,
                255,
                0.08
            );

        border:
            1px solid
            rgba(
                255,
                255,
                255,
                0.15
            );
    }

    .next-label {
        color: #ffd34e;

        font-size: 0.85rem;

        font-weight: 900;

        letter-spacing: 0.1em;

        text-transform: uppercase;
    }

    .next-teams {
        color: white;

        font-size:
            clamp(
                1.3rem,
                3vw,
                2.2rem
            );

        font-weight: 800;

        margin-top: 0.8rem;

        overflow-wrap: anywhere;
    }

    .upcoming-card {

        background:
            rgba(
                255,
                255,
                255,
                0.06
            );

        border-left:
            4px solid
            #5bc0eb;

        border-radius: 10px;

        padding:
            0.8rem
            1rem;

        margin-bottom:
            0.5rem;

        color: white;
    }

    .footer {
        text-align: center;

        color: #8b9aa8;

        margin-top: 2rem;

        font-size: 0.85rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# JSON LADEN
# ============================================================

@st.cache_data(
    ttl=5,
    show_spinner=False
)
def load_data():

    response = requests.get(
        JSON_URL,
        timeout=15,
        headers={
            "Cache-Control":
                "no-cache"
        }
    )

    response.raise_for_status()

    return response.json()


try:

    data = load_data()

except Exception as error:

    st.error(
        "Die Live-Daten "
        "konnten nicht geladen werden."
    )

    st.code(
        str(error)
    )

    st.stop()


# ============================================================
# LIVE_VIEW AUS JSON HOLEN
# ============================================================

live = data.get(
    "live_view",
    {}
)

status = live.get(
    "status",
    "Keine Verbindung"
)

phase = live.get(
    "phase",
    ""
)

current = live.get(
    "current_match"
)

next_match = live.get(
    "next_match"
)

upcoming = live.get(
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

spritzer_locked = live.get(
    "spritzer_locked",
    False
)

spritzer_timer = live.get(
    "spritzer_timer_active",
    False
)

updated_at = data.get(
    "updated_at",
    ""
)


# ============================================================
# KOPF
# ============================================================

st.markdown(
    """
    <div class="title-box">

        <div class="main-title">
            ⚽ WUZZLER LIVE
        </div>

        <div class="sub-title">

            Aktuelle Spiele,
            Turnierstand
            und Spritzerwertung

        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    f"""
    <div class="status-box">

        {status}

        &nbsp; • &nbsp;

        Phase:
        {phase}

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

tab_live, tab_stand, tab_spritzer = st.tabs(
    [

        "🔴 LIVE",

        "🏆 TURNIERSTAND",

        "🍹 SPRITZERWERTUNG"

    ]
)


# ============================================================
# LIVE-TAB
# ============================================================

with tab_live:

    st.markdown(
        """
        <div class="section-title">

            Jetzt auf dem Tisch

        </div>
        """,
        unsafe_allow_html=True,
    )


    if current:

        team1 = current.get(
            "team1",
            "?"
        )

        team2 = current.get(
            "team2",
            "?"
        )

        score1 = current.get(
            "score1",
            0
        )

        score2 = current.get(
            "score2",
            0
        )

        current_phase = current.get(
            "phase",
            phase
        )


        st.markdown(
            f"""
            <div class="live-card">

                <div class="phase">

                    {current_phase}

                </div>

                <div class="team">

                    {team1}

                </div>

                <div class="gegen">

                    GEGEN

                </div>

                <div class="team">

                    {team2}

                </div>

                <div class="score">

                    {score1}
                    :
                    {score2}

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "Aktuell läuft "
            "kein Spiel."
        )


    # --------------------------------------------------------
    # NÄCHSTES SPIEL
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-title">

            Als Nächstes

        </div>
        """,
        unsafe_allow_html=True,
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


        st.markdown(
            f"""
            <div class="next-card">

                <div class="next-label">

                    Nächste Begegnung

                </div>

                <div class="next-teams">

                    {next_team1}

                    gegen

                    {next_team2}

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "Es ist kein "
            "nächstes Spiel vorhanden."
        )


    # --------------------------------------------------------
    # WEITERE SPIELE
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-title">

            Weitere kommende Spiele

        </div>
        """,
        unsafe_allow_html=True,
    )


    if upcoming:

        for match in upcoming:

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

            match_phase = match.get(
                "phase",
                ""
            )


            st.markdown(
                f"""
                <div class="upcoming-card">

                    <b>

                        Spiel
                        {order}

                    </b>

                    &nbsp; —

                    {team1}

                    gegen

                    {team2}

                    <br>

                    <small>

                        {match_phase}

                    </small>

                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.caption(
            "Keine weiteren "
            "Spiele vorhanden."
        )


# ============================================================
# TURNIERSTAND
# ============================================================

with tab_stand:

    if standings:

        for group in standings:

            group_name = group.get(
                "group",
                "Turnier"
            )

            teams = group.get(
                "teams",
                []
            )


            st.subheader(
                group_name
            )


            if teams:

                table = pd.DataFrame(
                    teams
                )


                rename_columns = {

                    "rank":
                        "Rang",

                    "team":
                        "Team",

                    "points":
                        "Punkte",

                    "goals":
                        "Tore",

                    "against":
                        "Gegentore",

                    "games":
                        "Spiele"

                }


                table = table.rename(
                    columns=
                    rename_columns
                )


                columns = [

                    column

                    for column in [

                        "Rang",

                        "Team",

                        "Punkte",

                        "Tore",

                        "Gegentore",

                        "Spiele"

                    ]

                    if column
                    in table.columns

                ]


                st.dataframe(

                    table[
                        columns
                    ],

                    use_container_width=True,

                    hide_index=True

                )

    else:

        st.info(
            "Noch kein "
            "Turnierstand vorhanden."
        )


# ============================================================
# SPRITZERWERTUNG
# ============================================================

with tab_spritzer:

    if spritzer_locked:

        st.warning(
            "Die Spritzerwertung "
            "ist beendet."
        )

    elif spritzer_timer:

        st.warning(
            "Der Spritzer-Endtimer "
            "läuft."
        )

    else:

        st.success(
            "Die Spritzerwertung "
            "ist aktiv."
        )


    if spritzer:

        spritzer_table = pd.DataFrame(
            spritzer
        )


        spritzer_table = (
            spritzer_table.rename(
                columns={

                    "rank":
                        "Rang",

                    "team":
                        "Team",

                    "score":
                        "Spritzer"

                }
            )
        )


        st.dataframe(

            spritzer_table[

                [

                    "Rang",

                    "Team",

                    "Spritzer"

                ]

            ],

            use_container_width=True,

            hide_index=True

        )

    else:

        st.info(
            "Noch keine "
            "Spritzerdaten vorhanden."
        )


# ============================================================
# FOOTER
# ============================================================

if updated_at:

    try:

        date_text = (
            datetime
            .fromisoformat(
                updated_at
            )
            .strftime(
                "%d.%m.%Y "
                "– "
                "%H:%M:%S"
            )
        )

    except Exception:

        date_text = updated_at

else:

    date_text = "unbekannt"


st.markdown(
    f"""
    <div class="footer">

        Letzte Aktualisierung:

        {date_text}

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MANUELLES NEULADEN
# ============================================================

if st.button(
    "🔄 Daten neu laden",
    use_container_width=True
):

    st.cache_data.clear()

    st.rerun()
