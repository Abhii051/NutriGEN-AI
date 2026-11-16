"""
Master PDF Compiler Script for NutriGEN-AI Complete Technical Notes
Builds a publication-grade, double-pass numbered PDF document covering all 15 chapters.
"""

import sys
import os
import shutil
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable, Table, TableStyle
)
from reportlab.lib import colors

from scripts.pdf_styles import (
    NumberedCanvas, P, Callout, StyledTable, PRIMARY, SECONDARY, ACCENT, BORDER_COLOR, LIGHT_BG
)
from scripts.chapters_part1 import build_chapters_1_to_5
from scripts.chapters_part2 import build_chapters_6_to_10
from scripts.chapters_part3 import build_chapters_11_to_14
from scripts.chapters_part4 import build_chapter_15


def build_cover_page():
    story = []
    story.append(Spacer(1, 40))

    # Top Pill Badge
    pill_text = "<b>NUTRI-GENOMICS &amp; ARTIFICIAL INTELLIGENCE RESEARCH DIVISION</b>"
    story.append(P(f"<font color='{SECONDARY.hexval()}' size=8.5>{pill_text}</font>", "BodyBold"))
    story.append(Spacer(1, 10))

    # Document Title
    story.append(P("NutriGEN-AI", "CoverTitle"))
    story.append(P("Complete Technical Master Notes &amp; Engineering Viva Defense Manual", "CoverSubtitle"))
    story.append(HRFlowable(width="100%", thickness=2.5, color=PRIMARY, spaceAfter=18))

    # Abstract / Overview Callout
    story.append(Callout(
        "Official Academic Reference & Defense Guide",
        "This master notes manual provides an exhaustive, line-by-line engineering breakdown of NutriGEN-AI (Commit 9df7ad1). "
        "It covers clinical biometrics (Mifflin-St Jeor), dataset ETL pipelines (USDA FoodData Central), rule-based canonical "
        "allergen ontology, the mathematical formulation and convergence criteria of SciPy SLSQP constrained numerical optimization, "
        "sub-second Groq LPU LLM inference (Meta Llama 3.3 70B/3.1 8B), two-tier regex allergen defense, W3C CORS security hardening, "
        "and over 200 categorized viva examination questions with complete examiner-ready answers.",
        "info"
    ))
    story.append(Spacer(1, 24))

    # Metadata Table
    meta_headers = ["Project Metadata Field", "Engineering Specification & Verified Status"]
    meta_rows = [
        ["Project Title", "<b>NutriGEN-AI: Personalized AI-Based Nutrition & Meal Recommendation System</b>"],
        ["Target Benchmark", "Production-Ready MVP & Final Year Engineering Capstone Defense (Rated 8.5/10)"],
        ["Latest Verified Git Commit", "<code>9df7ad1</code> (Full Audit Tightening & 100% Passing Test Suite)"],
        ["Primary Author / Student", "Abhinav Sharma (Abhii051) & Engineering Team"],
        ["Core Technology Stack", "FastAPI, SciPy (SLSQP), Pandas, NumPy, Groq LPU (Meta Llama 3), Vanilla JS ES6+"],
        ["Dataset Source", "USDA FoodData Central (3,000+ Curated Foundation Foods & SR Legacy Records)"],
        ["Allergen & Quality Defense", "Two-Tier Pre-Optimization Ontology Filtering + Post-Generation Regex Scan"],
        ["Testing Coverage", "100% Pass Rate across 6 Clinical Profiles in Backend/tests/test_end_to_end_audit.py"]
    ]
    story.append(StyledTable(meta_headers, meta_rows, [160, 344]))
    story.append(Spacer(1, 24))

    # Table of Contents Overview
    story.append(P("Table of Contents & Curriculum Map", "SectionHeading"))
    toc_headers = ["Chapter #", "Curriculum Topic", "Primary Codebase File", "Key Focus Areas"]
    toc_rows = [
        ["Chapter 1", "Project Overview & Architecture", "High-Level System", "Problem statement, comparative matrix, 3-tier model, user journey"],
        ["Chapter 2", "Repository Structure & Files", "Entire Project Tree", "Every file, folder, function, input, output, caller, and legacy cleanup"],
        ["Chapter 3", "Clinical Nutrition Engine", "ai_model.py", "Mifflin-St Jeor, BMR, TDEE, PAL multipliers, 4-4-9 macro partition"],
        ["Chapter 4", "Food Dataset & Processing", "data_processing/, CSV", "USDA Foundation vs SR Legacy, FDC ID, cleaning ETL, per-100g math"],
        ["Chapter 5", "Preferences & Candidate Selection", "preferences.py", "Diet filters, canonical allergen ontology, food roles, deduplication"],
        ["Chapter 6", "The SLSQP Optimizer (Deep Dive)", "optimizer.py", "SciPy SLSQP, decision variables, bounds, objective weights, penalties"],
        ["Chapter 7", "Groq LPU & LLM Integration", "recipe_generator.py", "LPU architecture, Meta Llama 3.3/3.1, prompts, heuristic engine"],
        ["Chapter 8", "Allergen Safety & Validation", "recipe_generator.py", "Two-tier defense, regex word boundary, negative lookahead, disclaimers"],
        ["Chapter 9", "FastAPI Backend Architecture", "server.py", "REST endpoints, Pydantic schemas, W3C CORS, status codes, 500 safety"],
        ["Chapter 10", "Frontend & Communication", "frontend/script.js", "Live biometrics, DOM textContent XSS protection, localStorage, grocery"],
        ["Chapter 11", "End-to-End System Integration", "Master Pipeline", "Master call-flow sequence diagram, inter-module data contracts"],
        ["Chapter 12", "Testing & Quality Assurance", "test_end_to_end_audit.py", "Unit vs integration vs E2E, 6 clinical audit test cases, mocking Groq"],
        ["Chapter 13", "Deployment, DevOps, & Config", "requirements.txt, .env", "Virtual environments, local run steps, port conflicts, troubleshooting"],
        ["Chapter 14", "Limitations & Future Roadmap", "Architecture Analysis", "Engineering limitations, why RAG was not used, future roadmap"],
        ["Chapter 15", "The Ultimate Viva Defense Guide", "Defense Preparation", "Pitches (2/5/10 min), demo script, 200+ categorized Q&A"]
    ]
    story.append(StyledTable(toc_headers, toc_rows, [55, 150, 120, 179]))

    story.append(PageBreak())
    return story


def main():
    print("Beginning NutriGEN-AI Master Notes PDF Compilation...")
    output_pdf_path = PROJECT_ROOT / "NutriGEN_AI_Complete_Master_Notes.pdf"
    
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    story = []

    # 1. Cover & Table of Contents
    story.extend(build_cover_page())

    # 2. Chapters 1 to 5
    print("Building Chapters 1 to 5...")
    story.extend(build_chapters_1_to_5())

    # 3. Chapters 6 to 10
    print("Building Chapters 6 to 10 (including Optimizer deep dive)...")
    story.extend(build_chapters_6_to_10())

    # 4. Chapters 11 to 14
    print("Building Chapters 11 to 14 (Integration, Testing, DevOps, Limitations)...")
    story.extend(build_chapters_11_to_14())

    # 5. Chapter 15: The Ultimate Viva Defense Guide
    print("Building Chapter 15 (Viva Defense Guide with 200+ Q&A)...")
    story.extend(build_chapter_15())

    # Compile PDF with two-pass canvas
    print(f"Compiling flowables into PDF: {output_pdf_path}...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build successful!")

    # Copy to Artifact directory as well if it exists
    artifact_dir = Path(r"C:\Users\abhi\.gemini\antigravity\brain\c788ebc5-52c3-4a1a-81c1-2f4e8f7b4948")
    if artifact_dir.exists():
        dest_artifact = artifact_dir / "NutriGEN_AI_Complete_Master_Notes.pdf"
        shutil.copyfile(output_pdf_path, dest_artifact)
        print(f"Copied master PDF to artifact directory: {dest_artifact}")


if __name__ == "__main__":
    main()
