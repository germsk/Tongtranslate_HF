import streamlit as st
from pathlib import Path
import os

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="About TongTranslate"
)
# endregion <--------- Streamlit App Configuration --------->
# safe file path
BASE_DIR = Path(os.getcwd())
IMAGES_DIR = BASE_DIR / "Images"
REFERENCE_DIR = BASE_DIR / "Reference"

from helper_functions.utility import check_password

# Do not continue if check_password is not True.  
if not check_password():  
    st.stop()

#display logo and title 

col1, col2 = st.columns([1, 6])

with col1:
    st.image(IMAGES_DIR / "logo.PNG", width=80)

with col2:
    st.title("TongTranslate")

# 0 - About Us
with st.expander("About TongTranslate"):
    st.markdown("""
**TongTranslate** takes its name from Chinese word **通 (tōng)**, meaning to connect, to clarify, to make things flow. 
The tool embodies this idea by bridging gaps in Chinese-to-English translation. 
It identifies **proper nouns, idioms, and cultural terms,** verifies their correct English meanings through targeted web searches using contextual phrases, and then produces a precise translation. 
Each verified entity is added to a continually **growing backend glossary**, allowing TongTranslate to become more accurate and consistent with every use.
The **backend glossary** can be edited by translators to ensure accuracy of translated terms.
    """)

# 1. Project Scope
with st.expander("1. Project Scope"):
    st.markdown("""
**TongTranslate** is an AI-powered Chinese–English translation system designed to deliver 
**accurate, culturally aware, and contextually faithful translations**.

The project covers the core stages of the translation workflow, including:

- **Automated extraction** of entities, idioms, cultural expressions, and proper nouns  
  from user-supplied Chinese text.
- **Mapping extracted entities** against a backend bilingual glossary and previously 
  verified terms.
- **Web-based verification** of any unmapped entities using LLM-driven browsing to obtain 
  authoritative and up-to-date English equivalents.
- **LLM-enhanced translation** that preserves tone, cultural nuance, idiomatic meaning, 
  and intended message.
- **Continuous glossary enrichment**, where newly verified entities are written back into 
  the backend glossary to improve accuracy and consistency over time.
- **Generation of polished English output**, including a downloadable Word document and 
  a list of resolved entities for editorial review.

TongTranslate integrates AI agents, targeted tool use, glossary management, and OpenAI 
models into a cohesive end-to-end pipeline that significantly reduces manual verification.
    """)

# 2. Objectives Section
with st.expander("2. Objectives"):
    st.markdown("""
**TongTranslate** aims to solve key challenges in Chinese–English translation:

1. **Resolve inaccurate translations of proper nouns and vernacular terms**, which current tools often mistranslate due to missing context.
2. **Remove the need for manual online searching**, by automatically retrieving verified English equivalents.
3. **Eliminate manual glossary upkeep**, ensuring consistent terminology across documents.
4. **Improve domain accuracy**, producing translations aligned with professional standards.
5. **Increase efficiency and scalability**, reducing human workload while maintaining high quality.
    """)

# 3. Features Section
with st.expander("3. Key Features"):
    st.markdown("""
1. **Precision Entity Extraction**  
   Identifies proper nouns, cultural references, and domain-specific expressions that general tools often misinterpret.

2. **Intelligent Web-Search Verification**  
   Retrieves authoritative English equivalents for unmapped names, organisations, idioms, and events—removing the need for manual Googling.

3. **Self-Updating Glossary**  
   Automatically enriches the bilingual glossary with each translation run, reducing manual upkeep.

4. **Human-in-the-Loop Glossary Editing**  
   Allows translators to review and edit glossary entries for accuracy and consistency.
    """)

    st.page_link("pages/2_Glossary.py", label="👉 Open Glossary Page")

    st.markdown("""
5. **Context-Aware Glossary Mapping**  
   Ensures consistent terminology by matching extracted entities against the backend glossary and supporting human-in-the-loop verification.

6. **Culturally Faithful Translation**  
   Produces natural, domain-accurate English that preserves tone, nuance, and intent.

7. **Ready-to-Download Output**  
   Generates a clean, formatted Word document with the translated text and verified terms.
    """)

# 4. Data Sources
with st.expander("4. Data Sources"):
    st.markdown("""
- **Evolving Bilingual Glossary**  
  A glossary that grows with each translation run and is refined by an expert translator.

- **PETCI Dataset (Parallel English Translation of Chinese Idioms)**  
  A researcher-curated dataset containing gold-standard English translations of Chinese idioms.  
  TongTranslate uses a **preprocessed and cleaned PETCI subset**, standardised for consistent term extraction and evaluation.
  🔗 [PETCI Dataset](https://github.com/kenantang/petci)
    """)

#How to Use this App 
with st.expander("How to use this App"):
    st.markdown("""
1. Enter the text to be translated in the text area.
2. Click the 'Submit' button.
3. The app will generate the following:
    1. Mandarin Original
    2. English Translation
    3. Notes (option)
    - A downloadable word document containing the above.
    - Verified Terms Used in Translation
             """)
    
    #Dpwnload sample output

    st.subheader("📄 Download Sample Translation Output")

    sample_path = REFERENCE_DIR / "sample_output.docx"

    with open(sample_path, "rb") as f:
        sample_bytes = f.read()

    st.download_button(
        label="⬇️ Download Sample Output",
        data=sample_bytes,
        file_name="sample_output.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
