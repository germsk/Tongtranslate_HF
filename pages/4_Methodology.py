import streamlit as st
import pandas as pd
from helper_functions.utility import check_password
import os
from pathlib import Path

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="TongTranslate_Methodology"
)
# endregion <--------- Streamlit App Configuration --------->

#File Path
BASE_DIR = Path(os.getcwd())
IMAGES_DIR = BASE_DIR / "Images"
REFERENCE_DIR = BASE_DIR / "Reference"

# Do not continue if check_password is not True.  
if not check_password():  
    st.stop()

#display logo and title 

col1, col2 = st.columns([1, 6])

with col1:
    st.image(IMAGES_DIR / "logo.PNG", width=80)

with col2:
    st.title("TongTranslate - Methodology")

#Problem Statement
with st.expander("Problem Statement"):
    st.markdown("""

OpenAI’s translations using GPT-4o remain unreliable for proper nouns — especially local or Chinese names —
as well as idioms and culturally specific expressions. As a result, translators still perform substantial manual work: 
reviewing and editing model outputs, conducting internet searches, consulting the in-house glossary, and adding new terms when no entry exists.

This prototype aims to answer the question: 
**How can prompt design and workflow be improved to increase translation accuracy while automatically building and updating a backend glossary?**
                
**What is wrong with the current situation?**
                
Translators **lack trust in using AI-generated output because the translations are not sufficiently accurate**—particularly for names, idioms, and culturally specific terms. 
This **limits the usefulness of AI, and prevents wider adoption in the translation workflow.**
                """)   

#Approach to Solving the Problem
with st.expander("Approach to Solving the Problem"):
    st.markdown("""

For this prototype, I **identified limitations in the current OpenAI translations**.  

The **extract entities and web browse element helped to mimic the work process of the translator to verify terms through authoritative sources**
(prompt asked the LLM to retrieve translations from local news like Channel NewsAsia or websites ending with gov.sg to ensure a higher degree of accuracy).  The verified terms are then built into a backend glossary.  
""")

# Workflow
import streamlit as st

with st.expander("TongTranslate Workflow"):
    st.image(IMAGES_DIR / "Workflow.png", use_container_width=True)

    st.markdown("""
### TongTranslate Workflow Description

The TongTranslate prototype integrates **Crew AI agents, backend code, and OpenAI tools** to automate and **enhance Chinese-to-English translation** while **building a dynamic glossary**. 
The workflow consists of five sequential stages:

**1. User Input**

The process begins when the user submits a Chinese text for translation.

**2. Crew AI Agents**

Two specialised agents handle the initial processing:

Two specialised agents handle the initial processing:

- **Language Checker**  
  Detects whether the input contains Chinese characters. If Chinese is detected, processing continues. If not, the workflow stops and a message is returned.

- **Entity and Idiom / Cultural Expressions Extractor**  
  Extracts proper nouns, idioms, cultural expressions, and key terms requiring accurate and source-verified translation.

**3. Code (Backend Logic)**

The extracted entities are then sent into backend logic:

- **Map Against Backend Glossary**  
  Each entity is checked against the existing glossary. Mapped entities are immediately labelled; unmapped ones move to verification.

This step is performed using explicit code-based matching rules (e.g., longest-match, exact-match, Unicode-normalised comparisons).
This approach ensures consistency, because earlier prototypes using LLM-based matching was:
- unable to match all entries reliably
- inconsistent across runs
- non-deterministic (same input could produce different matches)

Since accurate term usage is essential for precise translation, entity–glossary matching must be done through deterministic algorithms, not LLM heuristics.
                
- **Merge Mapped Entities and Verified Entities**  
  After verification, mapped and newly verified entities are consolidated into **finalised entities**, which are injected into the translation prompt.

- **Cloud-Synced Glossary Persistence (Dropbox API)**  
  To ensure that glossary updates are preserved across sessions and deployments, TongTranslate uses the Dropbox API as a lightweight cloud persistence layer.  Newly verified terms—once approved through web-verification—are written directly to a Dropbox-hosted glossary file.  This allows the backend glossary to grow over time, remain consistent across all workflow runs, and stay editable through the Glossary page in the Streamlit interface.

**4. OpenAI**

Two OpenAI tools support verification and translation:

- **Web Browse for Updated English Translations**  
  Unmapped entities are verified using authoritative sources such as Channel NewsAsia or *.gov.sg* websites.

- **Translation**  
  Using the finalised verified entities, OpenAI generates the full English translation of the article as a Word document.

**5. Output**

The workflow produces two outputs:

- **Translated Article**  
  The final English article with accurate, source-verified terminology.

- **Updated Backend Glossary**  
  Newly verified terms are added to the glossary, improving accuracy and reducing repeated manual verification over time.  The glossary can be edited to maintain accuracy of translated terms.
                """)
    
    st.page_link("pages/2_Glossary.py", label="👉 Open Glossary Page")

# Evaluation of Results 

with st.expander("Hypothesis Testing and Validation"):
    st.markdown("""

**Hypothesis Testing and Validation**
                
To validate the assumptions behind the TongTranslate prototype, I worked closely with translators—our domain experts—to refine the prompt and incorporate their preferred translation style. We tested the prototype on several news articles containing proper nouns, official titles, and culturally specific expressions. These are the areas where GPT-4o commonly produces errors.

For each article, we compared the original Chinese text, the TongTranslate output, and the GPT-4o translation side-by-side to assess accuracy and consistency.

Early testing showed several clear improvements:

- **Princess Anne’s visit to Singapore**
    
    TongTranslate preserved the full title “Princess Anne” and maintained an appropriate news tone. GPT-4o produced a less precise headline.

- **Governor Khofifah Indar Parawansa of East Java Province**
    
    TongTranslate kept the full official designation. GPT-4o shortened or altered the title, reducing clarity.

- **Lawrence Wong on global structural change**
                
    TongTranslate used the correct ministerial title based on authoritative sources. GPT-4o introduced titles such as “Minister for Finance,” which did not match the Chinese text.

These examples support the hypothesis that entity extraction, web search, and glossary verification improve the accuracy of translated names and titles.

Testing also validated the assumption that web search improves accuracy when authoritative sources (e.g., CNA or gov.sg) are available. This helps counter a common issue in baseline LLM outputs where the model relies on outdated or incorrect internal knowledge. For instance, in early testing GPT-4o translated “President Tharman” as “President Halimah,” reflecting outdated information rather than the current office holder.

I will continue reviewing new entries in final_terms and monitor the accuracy of verified terms over time. When the glossary stabilises, TongTranslate can be considered for batch translation workflows.
             """)

    # Load Glossary
    filepath_use_cases = './Reference/use_cases.csv'
    use_cases = pd.read_csv(filepath_use_cases, encoding="utf-8-sig")
    
    st.subheader("Use Case Comparison Tests")

    st.table(use_cases)
