#import modules
from openai import OpenAI
import json
from helper_functions.config import get_secret

#use openai to perform web search

# import modules
from openai import OpenAI
import json

# Load API key (works locally + Streamlit Cloud)
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")   

# Define client with API key
client = OpenAI(api_key=OPENAI_API_KEY)          #

def web_browse(unmapped_entities: list, batch: int = 12):
    """
    Take the list of entities in unmapped_entities and use web browse tool.
    """

    targets = unmapped_entities[:batch]
    rows = []

    for e in targets:

        # ensure data is in a dict
        item = e if isinstance(e, dict) else dict(e)

        zh  = item.get("chinese", "")
        ctx = item.get("context_phrase", "")
        reg = item.get("region", "SG")
        eid = item.get("entity_id")

        prompt = f"""
You are a professional bilingual researcher based in Singapore.

Chinese entity: "{zh}"
Context phrase: "{ctx}"
Region: "{reg}"

### RULES
- Use official SG English names when available.
- Authoritative domains only: .gov.sg, .edu.sg, .org, CNA, ST, Wikipedia.
- Idioms: return meaning.
- If multiple credible names exist → MULTIPLE.
- If no English form exists → pinyin + "(unverified)".
- Return ONLY valid JSON.

JSON format to return:
{{
    "entity_id": {eid},
    "chinese": "{zh}",
    "translated_term": "<string>",
    "context_used": "{ctx}",
    "source_links": ["<url1>", "<url2>"],
    "verification_status": "VERIFIED|MULTIPLE|UNVERIFIED|ERROR",
    "notes": "<short>"
}}
"""

        try:
            resp = client.responses.create(
                model="gpt-4o-mini",
                tools=[{"type":"web_search"}],
                input=prompt,
                temperature=0.2,
                max_output_tokens=500
            )

            txt = resp.output_text or ""
            s, t = txt.find("{"), txt.rfind("}")
            payload = json.loads(txt[s:t+1]) if s != -1 and t != -1 else {}

        except Exception as ex:
            payload = {
                "translated_term": f"{zh} (unverified)",
                "verification_status": "ERROR",
                "source_links": [],
                "notes": f"{type(ex).__name__}"
            }

        rows.append({
            "entity_id": eid,
            "chinese": zh,
            "translated_term": payload.get("translated_term", ""),
            "context_used": ctx,
            "source_links": (payload.get("source_links") or [])[:3],
            "verification_status": payload.get("verification_status", "UNVERIFIED"),
            "notes": payload.get("notes", "")
        })

    return rows
