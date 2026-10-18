# Verification and submission status

Prepared on **18 October 2026** for Hassan Nasrallah, EECE 503P/798S.

## Checks actually completed

| Check | Result |
| --- | --- |
| Business PDF | Two pages rendered and visually inspected; readable and unclipped |
| Business context | Both TXT and PDF load into the system prompt |
| Notebook | All 8 code cells executed successfully; saved outputs include actual API evidence; notebook schema validated |
| Automated checks | 26 passed; see `demo/automated_checks.txt` |
| Three router paths | Verified in notebook and application examples |
| Multi-turn lead | Missing email requested, supplied next turn, fictional lead saved |
| Lead and feedback tools | Real JSONL writes and success receipts verified |
| OpenAI SDK contract | Actual SDK parsed mocked HTTP tool responses; matching tool result IDs verified |
| Reflection | Draft/revised logs verified; synthetic bad-price correction explicitly labeled |
| Gradio | App launched in browser and chat interactions verified |
| Walkthrough | Actual app screen recording converted to MP4 and a decoded frame inspected |
| Package | ZIP excludes `.env`, private runtime logs, caches, and virtual environments |

## Live API status

**Passed: 6 of 6 actual API scenarios with `gpt-4o-mini`.** The configured private key successfully authenticated. Services were answered from context; a name and project description were retained while Lina requested the missing email; the next turn triggered a successful model-issued `record_customer_interest` call. Explicit feedback and an unpublished certification question each triggered successful `record_feedback` calls. An exact-price request received the published custom-quote limitation without an invented amount. Reflection ran on all six turns.

The original live replies, routes, tool arguments, receipts, and reflection results are saved in `demo/live_transcript.json` and displayed in notebook section 9. This small end-to-end check is distinct from the 26 automated fixture/HTTP-mock tests. Model responses can vary on reruns.

The initial live run revealed redundant requests for optional project details. The final instructions clarify that one sentence identifying a requested task is sufficient notes. The repeated live check passed all six scenarios after that change.

## Assignment checklist mapping

| Requirement | Location |
| --- | --- |
| Business name, mission, services, team, value proposition | `business_bot/me/about_business.pdf` and `business_summary.txt` |
| Summary filename ambiguity | Both `me/business_summary.txt` and identical `me/summary.txt` provided |
| Clearly labeled persona and instructions | Notebook section 2; `PERSONA` / `INSTRUCTIONS` in `agent.py` |
| Simple three-intent router | `route_message`; notebook section 4 |
| `record_customer_interest(email, name, message)` | `agent.py`; notebook tool definitions |
| `record_feedback(question)` | `agent.py`; notebook tool definitions |
| MCP-style schemas / expected outputs | `TOOL_CONTRACTS`; notebook section 4 |
| Persona + rules + TXT + PDF system prompt | `make_system_prompt` |
| History + tools + model-issued calls + returned tool results | `BusinessAgent.respond` |
| OpenAI API implementation | `client.chat.completions.create`; configurable model |
| Gradio ChatInterface | `build_ui`; `app.py`; notebook section 7 |
| Private API key file | Local `.env`, ignored by Git and excluded from ZIP |
| Video | `demo/live_walkthrough.mp4` (actual API calls); additional labeled offline walkthrough |
| Reflection bonus | Implemented, with logged drafts and revised replies |
| Hugging Face bonus | Not deployed; setup guidance supplied |

## GitHub repository and course submission

Repository: [han33-dotcom/EECE503P-Assignment-3-Cedar-Circuit](https://github.com/han33-dotcom/EECE503P-Assignment-3-Cedar-Circuit). The repository is private and contains the submission files, including the notebook and actual live walkthrough. The private API key and runtime logs are excluded.

Grant the instructor access to the private repository and submit its URL using the course's instructions. No course-platform submission or Hugging Face deployment was performed. The local submission folder and ZIP remain saved under EECE503P.

## Known limits

The router uses simple heuristics and may misclassify ambiguous/mixed requests. The model and reflection pass can still make mistakes. Memory uses bounded truncation; older facts can be forgotten. Duplicate tool calls are deduplicated within a turn, while repeated submissions in different turns can produce additional records. Logs are local JSONL files, not a production CRM. The assistant records interest and feedback; it does not book appointments, send email, or accept payments.
