"""
Kiosk Server Launcher
Smart Body Posture Recognition & Guidance System
GLA University - B.Tech CSE Mini-Project (Team OG-Coders T-89)
"""

import sys
import webbrowser
import threading
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.api.app import create_app
from src.database.db import DatabaseManager
from config.settings import HOST, PORT, DEBUG


def seed_baseline_analytics(db: DatabaseManager) -> None:
    """Pre-populates sample historical analytics to demonstrate KPI dashboards."""
    try:
        kpis = db.get_analytics_kpis()
        if kpis["totalSessions"] == 0:
            print("[Init] Seeding baseline clinical trial session records...")
            # Seed 12 sample sessions
            sample_errors = [
                ["BP_NO_SLOUCH"],
                ["BP_UNCROSSED_LEGS"],
                ["BP_ARM_HEART_LEVEL"],
                ["BP_NO_SLOUCH", "BP_ARM_HEART_LEVEL"],
                [],
                [],
                ["WT_STANDING_UPRIGHT"],
                ["ECG_ARMS_RESTING"],
            ]
            for i, errs in enumerate(sample_errors):
                meas = "BP" if i < 6 else ("Weight" if i < 9 else "ECG")
                s_id = db.create_session(meas)
                dur = 12000 + (i * 1500)
                success = len(errs) <= 2
                db.complete_session(s_id, success=success)
                db.log_analytics_summary(s_id, meas, dur, errs, triggered=success)
                for e in errs:
                    db.log_posture_event(s_id, e)
    except Exception as e:
        print(f"[Init] Warning during database seeding: {e}")


def open_browser_delayed(url: str, delay: float = 1.2) -> None:
    """Opens the kiosk UI in default browser once the server has booted."""
    time.sleep(delay)
    print(f"\n[Kiosk] Launching kiosk interface in browser: {url}")
    webbrowser.open(url)


def main():
    print("=" * 65)
    print(" Smart Body Posture Recognition & Guidance System v1.0.0")
    print(" GLA University - B.Tech CSE Mini-Project")
    print(" Team: OG-Coders (T-89) | UR: 2415500155 (Dhananjay Chaudhary)")
    print(" Mentor: Rohit Kumar Gupta Sir")
    print("=" * 65)

    db = DatabaseManager()
    seed_baseline_analytics(db)

    app = create_app()
    kiosk_url = f"http://{HOST}:{PORT}"

    # Open browser automatically in a background thread
    threading.Thread(target=open_browser_delayed, args=(kiosk_url,), daemon=True).start()

    print(f"\n[Kiosk] Server listening on {kiosk_url}")
    print("[Kiosk] Press Ctrl+C in terminal to stop server.\n")

    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)


if __name__ == "__main__":
    main()
