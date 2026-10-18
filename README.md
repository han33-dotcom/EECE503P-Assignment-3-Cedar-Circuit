# Cedar & Circuit - Agent-Powered Business Assistant

**Hassan Nasrallah | EECE 503P/798S - Agentic Systems | Assignment C3**

Lina represents a fictional Beirut automation studio. She answers from an invented PDF/TXT business profile, routes each message, collects leads over several turns, and uses two model-callable logging tools. A Gradio `ChatInterface` displays the conversation alongside route, tool receipts, and reflection results.

**Repository:** [han33-dotcom/EECE503P-Assignment-3-Cedar-Circuit](https://github.com/han33-dotcom/EECE503P-Assignment-3-Cedar-Circuit) (private).

**Start here:** [executed notebook](business_bot/business_agent.ipynb), [live demo video](demo/live_walkthrough.mp4), [business profile](business_bot/me/about_business.pdf), and [verification results](VERIFICATION.md).

## Run locally

Use Python 3.10 or later. Open a terminal in this submission folder:

```powershell
cd business_bot
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Edit the private `business_bot/.env` file and add your own key:

```dotenv
OPENAI_API_KEY=your-own-key
OPENAI_MODEL=gpt-4o-mini
```

Then run:

```powershell
.venv\Scripts\python app.py
```

Open `http://127.0.0.1:7860`. The default mode calls OpenAI and incurs API usage. The model can be changed through `OPENAI_MODEL`; choose a model supporting Chat Completions, function tools, and JSON responses. The app reports authentication/network problems instead of silently switching to a fixture.

For an explicit, no-key application demonstration:

```powershell
.venv\Scripts\python app.py --offline
```

The interface labels this **OFFLINE FIXTURE**. Its scripted replies and SDK-shaped tool requests exercise the actual dispatcher and logging code, but are not an LLM. See `VERIFICATION.md` for the precise verification status.

On macOS/Linux use `.venv/bin/python` in place of `.venv\Scripts\python`.

## Notebook

`business_bot/business_agent.ipynb` contains the full implementation with clearly labeled persona and instructions, architecture notes, router examples, tool contracts, executed offline examples, a synthetic reflection correction, and actual live API evidence. Open it in Jupyter with the working directory set to `business_bot`, then run the cells in order. The UI cell in section 7 defaults to `RUN_LIVE=True` and uses your private key. Set it to `False` to select the labeled fixture. The installation cell installs the pinned app dependencies into the current kernel.

For Colab, upload the submission ZIP (which excludes `.env`), then extract it:

```python
from google.colab import files
import zipfile, os
uploaded = files.upload()  # select Hassan_Nasrallah_EECE503P_Assignment_3.zip
zip_name = next(name for name in uploaded if name.endswith('.zip'))
with zipfile.ZipFile(zip_name) as z:
    z.extractall('/content/c3')
os.chdir('/content/c3/Hassan_Nasrallah_EECE503P_Assignment_3/business_bot')
```

Open/upload `business_agent.ipynb` and run it with this same directory selected in the runtime. Configure `OPENAI_API_KEY` using an environment variable or a private `.env` before live mode. On Colab change the launch statement in section 7 to `ui.launch(share=True)` to get a temporary public link while the runtime is active. A local `.env.example` is supplied for creating `.env` after extraction.

## Demonstration sequence

1. Ask **What services do you offer?** The general route uses approved business context.
2. Clear the chat. Say **I am Samira Mansour. I am interested in automating order tracking.** Lina requests the missing email.
3. Reply **samira@example.com**. `record_customer_interest(email, name, message)` saves a fictional lead and returns a receipt.
4. Clear the chat. Say **Feedback: your contact form is broken.** The feedback route forces a model-issued `record_feedback(question)` call.
5. Clear the chat. Ask **Do you hold ISO 27001 certification?** This fact is absent. The general route can call the feedback tool and acknowledge uncertainty.
6. Inspect the trace and `logs/reflections.jsonl` for original and revised replies. The notebook also includes a clearly labeled synthetic bad-price draft to demonstrate a visible correction.

Watch `demo/live_walkthrough.mp4` for the actual Gradio app calling OpenAI. The saved `demo/live_transcript.json` contains six passing API scenarios, original replies, tool arguments and receipts, and reflection results; notebook section 9 displays that evidence. An additional `offline_walkthrough.mp4` is explicitly labeled as scripted fixture mode. Example identities are invented. See `demo/WALKTHROUGH.md` for the accompanying explanation.

## Tool contracts and routing

`TOOL_CONTRACTS` documents name, description, input JSON Schema, and success/error output shapes in the style of MCP tool definitions. This app does not run an MCP server. `TOOLS` adapts these contracts to OpenAI function definitions.

| Tool | Required parameters | Success output | Effect |
| --- | --- | --- | --- |
| `record_customer_interest` | `email`, `name`, `message` (strings) | `ok`, `record_id`, `status=interest_recorded` | Append to `logs/leads.jsonl` and print receipt |
| `record_feedback` | `question` (string) | `ok`, `record_id`, `status=feedback_recorded` | Append to `logs/feedback.jsonl` and print receipt |

Both tools return `ok=false` and an error on validation/storage failure. The dispatcher rejects unknown tool names, malformed JSON, extra fields, and lead values absent from the user's messages. Duplicate calls within a turn reuse their receipt.

The heuristic router gives feedback/complaints priority, then detects leads using interest phrases, emails, or a pending request for contact fields. Other messages follow the general path. Unknown facts are detected by the model in the general path and logged through `record_feedback`; the trace preserves the original route and actual tool calls. Ambiguous/mixed intents can be misclassified.

The live loop passes the system prompt, up to 16 recent user/assistant messages (20,000 characters), the new user input, and both tools to `client.chat.completions.create`. Model tool requests are dispatched and their results returned using matching `tool_call_id` values. The model then produces the final draft. At most five responses are allowed per tool loop.

## Reflection bonus

An optional second model call checks the draft against the same business context and instructions. It returns JSON with `reply` and `needs_feedback`. The original draft, revised reply, and change flag are logged. If review detects an unlogged unknown fact, the agent requests a model-issued feedback call. Invalid review JSON retains the original draft with a diagnostic. Reflection is an additional check, not a guarantee of correctness; it adds latency and API usage.

## Files

```text
business_bot/
  me/about_business.pdf       Fictional business profile
  me/business_summary.txt     Few-paragraph summary required by checklist
  me/summary.txt              Identical alias required by task wording
  business_agent.ipynb        Complete notebook with saved example outputs
  agent.py                   Matching reusable implementation
  app.py                     Gradio launch entry point
  .env                       Private local key configuration; ignored by Git
  .env.example               Public configuration template
  requirements.txt           Pinned app dependencies
  requirements-dev.txt       Additional verification dependencies
  tests/test_agent.py         Offline and real-SDK HTTP-mock checks
demo/                        Walkthrough and verification evidence
README.md                    Setup and design explanation
VERIFICATION.md              Actual checks and outstanding submission steps
```

## GitHub submission and optional hosting

The submission repository is [han33-dotcom/EECE503P-Assignment-3-Cedar-Circuit](https://github.com/han33-dotcom/EECE503P-Assignment-3-Cedar-Circuit). It is private; grant your instructor access before submitting its URL through the course's process. Both demo videos are included under `demo/`. Keep `.env`, runtime `logs/`, and virtual environments out of Git. The `.gitignore` and packaged ZIP exclude these private/runtime files. GitHub publication does not submit the assignment to the course platform.

For the optional Hugging Face Spaces bonus, create a Gradio Space and upload the contents of `business_bot` at the Space root. Store `OPENAI_API_KEY` in Space Secrets and use `GRADIO_SERVER_NAME=0.0.0.0`, `GRADIO_SERVER_PORT=7860`. Do not upload `.env` or private logs. Persistent production storage and access controls would need additional work; no hosted deployment is claimed here.

## References

- [OpenAI function-calling guide](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI Python Chat Completions reference](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create)
- [GPT-4o mini model documentation](https://developers.openai.com/api/docs/models/gpt-4o-mini)
- [Gradio ChatInterface documentation](https://www.gradio.app/docs/gradio/chatinterface)

The modern OpenAI client replaces the older `openai.ChatCompletion` spelling in the handout while preserving the requested chat-plus-tools interaction. Business facts come exclusively from the invented local documents.
