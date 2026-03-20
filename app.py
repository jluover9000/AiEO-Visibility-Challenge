import streamlit as st
import asyncio
from datetime import datetime, timezone
import pandas as pd

from services.auth_service import check_password
from services.file_handler import (
    parse_uploaded_files,
    validate_files,
    extract_persona,
    load_persona,
    remove_persona_header,
    extract_scoring_prompt_name,
    load_scoring_prompt,
    remove_scoring_prompt_header,
)
from services.llm_service import OpenAIAgent, GeminiAgent, ClaudeAgent
from services.logger_service import create_downloadable_json
from services.scoring_service import score_all_responses
from rag.retrieval import retrieve_context


st.set_page_config(page_title="Multi-LLM Prompt Tester", layout="wide")

if not check_password():
    st.stop()


st.title("Multi-LLM Prompt Tester")
st.write(
    "Upload .md files to test prompts across OpenAI, Gemini, and Claude simultaneously."
)

st.markdown("---")

uploaded_files = st.file_uploader(
    "Upload Markdown Files (.md)",
    type=["md"],
    accept_multiple_files=True,
    help="Select one or more .md files. Each file will be sent to all three LLMs.",
)

if uploaded_files:
    st.success(f"Uploaded {len(uploaded_files)} file(s)")

    for file in uploaded_files:
        st.write(f"- {file.name}")

    if st.button("Process Prompts", type="primary"):
        prompts = parse_uploaded_files(uploaded_files)

        if not prompts:
            st.error("No valid .md files found.")
            st.stop()

        if "results" not in st.session_state:
            st.session_state.results = {
                "session_id": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "prompts": [],
            }

        for idx, prompt_data in enumerate(prompts):
            st.markdown("---")
            st.subheader(f"{prompt_data['filename']}")

            with st.expander("View Prompt Content"):
                st.code(prompt_data["content"], language="markdown")

            persona_name = extract_persona(prompt_data["content"])
            persona_content = load_persona(persona_name) if persona_name else None

            if persona_name:
                if persona_content:
                    st.info(f"Using Persona: **{persona_name}**")
                else:
                    st.warning(f"Persona '{persona_name}' not found. Proceeding without persona.")
                    persona_content = None

            scoring_prompt_name = extract_scoring_prompt_name(prompt_data["content"])
            scoring_system_prompt = load_scoring_prompt(scoring_prompt_name) if scoring_prompt_name else None

            if scoring_prompt_name:
                if scoring_system_prompt:
                    st.info(f"Using Scoring Prompt: **{scoring_prompt_name}**")
                else:
                    st.warning(f"Scoring prompt '{scoring_prompt_name}' not found. Using default scoring criteria.")

            clean_prompt = remove_persona_header(prompt_data["content"])
            clean_prompt = remove_scoring_prompt_header(clean_prompt)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### OpenAI")
                openai_container = st.empty()
                openai_status = st.empty()

            with col2:
                st.markdown("### Gemini")
                gemini_container = st.empty()
                gemini_status = st.empty()

            with col3:
                st.markdown("### Claude")
                claude_container = st.empty()
                claude_status = st.empty()

            openai_agent = OpenAIAgent()
            gemini_agent = GeminiAgent()
            claude_agent = ClaudeAgent()

            state = {
                "openai_text": "",
                "gemini_text": "",
                "claude_text": "",
                "openai_result": None,
                "gemini_result": None,
                "claude_result": None,
            }

            async def stream_openai():
                openai_status.info("Processing...")
                generator = openai_agent.generate_response(clean_prompt, persona_content)
                try:
                    async for update in generator:
                        if update.get("done"):
                            state["openai_result"] = update.get("result")
                            if state["openai_result"]:
                                openai_status.success(
                                    f"Complete ({state['openai_result']['duration_seconds']}s)"
                                )
                        else:
                            state["openai_text"] += update.get("chunk", "")
                            openai_container.markdown(state["openai_text"])
                except Exception as e:
                    openai_status.error(f"❌ Error: {str(e)}")

            async def stream_gemini():
                gemini_status.info("Processing...")
                generator = gemini_agent.generate_response(clean_prompt, persona_content)
                try:
                    async for update in generator:
                        if update.get("done"):
                            state["gemini_result"] = update.get("result")
                            if state["gemini_result"]:
                                gemini_status.success(
                                    f"Complete ({state['gemini_result']['duration_seconds']}s)"
                                )
                        else:
                            state["gemini_text"] += update.get("chunk", "")
                            gemini_container.markdown(state["gemini_text"])
                except Exception as e:
                    gemini_status.error(f"❌ Error: {str(e)}")

            async def stream_claude():
                claude_status.info("Processing...")
                generator = claude_agent.generate_response(clean_prompt, persona_content)
                try:
                    async for update in generator:
                        if update.get("done"):
                            state["claude_result"] = update.get("result")
                            if state["claude_result"]:
                                claude_status.success(
                                    f"Complete ({state['claude_result']['duration_seconds']}s)"
                                )
                        else:
                            state["claude_text"] += update.get("chunk", "")
                            claude_container.markdown(state["claude_text"])
                except Exception as e:
                    claude_status.error(f"❌ Error: {str(e)}")

            async def run_all():
                await asyncio.gather(stream_openai(), stream_gemini(), stream_claude())

            asyncio.run(run_all())

            st.markdown("---")
            st.markdown("### Scoring Responses")

            try:
                rag_context = retrieve_context(clean_prompt)
            except Exception as e:
                st.warning(f"RAG retrieval failed, scoring without context: {str(e)}")
                rag_context = ""

            if rag_context:
                chunk_count = len(rag_context.split("\n\n"))
                st.caption(f"Retrieved {chunk_count} context chunk(s) from the knowledge base.")

            with st.spinner("Sending responses to GPT for evaluation..."):
                try:
                    scores = asyncio.run(
                        score_all_responses(
                            question=clean_prompt,
                            responses={
                                "openai": state["openai_result"] or {},
                                "gemini": state["gemini_result"] or {},
                                "claude": state["claude_result"] or {},
                            },
                            scoring_system_prompt=scoring_system_prompt,
                            context=rag_context or None,
                        )
                    )
                except Exception as e:
                    st.error(f"Scoring failed: {str(e)}")
                    scores = None

            if scores:
                st.subheader("Score Comparison")

                score_data = {
                    "Model": ["OpenAI", "Gemini", "Claude"],
                    "Score": [
                        f"{scores['openai'].get('score', 0):.1f}" if isinstance(scores["openai"].get("score"), (int, float)) else "N/A",
                        f"{scores['gemini'].get('score', 0):.1f}" if isinstance(scores["gemini"].get("score"), (int, float)) else "N/A",
                        f"{scores['claude'].get('score', 0):.1f}" if isinstance(scores["claude"].get("score"), (int, float)) else "N/A",
                    ],
                    "Rank": [
                        f"#{scores['openai'].get('rank', 'N/A')}",
                        f"#{scores['gemini'].get('rank', 'N/A')}",
                        f"#{scores['claude'].get('rank', 'N/A')}",
                    ],
                }

                df = pd.DataFrame(score_data)

                def highlight_winner(row):
                    model_name = row["Model"].lower()
                    if model_name == scores.get("winner", "").lower():
                        return ["background-color: #90EE90"] * len(row)
                    return [""] * len(row)

                styled_df = df.style.apply(highlight_winner, axis=1)
                st.dataframe(styled_df, width="stretch", hide_index=True)

                winner = scores.get("winner", "openai")
                winner_score = scores.get(winner, {}).get("score", "N/A")
                st.success(
                    f"Winner: **{winner.upper()}** with score **{winner_score}/100**"
                )

                st.markdown("#### Justifications")
                for model in ["openai", "gemini", "claude"]:
                    score_info = scores.get(model, {})
                    rank = score_info.get("rank", "N/A")
                    score = score_info.get("score", "N/A")
                    justification = score_info.get(
                        "justification", "No justification available"
                    )

                    with st.expander(
                        f"{model.upper()} - Score: {score}/100, Rank: #{rank}"
                    ):
                        st.write(justification)

                if scoring_prompt_name:
                    st.info(f"**Scoring Prompt:** {scoring_prompt_name}")

            prompt_result = {
                "filename": prompt_data["filename"],
                "question": clean_prompt,
                "persona": persona_name,
                "scoring_prompt": scoring_prompt_name,
                "rag_context": rag_context or None,
                "responses": {
                    "openai": {
                        **(
                            state["openai_result"]
                            or {"error": "Failed to generate response"}
                        ),
                        **(
                            {
                                "score": scores["openai"]["score"],
                                "rank": scores["openai"]["rank"],
                                "justification": scores["openai"]["justification"],
                            }
                            if scores
                            else {}
                        ),
                    },
                    "gemini": {
                        **(
                            state["gemini_result"]
                            or {"error": "Failed to generate response"}
                        ),
                        **(
                            {
                                "score": scores["gemini"]["score"],
                                "rank": scores["gemini"]["rank"],
                                "justification": scores["gemini"]["justification"],
                            }
                            if scores
                            else {}
                        ),
                    },
                    "claude": {
                        **(
                            state["claude_result"]
                            or {"error": "Failed to generate response"}
                        ),
                        **(
                            {
                                "score": scores["claude"]["score"],
                                "rank": scores["claude"]["rank"],
                                "justification": scores["claude"]["justification"],
                            }
                            if scores
                            else {}
                        ),
                    },
                },
                "winner": scores.get("winner") if scores else None,
            }
            st.session_state.results["prompts"].append(prompt_result)

        st.markdown("---")
        st.success("All prompts processed!")

        st.subheader("Download Results")

        col1, col2 = st.columns(2)

        with col1:
            json_data = create_downloadable_json(st.session_state.results)
            st.download_button(
                label="Download JSON Log",
                data=json_data,
                file_name=f"llm_logs_{st.session_state.results['session_id']}.json",
                mime="application/json",
            )

else:
    st.info("Upload one or more .md files to get started")

st.markdown("---")
st.caption(
    "Multi-LLM Prompt Tester | Powered by OpenAI, Google Gemini, and Anthropic Claude"
)
