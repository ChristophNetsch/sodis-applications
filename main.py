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

    st.set_page_config(page_title='Frag Nico-Mario', page_icon = FAVICON, initial_sidebar_state = 'auto')

    st.image(LOGO_IMG.resize( [int(0.5 * s) for s in LOGO_IMG.size]), use_column_width=True)
    st.header('Einstellungen')

    kf_name = st.selectbox('Wähle eine hinterlegte Wissensquelle:', get_knowledge_file_options())
    uploaded_file = st.file_uploader("Oder wähle eine eigene Wissensquelle (TXT-Datei):")
    getfile = st.button("Einlesen..")

    temperature = st.slider("Sprachmodell-Temperatur", min_value=0.0, max_value=2.0, value=0.1, step=0.01, help="Je höher, desto kreativer die Antworten")
    max_tokens = st.slider("Max. Anzahl Tokens", min_value=8, max_value=500, value=100, step=1, help="Je höher, desto länger werden die Antworten potenziell.")
    max_rerank = st.slider("Recherche-Gründlichkeit", min_value=50, max_value=500, value=300, step=1, help="Je höher, desto höher die Antwortqualität.")
    
    st.header('Fragen')

    question = st.text_area("",value="Was ist denn Aktion Sodis?")
    button = st.button("Frag Nico-Mario!")

    # Set filepaths for knowledge bank
    knowledge_jsonl = Path(KNOWLEDGE_FILEPATH, JSONLNAME)
    knowledge_txt = Path(kf_name)

    if uploaded_file:
        string_data = uploaded_file.read()
        lines = [{"text": line.decode("utf-8")} for line in string_data.splitlines() if line]
        # Convert to a list of JSON strings
        json_lines = [json.dumps(l) for l in lines]

        # Join lines and save to .jsonl file
        json_data = '\n'.join(json_lines)
        
        with open(knowledge_jsonl, 'w') as f:
            f.write(json_data)
        
        update_knowledge_base_and_sleep(knowledge_jsonl)

    if getfile:
        if not uploaded_file:
            convert_txt2jsonl(knowledge_jsonl, knowledge_txt)
        update_knowledge_base_and_sleep(knowledge_jsonl)

    # Knowledge engine question and answer
    if button:
        can_query = True

        if can_query:
            try:
                with st.spinner(text="Nico-Mario denkt nach..."):
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
                st.markdown(response_json["answers"][0], unsafe_allow_html=False)
                
            except openai.error.InvalidRequestError as ex:
                st.error(f"Irgendwas ist schief gelaufen: ({ex.user_message}).")

def update_knowledge_base_and_sleep(knowledge_jsonl):
    try:
        with st.spinner(text="Wissensquelle wird eingelesen..."):   
            update_knowledge_base(knowledge_jsonl, knowledge_available_online)
            sleep(5)
    except openai.error.InvalidRequestError as ex:
        st.error(f"Irgendwas ist beim Hochladen schief gelaufen: ({ex.user_message}).")
            
if __name__ == "__main__":
    main()
