# imports
from openai import OpenAI
from docx import Document
import tempfile
import os
import json

# Load API key from HuggingFace environment variables
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# define client
client = OpenAI(api_key=OPENAI_API_KEY)

# function to convert markdown to word document
def convert_markdown_to_word(markdown_text: str) -> str:
    """
    Converts LLM markdown output into a Word (.docx) file.
    Returns the absolute path to the saved file.
    """
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "translation_output.docx")

    doc = Document()
    for line in markdown_text.split("\n"):
        doc.add_paragraph(line)

    doc.save(output_path)
    return output_path

# define tool for function calling
word_tool = [
    {
        "type": "function",
        "name": "convert_markdown_to_word",
        "description": "Convert LLM translation output (markdown) into a Word document and return file path.",
        "parameters": {
            "type": "object",
            "properties": {
                "markdown_text": {
                    "type": "string",
                    "description": "Translation output in markdown format."
                }
            },
            "required": ["markdown_text"]
        }
    }
]

#translation prompt

translation_prompt = """
You are an expert bilingual Chinese→English news translator with rigorous terminology discipline. 
You translate faithfully, apply verified glossary terms consistently, and write in clear, concise, journalistic UK English for a Singapore audience.

Before translating, confirm the {text} is Mandarin (Simplified or Traditional).
If not, output the same error JSON as in the language check and STOP. 
If Mandarin, translate into UK English for a Singapore readership in a clear, concise, journalistic style.
**Do NOT use content, quotes, or wording sourced from Lianhe Zaobao (早报) to verify your English translation.**  
Perform these steps **in order**:

-----------------------------------------------------------------------
VERIFIED TERMS PROVIDED
-----------------------------------------------------------------------
You have been provided the verified bilingual terms below. 
Always use these exact English names or expressions whenever they appear 
in the source text — do not override, retranslate, or ignore them.

{verified_table}

Always use the verified bilingual glossary terms provided above.
If a Chinese name or term is not in the list, use pinyin for names and clear English paraphrasing for expressions.

-----------------------------------------------------------------------
TRANSLATION GUIDELINES
-----------------------------------------------------------------------
Here is the source_text you must process.  
Copy it EXACTLY (including heading, blank lines, and paragraphs) in section 1.  
Translate EVERY LINE of the source_text to English.

IMPORTANT — DO NOT SKIP THE HEADLINE:
• The *first non-empty line* of the source_text is the HEADLINE.
• You MUST copy the headline EXACTLY into Section 1 (“Mandarin Original”).
• You MUST translate the headline as the FIRST line in Section 2 (“English Translation”).
• NEVER omit, merge, replace, or reinterpret the headline.

<source_text>
{text}
</source_text>

Preserve paragraphing.  Avoid added or altered facts.

Idioms: use standard English equivalent if available. Otherwise paraphrase naturally; optionally add a brief literal gloss in brackets only if it aids clarity. 
Introduce acronyms on first mention; avoid multiple variants in brackets; pick one best form.

Other translation guidelines:
    - WORD CHOICE
        •	Prefer slightly elevated but natural word choices where they improve readability (e.g., grand drum vs big drum).
        •	Use mainstream English for religious/philosophical terms (e.g., Zen Buddhism, Ancestor).
        •	For cultural festivals, use mainstream SG media forms (Lunar New Year, Hungry Ghost Festival).
    - NAMES
        •	For Singapore personalities (politicians, community leaders, volunteers, artists), ALWAYS use the official English spelling of names, followed by community-used names if official English spelling is not available.
        •	If no official spelling exists, use pinyin and mark (to verify).
        •	Always use official English names for Singapore institutions, clan associations, and venues (e.g., SFCCA, SCCCI, School of the Arts (SOTA) Concert Hall).
    - GENERAL STYLE
        •	Avoid academic digressions or multiple variants in brackets — select the best single form.
        •	Ensure translations read smoothly and naturally for a Singaporean English-speaking audience.
        •	Use Natural, Fluent English.  Ensure the translation reads smoothly and naturally.
        •	Preserve the meaning, tone, and nuance of the original.
    
Ensure:
- Consistency of entity names throughout the translation.
- Correct acronym introduction (first mention spelled out).
- No added or altered facts.
- Original paragraphing preserved.

-----------------------------------------------------------------------
OUTPUT FORMAT
-----------------------------------------------------------------------
    1) Mandarin Original  
     <verbatim copy>  

    2) English Translation  
     <final translated text>  

    3) Notes (optional)  
     Brief clarifications about tricky names or idioms.
"""

#format block to insert into prompt
def make_verified_terms_block(final_terms) -> str:
    lines = []
    for t in final_terms:
        zh = t.get("chinese", "")
        en = t.get("translated_term", t.get("english", ""))
        status = t.get("verification_status", t.get("status", ""))

        if zh and en:
            if status:
                lines.append(f"- {zh} → {en} ({status})")
            else:
                lines.append(f"- {zh} → {en}")

    return "\n".join(lines) if lines else "No verified terms available."

def translate_function (input_text: str, final_terms: list) -> str:
    """
    Translates Mandarin → English using the verified bilingual glossary.
    Uses the predefined translation_prompt template.
    """

    # Load verified bilingual terms for prompt injection
    verified_table = make_verified_terms_block(final_terms)

    # Build the final prompt text by injecting runtime variables
    prompt = translation_prompt.format(
        verified_table=verified_table,
        text= input_text
    )
    
    # Call the model
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,             
        temperature=0.1,          # low randomness for stable translation
        max_output_tokens=4096,   # generous length
        tools = word_tool,        # call word tool to save output as word document 
        tool_choice="auto",       # let LLM decide 
    )
     # If LLM decides to call the tool 
    output = response.output[0]

    if hasattr(output, "tool_calls") and output.tool_calls:
        tool_call = output.tool_calls[0]   # expecting one tool call
        fn = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if fn == "convert_markdown_to_word":
            markdown_text = args["markdown_text"]
            return convert_markdown_to_word(markdown_text)
        
    # Otherwise, return normal markdown -
    return response.output_text
 