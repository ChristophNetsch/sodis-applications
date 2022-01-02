from dotenv import load_dotenv
from time import sleep
import openai
import streamlit as st
from pathlib import Path
import os
import json
import logging

from constants import *
from knowledge_processing import get_knowledge_file_options, convert_txt2jsonl, update_knowledge_base, knowledge_available_online

load_dotenv()

def main() -> None:
    # API call to openAI
    logging.info(f"Connecting to OPENAI API via organization key {os.getenv('OPENAI_ORGANIZATION')}.")
    openai.organization = os.getenv("OPENAI_ORG_ID") 
    openai.api_key = os.getenv("OPENAI_SECRET")

    st.set_page_config(page_title='Frag Nico-Mario', page_icon = FAVICON, layout = 'wide', initial_sidebar_state = 'auto')

    st.image(LOGO_IMG.resize( [int(0.5 * s) for s in LOGO_IMG.size]), use_column_width=True)
    st.header('Wähle eine Wissensquelle.')

    knowledge_base_updated = False
    kf_name = st.selectbox('Wähle eine hinterlegte Wissensquelle:', get_knowledge_file_options())
    uploaded_file = st.file_uploader("Oder wähle eine eigene Wissensquelle (TXT-Datei):")

    getfile = st.button("Einlesen..")

    question = st.text_area('Was willst du wissen?')
    button = st.button("Frag Nico-Mario!")

    # Set filepaths for knowledge bank
    knowledge_jsonl = Path(KNOWLEDGE_FILEPATH, JSONLNAME)
    knowledge_txt = Path(KNOWLEDGE_FILEPATH, kf_name)

    if uploaded_file:
        string_data = uploaded_file.read()
        lines = [{"text": line} for line in string_data.splitlines() if line]
        # Convert to a list of JSON strings
        json_lines = [json.dumps(l) for l in lines]

        # Join lines and save to .jsonl file
        json_data = '\n'.join(json_lines)
        
        with open(knowledge_jsonl, 'w') as f:
            f.write(json_data)
        
        with st.spinner(text="Wissensquelle wird eingelesen..."):
            update_knowledge_base(knowledge_jsonl, knowledge_available_online)
        knowledge_base_updated = True

    if getfile:
        if not uploaded_file:
            convert_txt2jsonl(knowledge_jsonl, knowledge_txt)
        with st.spinner(text="Wissensquelle wird eingelesen..."):   
            update_knowledge_base(knowledge_jsonl, knowledge_available_online)
        knowledge_base_updated = True

    # Knowledge engine question and answer
    if button:
        can_query = True
        if not knowledge_base_updated:
            if knowledge_jsonl.exists():
                with st.spinner(text="Wissensquelle wird eingelesen..."):   
                    update_knowledge_base(knowledge_jsonl, knowledge_available_online)
                    sleep(5)
            else:
                st.error("Keine Wissensquelle online hinterlegt. Bitte wähle eine Wissensquelle aus oder lade eine eigene hoch.")
                can_query = False    
        
        if can_query:
            with st.spinner(text="Nico-Mario denkt nach..."):
                response_json = openai.Answer.create(
                    search_model="ada",
                    model="davinci",
                    question=question,
                    file=openai.File.list()['data'][-1]['id'],  # Get latest file
                    examples_context= "In 2017, U.S. life expectancy was 78.6 years." ,
                    examples=[["What is human life expectancy in the United States?", "78 years."]],
                    max_rerank=int(os.getenv("OPENAI_MAX_RERANK")),
                    max_tokens=int(os.getenv("OPENAI_MAX_TOKENS")),
                    stop=["\n", "<|endoftext|>"]
                )
            # Return answer to UI
            st.markdown(response_json["answers"][0], unsafe_allow_html=False)
            
if __name__ == "__main__":
    main()
