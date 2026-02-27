import streamlit as st
import asyncio
from datetime import datetime

from services.auth_service import check_password
from services.file_handler import parse_uploaded_files, validate_files
from services.llm_service import OpenAIAgent, GeminiAgent, ClaudeAgent
from services.logger_service import create_downloadable_json


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
                "session_id": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "prompts": [],
            }

        for idx, prompt_data in enumerate(prompts):
            st.markdown("---")
            st.subheader(f"{prompt_data['filename']}")

            with st.expander("View Prompt Content"):
                st.code(prompt_data["content"], language="markdown")

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
                generator = openai_agent.generate_response(prompt_data["content"])
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
                generator = gemini_agent.generate_response(prompt_data["content"])
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
                generator = claude_agent.generate_response(prompt_data["content"])
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

            prompt_result = {
                "filename": prompt_data["filename"],
                "content": prompt_data["content"],
                "responses": {
                    "openai": state["openai_result"]
                    or {"error": "Failed to generate response"},
                    "gemini": state["gemini_result"]
                    or {"error": "Failed to generate response"},
                    "claude": state["claude_result"]
                    or {"error": "Failed to generate response"},
                },
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
