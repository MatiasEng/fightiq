# FightIq v2.0 

- [ ] Scheduled scraping pipeline — cron-based, not manual, keeps fight/fighter data current after each UFC event.
- [x] Prediction model — existing Random Forest, plus a documented comparison against XGBoost/LightGBM (ties to Course 2 Week 4 material).
- [ ] Document Comparison between models
- [ ] Containerized backend — FastAPI wrapped in Docker, deployed live (Railway/Render/Fly.io). Moved early in build order — deployment is table stakes, not a late add-on.
- [ ] Frontend — existing Next.js/Tailwind stack: matchup picker, live predictions, model confidence displayed.
- [ ] Public accuracy tracking — model's real prediction record, updated after each event, visible on the site (trust signal).
- [ ] Clean README / case study — problem, architecture, tradeoffs, what you'd improve. This is what gets read, not just the code.


# FigthtIQ v2.1 

- [x] SHAP-based explainability — feature importances computed per prediction, feeding the next item.
- [x] Structured prompting layer (not RAG — corrected terminology) — LLM receives SHAP values + fighter stats as structured context, generates a natural-language explanation of the prediction. Only call it RAG if you actually add retrieval (e.g., vectorized past-fight lookup) — otherwise this is structured prompting with context.
- [x] Tool use — the LLM calls a function that fetches your model's live SHAP output for a given matchup, rather than the explanation being pre-baked — demonstrates real tool-use integration, not a static wrapper.
- [x] Explanation consistency eval — sample ~20 predictions, manually verify the LLM's explanation matches what SHAP actually shows, report a consistency score. Turns "I added an LLM feature" into a real engineering claim.

## Optional 

- [ ] True RAG extension — vector store of historical matchups, retrieved to ground explanations in similar past fights. Real added complexity — only build if you have a concrete reason, not to check a box.
- [ ] Multi-step agent — chain "fetch stats → run prediction → explain" as a tool-calling loop instead of one call. Natural extension of #9 once it's solid.


## Skills to build FightIQ v2 — mapped to what's already discussed

**1. Docker** — containerize the FastAPI backend, deploy via Render's Dockerfile support. Immediate next step, already scoped.

**2. XGBoost / LightGBM** — add as a documented comparison model against your existing Random Forest. Directly extends Course 2 Week 4 (decision trees) material you just finished.

**3. SHAP** — feature importance/explainability library. Feeds both your model comparison (why does XGBoost outperform/underperform RF here) and the LLM explanation layer downstream.

**4. LLM API integration (Anthropic or OpenAI SDK)** — the raw mechanics: authenticated API calls, message format, response parsing. Foundational for everything below.

**5. Structured output / prompting** — getting the LLM to return reliable JSON or fixed-format text you can parse in code, not free-form prose.

**6. Tool use / function calling** — letting the LLM call your own function (e.g., fetch SHAP values for a given matchup) rather than hallucinating an explanation. This is the actual "AI integration" skill, not just calling an API.

**7. LLM output evaluation** — a basic method to check the model's explanations stay factually consistent with the real SHAP values (sample predictions, manual verification, report a consistency rate). Was flagged as a real gap earlier — don't skip it.

**8. CI/CD basics** — automated build/deploy on push (Render and Vercel both support this natively via GitHub integration — worth confirming yours is actually wired up, since this showed up as a high-frequency market skill (29.3% of postings) and it's nearly free to set up if not already done).

**9. Scheduled jobs / cron** — automating the scraping pipeline to run after each UFC event instead of manually, if not already in place from v1.0.

**10. Public accuracy tracking** — not a new technical skill exactly, but requires basic dashboarding/logging of prediction-vs-actual-outcome over time, displayed on the frontend.

**Lower priority / only if scope allows:**
- **Vector databases** (Pinecone, Weaviate, or similar) — only needed if you extend into true RAG (retrieving similar historical fights), which is optional scope per the earlier correction.
- **Agent orchestration** (multi-step tool-calling loops) — natural extension of #6, but only after #6 is solid.

**Sequencing recap, tied to what's already agreed:** Docker first (this week) → confirm CI/CD is wired → XGBoost/SHAP (v2.0 core, ties to material you just finished) → ship and confirm live → LLM layer: API integration → structured output → tool use → evaluation (v2.1, in that order).

This list is deliberately bounded to what FightIQ v2 needs — not a general "AI engineer skill inventory." Want me to break down #1 (Docker) into the actual Dockerfile now, or keep this as the reference list for now?
