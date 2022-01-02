from dotenv import load_dotenv
from time import sleep
import openai
import streamlit as st
from pathlib import Path
import os
import json
import logging

from constants import *
from language import language_mapper
from knowledge_processing import get_knowledge_file_options, convert_txt2jsonl, update_knowledge_base, knowledge_available_online

load_dotenv()
language_definition = language_mapper.get(os.getenv("SODISAPP_LANGUAGE", "DE"), "DE")

def main() -> None:
    st.set_page_config(page_title=language_definition.get("app_title"), page_icon = FAVICON, initial_sidebar_state = 'auto')

    st.image(LOGO_IMG.resize( [int(0.5 * s) for s in LOGO_IMG.size]), use_column_width=True)
    
    st.header(language_definition.get("Questions"))
    question = st.text_area("",value="Was ist denn Aktion Sodis?", help="")
    button = st.button(language_definition.get("app_title"))
    answer_placeholder = st.empty()
    
    with st.expander(language_definition.get("Settings")):
        col1, col2 = st.columns(2)
        kf_name = col1.selectbox(language_definition.get("knowledge_source_prompt"), get_knowledge_file_options())
        uploaded_file = col2.file_uploader(language_definition.get("upload_knowledge_prompt"))
        getfile = st.button(language_definition.get("Reading"))
        
        col1, col2 = st.columns(2)
        openai_org_key = col1.text_area(language_definition.get("openai_orgid."),value=os.getenv("OPENAI_ORG_ID"), height=18)
        # openai_secret = os.getenv("OPENAI_SECRET") 
        openai_secret = col2.text_area(language_definition.get("openai_key"), height=18)
        
        temperature = st.slider(language_definition.get("sampling_temperature"), min_value=0.0, max_value=2.0, value=0.1, step=0.01, help=language_definition.get("sampling_temperature_help"))
        max_tokens = st.slider(language_definition.get("max_tokens"), min_value=8, max_value=500, value=100, step=1, help=language_definition.get("max_tokens_help"))
        max_rerank = st.slider(language_definition.get("max_rerank"), min_value=50, max_value=500, value=300, step=1, help=language_definition.get("max_rerank_help"))

    # Set filepaths for knowledge bank
    knowledge_jsonl = Path(KNOWLEDGE_FILEPATH, JSONLNAME)
    knowledge_txt = Path(kf_name)
    connect_openai_api(openai_secret, openai_org_key)
    logging.info(f"Connecting to openai-api. With openai_org_key={openai_org_key}.")

    if uploaded_file:
        string_data = uploaded_file.read()
        lines = [{"text": line.decode("utf-8")} for line in string_data.splitlines() if line]
        # Convert to a list of JSON strings
        json_lines = [json.dumps(l) for l in lines]

        # Join lines and save to .jsonl file
        json_data = '\n'.join(json_lines)
        
        with open(knowledge_jsonl, 'w') as f:
            f.write(json_data)
        with st.spinner(text=language_definition.get('upload_wait')):   
            update_knowledge_base_and_sleep(knowledge_jsonl)

    if getfile:
        if not uploaded_file:
            convert_txt2jsonl(knowledge_jsonl, knowledge_txt)
        with st.spinner(text=language_definition.get('upload_wait')):   
            update_knowledge_base_and_sleep(knowledge_jsonl)

    # Knowledge engine question and answer
    if button:
        can_query = True

        if can_query:
            try:
                with st.spinner(text=language_definition.get("inference_wait")):
                    response_json = openai.Answer.create(
                        search_model="ada",
                        model="davinci",
                        question=question,
                        temperature=temperature,
                        file=openai.File.list()['data'][-1]['id'],  # Get latest file
                        examples_context= EXAMPLES_CONTEXT,
                        examples=EXAMPLES,
                        max_rerank=max_rerank,
                        max_tokens=max_tokens,
                        stop=["\n", "<|endoftext|>"]
                    )
                        
                # Return answer to UI
                answer_placeholder.markdown(response_json["answers"][0], unsafe_allow_html=False)
                
            except Exception as ex:
                if isinstance(ex, openai.error.InvalidRequestError):
                    answer_placeholder.error(f"{language_definition.get('inference_error')}: ({ex.user_message}).")
                elif isinstance(ex, openai.error.AuthenticationError):
                    answer_placeholder.error(f"{language_definition.get('authentication_error')}: ({ex.user_message}).")

def connect_openai_api(openai_secret, openai_org_key):
    """API call to openAI."""
    openai.organization = openai_org_key
    openai.api_key = openai_secret

def update_knowledge_base_and_sleep(knowledge_jsonl):
    try:
        update_knowledge_base(knowledge_jsonl, knowledge_available_online)
        sleep(5)
    except openai.error.InvalidRequestError as ex:
        st.error(f"{language_definition.get('upload_error')}: ({ex.user_message}).")
            
if __name__ == "__main__":
    main()
