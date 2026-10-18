# Walkthrough guide

## Actual live OpenAI walkthrough

`live_walkthrough.mp4` records the actual Gradio interface making OpenAI API calls, with the LIVE OPENAI banner visible. It combines the services/reflection scene with the subsequent multi-turn lead, feedback, and unknown-question scenes. Idle time between the two recording segments is trimmed; replies and tool requests are actual app output. There is no narration, and all customer details are fictional.

The companion `live_transcript.json` preserves a separate actual API test run: all six scenarios passed, including services, missing email, successful lead recording on the next turn, feedback, unpublished certification, and exact-price restraint. `live_ui_reflections.jsonl` preserves actual drafts and revised replies from the browser demonstration. A services reply was visibly revised to include the published written-scope/custom-quote process. This is an observed refinement; the separate seeded $999 example in the notebook remains labeled synthetic.

The live notebook UI defaults to `RUN_LIVE=True`. Your private key is needed to rerun the demonstration; it is excluded from the ZIP and Git.

## Additional offline walkthrough

`offline_walkthrough.mp4` is an actual screen recording of the Gradio app (1600 x 1000, 15 fps, approximately 2 minutes 32 seconds). Its banner explicitly identifies **OFFLINE FIXTURE** mode. It has no narration. The app's code is identical in live mode; offline mode injects a deterministic SDK-shaped client in place of the provider. This video demonstrates application control flow, not live LLM performance.

The recording shows:

1. The business identity, reflection toggle, and offline disclosure.
2. A services question routed to `general_question`, with the draft and revised reply visible.
3. A customer supplying a name and project notes. Lina asks for the missing email.
4. The same customer supplying an email. `record_customer_interest` receives the three fields and writes a real local JSONL record.
5. Explicit feedback routed to `feedback_and_unanswered`, with `record_feedback` called.
6. A question about an unpublished certification. The general path invokes `record_feedback` and returns an uncertainty response.

The JSON widget may collapse nested results; click the arrow beside `result` to inspect `ok`, `record_id`, and `status`. Saved receipts are also in `offline_transcript.json`. The companion screenshots capture lead collection, feedback, and the unknown question.

The notebook's synthetic reflection example deliberately seeds a fictitious $999 project quote and logs its replacement with the published custom-quote policy. It is labeled synthetic and is not presented as an observed live-model error. Most valid drafts remain unchanged; `changed=false` is a legitimate review result.

To reproduce the live demonstration, configure your key in `.env`, start `python app.py`, and follow the same sequence. Never show the key file in a recording. Verification details are documented in `../VERIFICATION.md`.
