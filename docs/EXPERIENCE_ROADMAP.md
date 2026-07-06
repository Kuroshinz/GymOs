# Experience Roadmap

The complete gym experience, from opening the application to full autopilot.

---

## 1. Opening the Application

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| Launch | `python main.py` | Desktop shortcut, autostart option |
| Startup time | <3 seconds | <1 second (v0.8) |
| First view | Dashboard — today's workout, nutrition, weight, PR, streak | Same, with weekly summary (v0.6) |
| Database | Auto-creates on first run | Auto-backup on every launch |

---

## 2. Starting a Workout

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| Today's plan | Dashboard shows scheduled day | Same |
| Start session | Open program → select day → Start | One-click "Start Today's Workout" |
| Equipment prep | Manual | Show required equipment from exercise definitions |
| Warm-up guidance | — | Recommended warm-up sets from knowledge/ (v0.6) |

---

## 3. Live Coaching (During Workout)

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| Set logging | Weight, reps, RPE/RIR input | Same + RPE auto-calc from RIR (v0.6) |
| Previous session | Auto-displayed for comparison | Same |
| Rest timer | Manual | Auto-start after set log (v0.6) |
| Form tips | — | Knowledge-based form cues per exercise (v0.7) |
| Fatigue warning | — | Alert when RIR consistently too low (v0.6 via FatigueRule) |
| PR detection | Auto-detect on completion | Inline notification ("PR! +2.5kg") |
| Auto-save | Every 30 seconds | Same |

---

## 4. Workout Summary

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| On completion | Modal with duration, volume, exercises | Same |
| PR celebration | Visual highlight | Same |
| Nutrition nudge | — | "You burned ~X calories — consider post-workout meal" (v0.7) |
| Recovery check | — | "Your fatigue is high — consider early rest day" (v0.6 via GymBrain) |

---

## 5. Weekly Review

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| Generation | WeeklyReviewGenerator exists | Same |
| Dashboard rendering | Not wired | Rich weekly review widget (v0.6) |
| Content | Volume trend, sessions completed, PRs | + Nutrition compliance, recovery trend, recommendations summary |
| Export | — | PDF/JSON export of weekly review (v0.7) |

---

## 6. Daily Intelligence

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| Recommendations | GymBrain evaluates 18 rules | Same |
| Display | Dashboard shows top recommendations | Prioritized, categorized display (v0.6) |
| Explanations | Structured evidence | Natural language explanations (v0.8) |
| Actionability | Read-only | One-click actions ("Schedule deload", "Increase protein") (v0.7) |

---

## 7. Mesocycle Review (4-8 Weeks)

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| Current | Manual review of charts | Automated mesocycle analysis (v0.7) |
| Content | — | Volume progression, strength gains, muscle balance, recovery trend |
| Deload decision | Manual (rule suggests) | Auto-scheduled deload (v0.9) |
| Program adjustment | Manual | Auto-adjust program parameters (v0.9) |

---

## 8. Adaptive Programming (v0.9+)

| Step | Current (v0.5) | Planned |
|------|---------------|---------|
| Program selection | Manual | Auto-chosen based on progress |
| Exercise selection | Fixed program | Swaps plateaued exercises |
| Volume adjustment | Manual (rule suggests) | Auto-regulated based on recovery |
| Deload scheduling | Manual (rule triggers) | Auto-inserted deload weeks |
| User role | User decides | User approves AI decisions |

---

## Current Experience Gap Analysis

| Step | Maturity | Gap |
|------|----------|-----|
| Opening | ✅ v0.5 | — |
| Starting workout | ✅ v0.5 | Equipment guidance missing |
| Live coaching | ✅ v0.5 | Rest timer, form tips, fatigue alerts missing |
| Workout summary | ✅ v0.5 | Nutrition/recovery nudge missing |
| Weekly review | ⏳ v0.6 | Generator exists, UI not wired |
| Daily intelligence | ✅ v0.5 | Natural language explanations missing |
| Mesocycle review | ❌ v0.7 | Not started |
| Adaptive programming | ❌ v0.9 | Not started |
