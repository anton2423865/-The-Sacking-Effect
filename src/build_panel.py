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
import matplotlib.pyplot as plt
import soccerdata as sd

TREATMENT_DATE = pd.Timestamp("2026-01-12")  # Alonso sacked, Arbeloa appointed
TEAMS = ["Real Madrid", "Barcelona", "Atlético Madrid"]
ROLLING_WINDOW = 5  # matches


def pull_la_liga(seasons):
    fbref = sd.FBref(leagues="ESP-La Liga", seasons=seasons)
    return fbref.read_schedule().reset_index()


def parse_score(raw):
    """soccerdata returns a single 'score' string like '1\u20133' (an EN-DASH,
    not a hyphen). Split on it and return (home_goals, away_goals), or
    (None, None) if the match hasn't been played / score is missing."""
    if pd.isna(raw):
        return None, None
    parts = str(raw).split("\u2013")
    if len(parts) != 2:
        return None, None
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return None, None


def team_points_series(schedule, team_name):
    """Per-match dataframe of date + matchweek + points earned for one team."""
    home = schedule[schedule["home_team"] == team_name].copy()
    away = schedule[schedule["away_team"] == team_name].copy()

    def pts(row, is_home):
        hs, as_ = parse_score(row["score"])
        if hs is None:
            return None  # not played yet, or unparseable
        if hs == as_:
            return 1
        if is_home:
            return 3 if hs > as_ else 0
        return 3 if as_ > hs else 0

    home["points"] = home.apply(lambda r: pts(r, True), axis=1)
    away["points"] = away.apply(lambda r: pts(r, False), axis=1)

    both = pd.concat([home, away])[["date", "week", "points"]].dropna(subset=["points"])
    both["date"] = pd.to_datetime(both["date"])
    both = both.sort_values("date").reset_index(drop=True)
    both["team"] = team_name
    both["rolling_ppg"] = both["points"].rolling(ROLLING_WINDOW, min_periods=1).mean()
    return both


def main():
    schedule = pull_la_liga(seasons=["2025-2026"])
    schedule.to_csv("la_liga_2025_2026_schedule.csv", index=False)

    all_teams = pd.concat([team_points_series(schedule, t) for t in TEAMS])
    all_teams.to_csv("team_rolling_ppg.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    for team in TEAMS:
        sub = all_teams[all_teams["team"] == team]
        ax.plot(sub["date"], sub["rolling_ppg"], label=team, linewidth=2)

    ax.axvline(TREATMENT_DATE, color="gray", linestyle="--", linewidth=1)
    ax.text(TREATMENT_DATE, ax.get_ylim()[1], "Alonso sacked", rotation=90,
            va="top", ha="right", fontsize=9, color="gray")
    ax.set_ylabel(f"Rolling {ROLLING_WINDOW}-match points per game")
    ax.set_title("Real Madrid vs. comparison clubs, 2025-26 La Liga")
    ax.legend()
    fig.tight_layout()
    fig.savefig("real_madrid_ppg_sanity_check.png", dpi=150)

    print("Saved: la_liga_2025_2026_schedule.csv, team_rolling_ppg.csv, "
          "real_madrid_ppg_sanity_check.png")


if __name__ == "__main__":
    main()
