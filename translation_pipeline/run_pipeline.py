# Import modules
import os
import sys
import pandas as pd

# telling code where to look
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#import functions
from dotenv import load_dotenv
from agents.agents import extract_entities
from helper_functions.map_glossary import map_glossary_local, append_to_glossary_csv, merge_terms
from helper_functions.normalize_output import norm
from openai_calls.web_browse import web_browse
from openai_calls.translator import translate_function
from crewai import Crew, Process

#Load the environment variables
# If the .env file is not found, the function will return `False
load_dotenv()

#set gpt model
os.environ['OPENAI_MODEL_NAME'] = "gpt-4o-mini"

#define translation pipeline

def translation_pipeline(input_text, batch: int | None = 10):

    # Step 1 - agents/ task lang check and entity extraction 
    # Use of AI agents to ensure structured output 
    print("🔍 Step 1: Running entity extraction and glossary mapping…")
    raw_extracted_data = extract_entities.kickoff(inputs={"text": input_text})

    #ensure output is in-memory dict
    clean_extracted_entities = norm(raw_extracted_data)
    #obtain list of extracted entities
    extracted_entities = clean_extracted_entities.get("entities", [])
    print(f"✅ Extracted {len(extracted_entities)} entities in memory.")

    # Step 1.5 - glossary mapping 
    # invoking function for mapping 
    print("📘 Mapping extracted terms against backend glossary…")
    mapped_entities, unmapped_entities = map_glossary_local(extracted_entities)
    # ✅ Entities mapped against glossary
    print(f"✅ Entities mapped: {len(mapped_entities)} mapped | {len(unmapped_entities)} unmapped")

    # Step 2 - web browsing 
    # use of Open AI web browse function for entities tagged as "UNKNOWN" in mapped_entities.json (created in step 1.5)
    print("🌐 Step 2: Verifying unknown/ambiguous terms via web search…")
    verified_entities = web_browse(unmapped_entities, batch=batch)          # set batch=None to do ALL unknowns
    print("✅ Step 2 done.")

    # step 3 - building glossary 
    # invoking function to build glossary for #Step 4 
    print("📘 Step 3: Building translated terms and appending to backend glossary...")
    #combining mapped_entities and verified_entities
    final_terms = merge_terms(mapped_entities, verified_entities) 
    #append terms to glossary
    append_to_glossary_csv(final_terms)
    print("✅ Step 3 done.")

    # Step 4 - translation in progress 
    # use of Open AI to translate and with reference to final_terms
    print("🗣️ Step 4: Translation in progress")
    result = translate_function (input_text, final_terms)
    print("✨ Translation complete.")

    # 💥 DEBUG PRINTS AT THE END
    print("\n====== DEBUG: mapped_entities ======")
    for e in mapped_entities:
        print(e)

    print("\n====== DEBUG: unmapped_entities ======")
    for e in unmapped_entities:
        print(e)

    print("\n====== DEBUG: verified_entities ======")
    for e in verified_entities:
        print(e)

    print("\n====== DEBUG: final_terms ======")
    for e in final_terms:
        print(e)

    return result, final_terms
