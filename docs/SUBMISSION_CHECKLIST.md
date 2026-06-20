# FinGuard AI Submission Checklist

## Required deliverables

- [x] Source code for data generation, training, inference, API, and dashboard.
- [x] Dependency and environment files.
- [x] Generated synthetic dataset and ready-to-run model artifacts.
- [x] Automated tests and smoke test.
- [x] Technical documentation in Markdown and submission-ready document format.
- [x] Editable presentation deck.
- [x] Demo recording script and shot list.
- [ ] Final narrated `FinGuard_AI_Demo.mp4` reviewed by the team.
- [ ] Hosted demo URL added only in the submission portal.

## Final content checks

- [ ] Team name and member names are added to the cover slide if required.
- [ ] Competition name, round, deadline, and file-size limits are confirmed.
- [ ] Market figures are refreshed from current NPCI and RBI sources.
- [ ] The synthetic-data limitation is visible; metrics are not presented as bank-production results.
- [ ] No claim says the tool proves fraud or automatically blocks a payment.
- [ ] No API key, `.env`, phone number, UPI PIN, or bank identifier is present.
- [ ] The Groq model name is available in the target account; update `GROQ_MODEL` if necessary.

## Technical checks

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m uvicorn api:app --port 8000
```

- [ ] `/health` reports `model_ready: true`.
- [ ] Suspicious manual check is flagged and explanation matches visible SHAP factors.
- [ ] English and Hindi output both render.
- [ ] `/docs` loads and `/predict` plus `/explain` succeed.
- [ ] Docker image builds in the intended deployment environment.

## Packaging

- [ ] Exclude `.venv`, `.env`, caches, and local render intermediates.
- [ ] Include `data/`, `models/`, `docs/`, `outputs/`, and all source/config/test files.
- [ ] Open the PPTX and DOCX on a second machine.
- [ ] Play the MP4 from start to finish with sound.
- [ ] Upload files before the deadline and verify each upload is downloadable.
