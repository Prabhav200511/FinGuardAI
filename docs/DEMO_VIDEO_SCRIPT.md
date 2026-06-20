# FinGuard AI Demo Video Script

**Target length:** 2 minutes 30 seconds  
**Format:** 1080p landscape, clear narration, no API keys or personal data on screen

## Before recording

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m uvicorn api:app --port 8000
```

Use a clean browser window at 100% zoom. Keep the dashboard on the Live Feed tab before recording.

## Shot list and narration

| Time | Screen action | Suggested narration |
|---:|---|---|
| 0:00-0:12 | Show title and four session metrics. | "FinGuard AI detects suspicious UPI payments and tells the user exactly why they were flagged, in English or Hindi." |
| 0:12-0:28 | Scroll through the seeded Live Feed. Point to risk and status columns. | "Every transaction is scored from zero to one hundred using amount, time, merchant category, device, location, velocity, and merchant history." |
| 0:28-0:45 | Click **Fraud Txn**, then open **Fraud Alerts**. | "This simulated transaction is immediately flagged. The alert preserves the transaction context and the calibrated model score." |
| 0:45-1:08 | Show the SHAP bar chart and click **Get AI Explanation**. | "SHAP identifies the strongest contributors. The explanation service converts those same factors into a short action-oriented message, so the text remains grounded in the model." |
| 1:08-1:25 | Switch language to Hindi and generate the Hindi explanation. | "The same evidence is rendered in Hindi through the language-specific prompt. If Groq is unavailable, a local bilingual fallback keeps the demo functional." |
| 1:25-1:45 | Use Manual Check with amount 45000, hour 2, new device, 850 km, velocity 2, new merchant. | "Bank analysts can reproduce a case manually. This transaction scores around ninety and explains the amount, device change, and location jump." |
| 1:45-2:02 | Open Analytics and show volume, attack pattern, distribution, and heatmap. | "The operations view summarizes alert volume, risk distribution, fraud patterns, and high-risk time and amount combinations." |
| 2:02-2:18 | Show `http://localhost:8000/docs`, expand `/explain`. | "FastAPI exposes the same pipeline through documented predict and explain endpoints, ready to integrate with an existing bank fraud system." |
| 2:18-2:30 | Return to the alert explanation and finish on the FinGuard AI title. | "FinGuard AI makes fraud detection transparent, bilingual, and actionable, especially for users and small merchants who cannot afford a black-box warning." |

## Recording checklist

- Hide bookmarks, notifications, usernames, and terminal secrets.
- Do not display `.env`, UPI PINs, account data, email, or phone numbers.
- Use the seeded feed so the opening screen is populated.
- Pause briefly after each click; avoid rapid cursor movement.
- Confirm Hindi glyphs render correctly.
- Export as H.264 MP4, 1920x1080, 30 fps, with readable audio.
- Add captions for accessibility.
- Name the final file `FinGuard_AI_Demo.mp4`.

## Backup demo path

If the network or Groq is unavailable, continue normally. The dashboard displays "Offline explainability" and produces feature-grounded English and Hindi explanations. This is expected behavior, not an error.
