"""Virtual Assistant RAG: local RAG chatbot for operational manuals."""

import sys
from pathlib import Path


def main() -> None:
    """Launch the Streamlit chat interface."""
    from streamlit.web import cli as stcli

    app_path = Path(__file__).with_name("app.py")
    # Extra arguments are forwarded to Streamlit (e.g. `--server.port 8502`).
    sys.argv = ["streamlit", "run", *sys.argv[1:], str(app_path)]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
