"""
build_panel.py

Step 1 of the synthetic-control project: pull La Liga match results for
Real Madrid and two comparison clubs (Barcelona, Atletico Madrid) for the
2025-26 season, compute rolling points-per-game, and plot the trajectories
around the Jan 12, 2026 Xabi Alonso -> Alvaro Arbeloa managerial change.

This is a sanity check, not the final analysis -- the goal is just to see,
by eye, whether Real Madrid's trajectory visibly bends after the change
before you invest time in the full synthetic control pipeline.

INSTALL FIRST:
    pip install soccerdata pandas matplotlib --break-system-packages

WHY soccerdata AND NOT A HAND-ROLLED SCRAPER:
FBref actively blocks plain requests/BeautifulSoup scrapers (bot detection).
soccerdata is a maintained wrapper that handles FBref's rate limiting and
caches results locally (~/soccerdata by default), so re-runs are fast after
the first pull. Docs: https://soccerdata.readthedocs.io/

NOTE ON COLUMN NAMES:
soccerdata's schema has shifted slightly across versions. Before running
the full script, run this in a notebook/REPL to confirm real column names:
    import soccerdata as sd
    fbref = sd.FBref(leagues="ESP-La Liga", seasons=["2025-2026"])
    schedule = fbref.read_schedule().reset_index()
    print(schedule.columns.tolist())
    print(schedule.head())
Adjust the column names below (date / home_team / away_team / home_score /
away_score) if your installed version differs.
"""

import pandas as pd
import soccerdata as sd


def pull_schedule(league, seasons):
    """
    Pull a league schedule from FBref using soccerdata.
    """
    fbref = sd.FBref(leagues=league, seasons=seasons)
    return fbref.read_schedule().reset_index()


def parse_score(raw):
    """
    Convert a score such as '2–1' into (home_goals, away_goals).

    Returns (None, None) when the score is missing or cannot be parsed.
    """
    if pd.isna(raw):
        return None, None

    parts = str(raw).split("–")

    if len(parts) != 2:
        return None, None

    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return None, None


def team_points_series(schedule, team_name):
    """
    Create a per-match dataframe containing:

    date
    week
    points
    team
    rolling_ppg
    """

    home = schedule[schedule["home_team"] == team_name].copy()
    away = schedule[schedule["away_team"] == team_name].copy()

    def points(row, is_home):
        home_score, away_score = parse_score(row["score"])

        if home_score is None:
            return None

        if home_score == away_score:
            return 1

        if is_home:
            return 3 if home_score > away_score else 0

        return 3 if away_score > home_score else 0

    home["points"] = home.apply(
        lambda row: points(row, True),
        axis=1
    )

    away["points"] = away.apply(
        lambda row: points(row, False),
        axis=1
    )

    both = pd.concat([home, away])

    both = both[
        ["date", "week", "points"]
    ].dropna(subset=["points"])

    both["date"] = pd.to_datetime(both["date"])

    both = both.sort_values("date").reset_index(drop=True)

    both["team"] = team_name

    both["rolling_ppg"] = (
        both["points"]
        .rolling(5, min_periods=1)
        .mean()
    )

    return both