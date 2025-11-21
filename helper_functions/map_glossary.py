# Import 
import os
import json
import pandas as pd
from helper_functions.json_functions import read_json_safely, write_json
import unicodedata
from pathlib import Path 
import csv
from helper_functions.dropbox import read_csv_from_dropbox, write_csv_to_dropbox

#remove white space in text
def normalize(text: str) -> str:
    """Unicode + whitespace normalization."""
    return unicodedata.normalize("NFC", str(text)).strip().replace("\u3000", " ")

#mapping extracted entities to glossary (Step 1.5)
def map_glossary_local(
    entities,
    glossary_path="/Resources/glossary.csv",
    substring=True
):
    """
    Map extracted entities against glossary
    Creates two lists - mapped and unmapped
    Code to ensure deterministic mapping
    """

    # Step 2: read glossary
    glossary = read_csv_from_dropbox(glossary_path).fillna("")

    # convert csv to dict
    glossary_dict = {
        normalize(ch): en
        for ch, en in zip(glossary["chinese"], glossary["english"])
    }

    # create two empty lists
    mapped_entities = [] #terms found in glossary
    unmapped_entities = [] #terms not found in glossary

    # Map entities by looping
    for e in entities:
        # ensure each item is a normal python dict
        e_dict = e.dict() if hasattr(e, "dict") else e
        # normalise the Chinese text
        zh = normalize(e_dict.get("chinese", ""))
        # try exact match first
        eng = glossary_dict.get(zh, None)
        # if exact match fails, try substring search
        if not eng and substring:
            hits = [v for k, v in glossary_dict.items() if k and k in zh]
            eng = max(hits, key=len) if hits else None
        #update entity info 
        e_dict.update({
            "glossary_status": "KNOWN" if eng else "UNKNOWN",
            "translated_term": eng,
            "source": "glossary" if eng else None
        })
        #append to correct list
        if eng:
            mapped_entities.append(e)
        else:
            unmapped_entities.append(e)

    print(f"✅ Glossary mapping done: {len(mapped_entities)} mapped, {len(unmapped_entities)} unmapped")
    return mapped_entities, unmapped_entities

#saving new terms to glossary (Step 3)
def append_to_glossary_csv(final_terms, glossary_csv="/Resources/glossary.csv"):
    """
    Append verified terms into Dropbox glossary.csv
    """

    # Load existing glossary
    df = read_csv_from_dropbox(glossary_csv)

    # Track existing Chinese terms
    existing = set(df["chinese"].tolist())

    rows_to_add = []

    for term in final_terms:
        zh = term.get("chinese", "").strip()
        if not zh or zh in existing:
            continue

        rows_to_add.append({
            "chinese": zh,
            "english": term.get("english", "").strip(),
            "status": term.get("status", ""),
            "source": term.get("source", ""),
            "links": "; ".join(term.get("links", [])),
        })

    # Append new rows
    if rows_to_add:
        df = pd.concat([df, pd.DataFrame(rows_to_add)], ignore_index=True)

        # Save back to Dropbox
        write_csv_to_dropbox(df, glossary_csv)

        print(f"✅ Glossary updated with {len(rows_to_add)} new entries → {glossary_csv}")
    else:
        print("ℹ️ No new glossary terms added.")


# Step 3 - merging the terms into final_entities
def merge_terms(mapped_entities, verified_entities):
    """
    Combine glossary-mapped and web-verified terms.
    Verified terms override glossary results when available.
    Returns final list of terms in memory.
    """

    merged = {}

    # 1. Add glossary-known items
    for m in mapped_entities:
        zh = m.get("chinese")
        en = m.get("translated_term")

        if not zh or not en:
            continue

        merged[zh] = {
            "chinese": zh,
            "english": en,
            "status": "KNOWN",
            "source": m.get("source", "glossary"),
            "links": []
        }

    # 2. Add verified items (override glossary)
    for v in verified_entities:
        zh = v.get("chinese")
        if not zh:
            continue

        merged[zh] = {
            "chinese": zh,
            "english": v.get("translated_term", ""),
            "status": v.get("verification_status", "UNVERIFIED"),
            "source": "verified",
            "links": v.get("source_links", [])[:3]
        }

    return list(merged.values())
