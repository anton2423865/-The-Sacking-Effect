# ⚽ The Sacking Effect

> **📌 Quick summary (for anyone short on time):** Real Madrid fired their manager in January 2026. Sports headlines will call it either a "genius move" or a "panic move" depending on what happens next — but neither headline is actually *proven* by anything. This project uses a real statistics technique (borrowed from economics) to test, properly, whether firing him actually changed the results, or whether the team would have done the same thing anyway. Right now, the project has finished **Phase 1 of 6** — an early look at the raw numbers — and the honest finding so far is: *you can't tell yet just by looking at a chart, which is exactly why the rest of this project exists.*

---

**Does firing the manager actually change a football team's results — or would it have happened anyway?**

Real Madrid sacked Xabi Alonso on January 12, 2026, seven months into the job, after a Supercopa final loss to Barcelona. The headlines write themselves either way: *"new manager bounce"* if results improve, *"panic move"* if they don't. This project skips the headline and asks the harder question properly, using **synthetic control** — a causal inference method built for exactly this situation: one team, one event, no control group, no A/B test possible.

It's the same family of technique economists use to evaluate real policies (the California tobacco-tax study is the textbook example) and that marketing/growth teams use to measure whether a campaign actually caused a lift. Sport is just the sandbox — the method is the point.

---

## 🧠 Key terms, in plain English

A handful of technical words come up repeatedly below. Here's what they actually mean — no stats background required. Worth a quick read before diving into the rest of the page.

| Term | What it really means |
|---|---|
| **Causal inference** | Figuring out whether A actually *caused* B, rather than B just happening to follow A. |
| **Synthetic control** | Building a fake, "digital twin" version of Real Madrid out of a blend of other clubs, to estimate what would have happened if the manager had *never* been sacked. |
| **Counterfactual** | The "what if" scenario — what would have happened in a world where the sacking never took place. |
| **Donor pool** | The list of other clubs used as ingredients to build that "digital twin" team. |
| **Treatment / treated** | Borrowed from medical trials — here, "the treatment" is the sacking itself, and Real Madrid is "the treated" team. |
| **Pre-treatment fit** | How closely the "digital twin" team's results matched the real team's results *before* the sacking happened. If it doesn't match well here, nothing it says about *after* the sacking can be trusted either. |
| **Placebo test** | Repeating the exact same test on clubs that were *never* sacked, to see how often a "fake effect" shows up purely by chance. This stands in for the significance testing (p-values) used in a more traditional experiment. |
| **Panel data** | Data tracking multiple teams over time, lined up match by match — the format all of this analysis actually runs on. |

---

## 💡 The idea, in 30 seconds

Instead of comparing Real Madrid's results before and after the sacking (unreliable — form changes for a hundred reasons that have nothing to do with the manager), build a **synthetic Real Madrid**: a weighted blend of other elite clubs that never fired their manager, chosen so it closely tracks the real team's form *before* the event. If that synthetic twin fits well pre-event, the gap between it and the real team *after* the event is a defensible estimate of the sacking's actual effect.

> **Think of it like this:** imagine building a clone of Real Madrid out of spare parts from Barcelona, Bayern Munich, Manchester City, and a few other elite clubs — a clone engineered specifically to behave exactly like the real Real Madrid *up until the day of the sacking*. After that day, the clone just keeps doing whatever it would have done anyway, with no managerial change, while the real team lives through the actual event. Whatever gap opens up between the real team and its clone from that point on is the best available estimate of what the sacking actually did.

---

## 📍 Where this stands right now — Phase 1 complete

The first real output: rolling 5-match points-per-game for Real Madrid against two same-league benchmarks, Barcelona and Atlético Madrid, across the full 2025-26 season.

![Real Madrid vs. Barcelona vs. Atlético Madrid, rolling points per game](output/real_madrid_ppg_sanity_check.png)

> **In short:** this chart alone can't answer the question yet — it only shows that guessing by eye isn't good enough, which is exactly why the more rigorous method (and the rest of the roadmap below) is necessary.

**What it already shows, and why it's not the answer yet:**

Real Madrid does jump to a sustained run of 3.0 points per game for about six weeks right after the sacking — the "bounce" story. But Real was *already* climbing beforehand (up from ~1.2 in early December to 2.4 right at the event), so some of that rise could just be a trend continuing on its own. Then in March–April, Real actually dips *below* both Barcelona and Atlético before recovering again at season's end. Eyeballing this chart alone, you genuinely can't tell whether the sacking helped, hurt, or did nothing — which is the entire justification for building this properly instead of trusting a before/after comparison.

Atlético's own swing across the season (0 → 3.0 → 0.6, with no managerial change at all) is a reminder of how noisy a single team's single season is, which is exactly why the real analysis blends *several* donor clubs rather than eyeballing one comparison.

---

## 🗺️ Roadmap

- [x] **Phase 1 — Scope & data audit.** Case list locked, real `soccerdata` schema confirmed, sanity-check chart built (above). *— This is where the project stands right now.*
- [ ] **Phase 2 — Unified panel.** Pull the full donor pool (Bayern, Man City, Liverpool, Arsenal, PSG, Inter) and align every team on *matchweeks relative to treatment*, not calendar dates. *— In plain terms: line every club up by "weeks since the sacking" instead of the regular calendar, so they can all be compared fairly against each other.*
- [ ] **Phase 3 — First synthetic control fit.** Fit the Alonso → Arbeloa case with `pysyncon`, check pre-treatment fit quality before trusting anything. *— This is the step that actually builds the "digital twin" team described above.*
- [ ] **Phase 4 — Placebo tests.** In-space and in-time placebo tests — how you argue significance without a traditional p-value. *— See "Method notes for the curious" below for what a placebo test actually involves.*
- [ ] **Phase 5 — Full case bank.** Repeat across all six historical Real Madrid managerial changes; look for heterogeneity. *— i.e., check whether the effect looks similar or different across all six cases in the table below.*
- [ ] **Phase 6 — Write-up + dashboard.** Portfolio-ready report, optionally a clickable Streamlit app. *— The final, shareable version of all of this.*

---

## 📅 The six cases

These are the six times in Real Madrid's history that fit this project's criteria for a mid-season managerial change — each one becomes its own test case once Phase 5 is reached.

| Date | Change |
|---|---|
| Dec 2005 | Luxemburgo → López Caro |
| Dec 2008 | Schuster → Ramos |
| Jan 2016 | Benítez → Zidane |
| Oct 2018 | Lopetegui → Solari |
| Mar 2019 | Solari → Zidane |
| **Jan 2026** | **Alonso → Arbeloa** *(flagship case, in progress)* |

---

## 🏟️ Donor pool

Real Madrid's talent level rules out ordinary mid-table comparisons, so the donor pool is deliberately elite: **Barcelona, Atlético Madrid** (same league), plus **Bayern Munich, Manchester City, Liverpool, Arsenal, PSG, Inter Milan** — clubs the synthetic-control algorithm can plausibly blend into a believable counterfactual Real Madrid. *(In other words: it wouldn't be a meaningful comparison to blend in a relegation-threatened club — only genuine top-tier peers make the cut.)*

---

## 🔍 Method notes for the curious

Validity here isn't "does the chart look convincing" — it's two checks that come later in the roadmap:

- **Pre-treatment fit quality (MSPE):** if the synthetic team doesn't track the real one closely *before* the event, nothing after the event can be trusted. *In other words: if the "digital twin" wasn't already behaving like Real Madrid before the sacking, there's no reason to trust anything it claims about what would have happened afterward.*
- **Placebo tests:** re-running the exact same procedure on every donor team, pretending each was "treated," to see how often a gap this size shows up by chance alone. This stands in for a p-value. *Think of it like testing a smoke alarm in houses that have no fire — if it goes off constantly anyway, one alarm sounding isn't proof that there's an actual fire.*

---

## 🧰 Stack

- [`soccerdata`](https://soccerdata.readthedocs.io/) — FBref access with proper rate-limiting/caching (FBref blocks naive scrapers outright). *(FBref is a widely used football statistics website.)*
- [`pysyncon`](https://github.com/sdfordham/pysyncon) — synthetic control + placebo testing. *(The library that actually builds the "digital twin" and runs the checks described above.)*
- `pandas`, `numpy`, `matplotlib` — *standard Python tools for cleaning data, doing the underlying math, and drawing charts.*
- Background reading: [*Causal Inference: The Mixtape*](https://mixtape.scunning.com) by Scott Cunningham (free online) — *a friendly, non-textbook introduction to this whole field, for anyone who wants to go deeper.*

---

## ▶️ Running it

*This part is for anyone who wants to actually run the code themselves — feel free to skip ahead if you're just here to follow the project.*

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/data_pull.py        # Phase 1
```

Before trusting any pull, confirm the current `soccerdata` schema — it has shifted across versions:

```python
import soccerdata as sd
schedule = sd.FBref(leagues="ESP-La Liga", seasons=["2025-2026"]).read_schedule().reset_index()
print(schedule.columns.tolist())
```

---

## 🗂️ Repo structure

Here's how the project's files are organized:

```
the-sacking-effect/
  data/
    raw/          # cached pulls, gitignored
    processed/    # cleaned panel.csv, tracked
  src/
    data_pull.py
    panel_builder.py
    synthetic_control.py
    placebo_tests.py
  notebooks/
  output/          # charts + results tables (this README's chart lives here)
  README.md
  requirements.txt
  .gitignore
  LICENSE
```

---

## 🎯 Why this exists

Synthetic control and its close cousin, difference-in-differences, are what marketing and growth teams reach for when they can't run a clean experiment — did the campaign cause the lift, or was it the season? What policy teams use for program evaluation. Building this end-to-end — real messy data, a genuine counterfactual, and validity checks instead of a nice-looking chart — is the point, whether or not Real Madrid ever wins another trophy.

---

## 📄 License

MIT — see `LICENSE`.
