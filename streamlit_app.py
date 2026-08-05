import base64
import json

import requests
import streamlit as st


# Diese Werte müssen zu deinem Repository passen
GITHUB_OWNER = "juergen-jj"
GITHUB_REPO = "Wuzzkler-LIVE"
GITHUB_BRANCH = "main"
GITHUB_FILE = "live_data/turnier_live.json"


@st.cache_data(
    ttl=5,
    show_spinner=False
)
def load_live_data():

    token = st.secrets[
        "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"
    ]

    api_url = (
        "https://api.github.com/repos/"
        f"{GITHUB_OWNER}/"
        f"{GITHUB_REPO}/"
        "contents/"
        f"{GITHUB_FILE}"
    )

    headers = {
        "Accept":
            "application/vnd.github+json",

        "Authorization":
            f"Bearer {token}",

        "X-GitHub-Api-Version":
            "2022-11-28",
    }

    response = requests.get(
        api_url,
        params={
            "ref":
                GITHUB_BRANCH
        },
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    github_data = (
        response.json()
    )

    encoded_content = (
        github_data[
            "content"
        ]
        .replace(
            "\n",
            ""
        )
    )

    json_text = (
        base64
        .b64decode(
            encoded_content
        )
        .decode(
            "utf-8"
        )
    )

    return json.loads(
        json_text
    )
