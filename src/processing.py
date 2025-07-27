# src/processing.py
import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import time
import re
from collections import Counter

# This model is small, runs on CPU, and is great for semantic search
MODEL_NAME = 'all-MiniLM-L6-v2'
# --- THIS IS THE CRUCIAL FIX ---
# local_files_only=True forces the library to use the cached model
# and prevents it from trying to connect to the internet.
model = SentenceTransformer(MODEL_NAME, local_files_only=True)


def get_base_font_size(page):
    """
    Finds the most common font size on a page to identify body text.
    """
    fonts = [span['size'] for block in page.get_text("dict")["blocks"] for line in block.get("lines", []) for span in line.get("spans", [])]
    if not fonts:
        return 10
    return Counter(fonts).most_common(1)[0][0]


def is_likely_heading(span, base_font_size):
    """
    A much-improved heuristic to determine if a text span is a heading.
    """
    is_larger = span['size'] > base_font_size
    is_bold = "bold" in span['font'].lower()
    is_short_and_clean = len(span['text'].split()) < 12 and not span['text'].strip().endswith('.')
    return is_larger and (is_bold or is_short_and_clean)


def extract_structured_chunks(pdf_path):
    """
    A more robust function to extract structured content (headings and their text).
    """
    doc = fitz.open(pdf_path)
    sections = []
    
    for page_num, page in enumerate(doc):
        base_font_size = get_base_font_size(page)
        blocks = page.get_text("dict")["blocks"]
        current_heading = "Introduction"
        current_text = ""
        
        for block in blocks:
            if "lines" in block and block["lines"]:
                span = block["lines"][0]["spans"][0]
                if is_likely_heading(span, base_font_size):
                    if current_text.strip():
                        sections.append({
                            "document": os.path.basename(pdf_path),
                            "page_number": page_num + 1,
                            "section_title": current_heading,
                            "content": current_text.strip()
                        })
                    current_heading = " ".join([s['text'] for l in block['lines'] for s in l['spans']]).strip()
                    current_text = ""
                else:
                    block_text = " ".join([s['text'] for l in block['lines'] for s in l['spans']])
                    current_text += block_text + "\n"

    if current_text.strip():
        sections.append({
            "document": os.path.basename(pdf_path),
            "page_number": page_num + 1,
            "section_title": current_heading,
            "content": current_text.strip()
        })
        
    return sections


def refine_text(content, query_embedding, max_sentences=5):
    """
    A more robust function to find the most relevant sentences.
    """
    cleaned_content = content.replace('\n', ' ').replace('\u2022', '').replace('\uf0b7', '')
    cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
    
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned_content) if s.strip()]

    if not sentences:
        return ""
        
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, sentence_embeddings)[0]
    
    relevant_sentences = [(score, sent) for score, sent in zip(cosine_scores, sentences) if score > 0.1]
    ranked_sentences = sorted(relevant_sentences, key=lambda x: x[0], reverse=True)
    
    top_sentences = [s for score, s in ranked_sentences[:max_sentences]]
    return " ".join(top_sentences)


def process_documents_for_persona(pdf_paths, challenge_data):
    """
    Main processing function (no changes needed here).
    """
    persona_info = challenge_data['persona']
    job_info = challenge_data['job_to_be_done']

    query = f"Role: {persona_info['role']}. Task: {job_info['task']}"
    query_embedding = model.encode(query, convert_to_tensor=True)

    all_sections = []
    for pdf_path in pdf_paths:
        all_sections.extend(extract_structured_chunks(pdf_path))

    section_titles = [sec['section_title'] for sec in all_sections]
    title_embeddings = model.encode(section_titles, convert_to_tensor=True)
    title_scores = util.cos_sim(query_embedding, title_embeddings)[0]
    
    ranked_sections = sorted(zip(title_scores, all_sections), key=lambda x: x[0], reverse=True)

    output_sections = []
    seen_titles = set()
    rank = 1
    for score, section in ranked_sections:
        if rank > 5: break
        if section['section_title'] not in seen_titles:
            output_sections.append({
                "document": section["document"],
                "section_title": section["section_title"],
                "importance_rank": rank,
                "page_number": section["page_number"]
            })
            seen_titles.add(section['section_title'])
            rank += 1
            
    subsection_analysis = []
    for item in output_sections:
        original_section = next((sec for sec in all_sections if sec['section_title'] == item['section_title']), None)
        if original_section:
            refined = refine_text(original_section['content'], query_embedding)
            if refined:
                subsection_analysis.append({
                    "document": item["document"],
                    "refined_text": refined,
                    "page_number": item["page_number"]
                })

    final_output = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in pdf_paths],
            "persona": persona_info["role"],
            "job_to_be_done": job_info["task"],
            "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "extracted_sections": output_sections,
        "subsection_analysis": subsection_analysis
    }
    
    return final_output
