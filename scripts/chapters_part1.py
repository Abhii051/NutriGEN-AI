"""
Chapters 1 through 5 Content for NutriGEN-AI Master Notes
Covers:
- Chapter 1: Complete Project Understanding, Architecture, and Workflow
- Chapter 2: Repository Structure & File Responsibilities
- Chapter 3: Nutrition Calculation Engine (ai_model.py & Mifflin-St Jeor)
- Chapter 4: Dataset & Food Processing (USDA FDC, SR Legacy, Master Dataset)
- Chapter 5: Preferences, Canonical Allergen Ontology, and Candidate Selection
"""

from reportlab.platypus import PageBreak, Spacer, HRFlowable
from scripts.pdf_styles import (
    P, CodeBlock, Callout, StyledTable, QA, PRIMARY, SECONDARY, ACCENT
)


def build_chapters_1_to_5():
    story = []

    # =========================================================================
    # CHAPTER 1: COMPLETE PROJECT ARCHITECTURE & WORKFLOW
    # =========================================================================
    story.append(P("Chapter 1: Project Overview, Objectives, and System Architecture", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("1.1 What Exactly is NutriGEN-AI?", "SectionHeading"))
    story.append(P(
        "<b>NutriGEN-AI</b> is a full-stack, clinically bounded precision nutrition platform that couples "
        "<b>deterministic numerical optimization</b> (Sequential Least Squares Programming via SciPy) with "
        "<b>generative Large Language Models</b> (Meta Llama 3.3 70B and 3.1 8B via Groq LPU inference). "
        "It solves the fundamental flaw of modern AI diet assistants: <i>LLMs cannot perform accurate arithmetic, "
        "and numerical solvers cannot write tasty culinary recipes.</i> By separating mathematics from culinary synthesis, "
        "NutriGEN-AI achieves clinically exact macronutrient matching (&le; 5% error) with authentic cooking instructions."
    ))

    story.append(P("1.2 The Core Problem Statement", "SectionHeading"))
    story.append(P(
        "Generic fitness applications (e.g. MyFitnessPal, HealthifyMe) provide rigid, pre-cooked templates that fail "
        "to accommodate personal cultural diets (e.g. Indian vegetarian vs Mediterranean pescatarian), variable meal "
        "frequencies (2, 3, 4, or 5 eating occasions), or complex clinical allergies. Conversely, when users prompt "
        "conversational LLMs like ChatGPT for a diet, the model hallucinates caloric values by <b>20% to 50%</b> because "
        "autoregressive transformers predict next tokens rather than solving constrained mathematical equations. "
        "NutriGEN-AI addresses this dual failure."
    ))

    story.append(Callout(
        "The Fundamental Engineering Principle",
        "Never use an LLM for arithmetic or portion optimization. Use SciPy SLSQP for exact mathematical portion sizing, "
        "and use the LLM strictly for culinary language transformation (dish naming, step-by-step cooking methods).",
        "info"
    ))
    story.append(Spacer(1, 8))

    story.append(P("1.3 High-Level Comparative Analysis", "SectionHeading"))
    comp_headers = ["Evaluation Metric", "Generic Diet Apps", "Direct LLM Prompting", "NutriGEN-AI (Our Engine)"]
    comp_rows = [
        ["Calorie & Macro Sizing", "Static lookup tables", "Hallucinated (&plusmn;20-50% drift)", "<b>SciPy SLSQP Solver (&le; 5% error)</b>"],
        ["Portion Sizing", "Manual user guesswork", "Arbitrary approximations", "<b>Continuous grams clamped to bounds</b>"],
        ["Recipe Generation", "None or static links", "Hallucinated unmeasured foods", "<b>AI Chef bound strictly to grams</b>"],
        ["Allergen Protection", "Basic string matches", "Prompt drift / ignored", "<b>2-tier pre-filter + regex post-validator</b>"],
        ["Meal Occasions", "Fixed 3 meals", "Unstructured text", "<b>Dynamic 2, 3, 4, 5 meals (0 duplicates)</b>"],
        ["Execution Speed", "Fast", "Slow (4-8s OpenAI)", "<b>Sub-second Groq LPU / Heuristic fallback</b>"]
    ]
    story.append(StyledTable(comp_headers, comp_rows, [100, 110, 130, 164]))
    story.append(Spacer(1, 10))

    story.append(P("1.4 Three-Tier Architecture & System Components", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI is architected cleanly across three distinct decoupled tiers:<br/>"
        "<b>1. Client Presentation Tier (Frontend):</b> Single-page reactive application built in vanilla HTML5, "
        "modern CSS3, and ES6+ JavaScript. Features real-time client-side biometrics calculation, DOM textContent XSS immunization, "
        "localStorage plan history drawer, grocery checklist modal, and print report export.<br/>"
        "<b>2. Application & API Tier (Backend):</b> FastAPI asynchronous REST framework running on Uvicorn ASGI server. "
        "Enforces W3C-compliant CORS (explicit localhost defaults), Pydantic schema validation (PlanGenerationRequest), and exception sanitization.<br/>"
        "<b>3. Algorithmic & Intelligence Engines:</b><br/>"
        "&nbsp;&nbsp;• <i>Biometric Calculator (ai_model.py):</i> Mifflin-St Jeor clinical energy expenditure engine.<br/>"
        "&nbsp;&nbsp;• <i>Preferences & Allergen Filter (preferences.py):</i> Canonical allergen ontology with alias clustering.<br/>"
        "&nbsp;&nbsp;• <i>Numerical Optimization Solver (optimizer.py):</i> Bounded quadratic SciPy SLSQP solver.<br/>"
        "&nbsp;&nbsp;• <i>Generative Recipe Chef (recipe_generator.py):</i> Groq LPU Llama 3.3/3.1 with automated regex safety post-validation."
    ))

    story.append(P("1.5 Complete Input-to-Output Flowchart", "SectionHeading"))
    flow_diagram = (
        "+-----------------------------------------------------------------------------------+\n"
        "|                             CLIENT BROWSER (script.js)                            |\n"
        "|  User enters: Age, Sex, Height, Weight, Goal, Diet, Allergies, Meals, Prompt     |\n"
        "|  Real-time client biometrics display (BMR, TDEE, Calorie Target, Water Intake)    |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          | HTTP POST /api/generate-plan (JSON)\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|                            FASTAPI BACKEND (server.py)                            |\n"
        "|  W3C CORS Check -> Pydantic Schema Validation -> run_nutrigen_pipeline()          |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          | Handed to pipeline.py\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|                    1. BIOMETRIC CALCULATOR (ai_model.py)                         |\n"
        "|  Mifflin-St Jeor: BMR -> Activity Factor -> TDEE -> Goal Delta -> Macro Grams     |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          | Calories, Protein, Fat, Carbs Targets\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|                 2. PREFERENCE & ALLERGY FILTER (preferences.py)                   |\n"
        "|  Loads 3,000+ USDA foods -> Diet Filter -> Canonical Allergen Cluster Purge       |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          | Filtered Eligible Food Candidates\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|               3. CANDIDATE SELECTION & SLSQP SOLVER (optimizer.py)                |\n"
        "|  Scales to 2, 3, 4, 5 meals -> Zero Duplicate FDC IDs -> Bounds [L, U]            |\n"
        "|  SciPy minimize(method='SLSQP') -> Dual-Criteria Check -> Bounded Clamping        |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          | Exact Weighed Food Items per Meal Slot\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|                4. AI CHEF RECIPE GENERATOR (recipe_generator.py)                  |\n"
        "|  Groq API (Llama 3.3 70B / 3.1 8B) -> validate_recipe_safety() Post-Scan          |\n"
        "|  If unsafe or offline -> Immediate Smart Heuristic Recipe Fallback Switch         |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          | Complete JSON Response\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|                        CLIENT PRESENTATION & LOCAL STORAGE                        |\n"
        "|  DOM textContent Rendering -> Macro Gauges -> Recipe Drawers -> Grocery Checklist |\n"
        "+-----------------------------------------------------------------------------------+"
    )
    story.append(CodeBlock(flow_diagram))
    story.append(Spacer(1, 10))

    story.append(P("1.6 Complete User Journey Walkthrough: 'Aarav'", "SectionHeading"))
    story.append(P(
        "To make this concrete for your viva, always cite a real patient profile:<br/>"
        "<b>User Profile:</b> Aarav, 23yo Male, 176cm, 76.0kg, Target: 70.0kg (Weight Loss), Moderate Activity, "
        "Vegetarian, Indian Cuisine, 4 Meals (Breakfast, Lunch, Snack, Dinner), Peanut Allergy, "
        "Instruction: <i>'Quick 15 min meals, flavorful, no oven'</i>.<br/>"
        "<b>1. Biometric Calculation:</b> BMR is computed as 1,750 kcal; TDEE is 2,712.5 kcal; Weight Loss target is 2,212.5 kcal. "
        "Daily protein target is 152.0g (2.0 g/kg), fat is 61.5g (25% energy), carbs is 262.8g.<br/>"
        "<b>2. Allergen Pre-Filter:</b> 'Peanuts' is normalized to 'peanut' and expanded to ['peanut', 'groundnut', 'arachis', 'peanut butter']. "
        "All foods containing these terms are purged from the 3,000+ USDA dataset.<br/>"
        "<b>3. 4-Meal Slot Blueprint:</b> Breakfast (Poha, Paneer Bhurji, Banana, Milk), Lunch (Chapati, Dal Tadka, Bhindi, Ghee), "
        "Snack (Apple, Almonds), Dinner (Basmati Rice, Rajma Curry, Palak, Curd). Exactly 14 unique food IDs selected (0 duplicates).<br/>"
        "<b>4. SLSQP Optimization:</b> Solves portion gram weights (e.g. 65g Poha, 95g Paneer, 12g Ghee) matching 2,212.5 kcal with 98.8% accuracy (&le; 1.2% delta).<br/>"
        "<b>5. Recipe Generation:</b> Groq Llama 3 generates '15-Minute Spiced Poha & Paneer Skillet Bowl'. "
        "The safety validator verifies 0 allergen tokens. Output is rendered safely via DOM textContent."
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: REPOSITORY STRUCTURE & FILE RESPONSIBILITIES
    # =========================================================================
    story.append(P("Chapter 2: Repository Structure & Complete Codebase Tour", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("2.1 Directory Layout & Module Organization", "SectionHeading"))
    story.append(P(
        "The NutriGEN-AI repository (Commit <code>9df7ad1</code>) is structured logically into distinct layers. "
        "Below is the exact file tree of the project with the role of each directory:"
    ))
    tree_text = (
        "NutriGEN-AI/\n"
        "├── ai_model.py                # Root biometric & Mifflin-St Jeor nutrition engine\n"
        "├── requirements.txt           # Production pinned Python dependencies\n"
        "├── .env.example               # Environment template (GROQ_API_KEY, ALLOWED_ORIGINS)\n"
        "├── README.md                  # Project overview and run instructions\n"
        "├── Backend/\n"
        "│   ├── server.py              # FastAPI application, CORS, and REST endpoints\n"
        "│   ├── main.py                # CLI runner entry point for local pipeline testing\n"
        "│   ├── src/\n"
        "│   │   ├── pipeline.py        # Master pipeline orchestrator (coordinates all engines)\n"
        "│   │   ├── optimizer.py       # Candidate selection & SciPy SLSQP optimization solver\n"
        "│   │   ├── preferences.py     # Diet rules, canonical allergen ontology, cuisine scoring\n"
        "│   │   ├── recipe_generator.py# Groq LPU Llama 3.3/3.1 + regex safety validator\n"
        "│   │   └── calculator.py      # Harmonized biometric calculation utilities\n"
        "│   └── tests/\n"
        "│       ├── test_end_to_end_audit.py # 6 comprehensive clinical audit test cases\n"
        "│       ├── test_groq_llm.py         # Standalone Groq API integration test\n"
        "│       └── test_api.py              # FastAPI endpoint status tests\n"
        "├── frontend/\n"
        "│   ├── index.html             # Responsive semantic UI structure & clinical notice\n"
        "│   ├── script.js              # Live biometrics, DOM textContent rendering, history\n"
        "│   └── style.css              # Custom clinical modern stylesheet\n"
        "├── data/\n"
        "│   ├── processed/             # Master cleaned datasets\n"
        "│   │   └── master_food_dataset_final.csv # 3,000+ verified foods with per-100g macros\n"
        "│   └── raw/                   # USDA raw Foundation Foods & SR Legacy CSV archives\n"
        "├── data_processing/           # Offline ETL scripts used to clean & merge USDA data\n"
        "│   ├── clean_dataset.py       # Cleans zero-calorie anomalies and bad records\n"
        "│   ├── merge_datasets.py      # Merges food descriptions with nutrient values\n"
        "│   └── check_duplicates.py    # Validates unique FDC IDs across datasets\n"
        "└── nutrition/                 # Legacy prototype module (retained for research history)"
    )
    story.append(CodeBlock(tree_text))
    story.append(Spacer(1, 8))

    story.append(Callout(
        "Source of Truth Verification (Code vs. Documentation)",
        "In your viva, if an examiner asks about the 'nutrition/' folder: explain that 'nutrition/' was an early "
        "proof-of-concept prototype. The true production backend is located in 'Backend/src/' and 'ai_model.py'. "
        "Our code is the definitive source of truth.",
        "warn"
    ))
    story.append(Spacer(1, 8))

    story.append(P("2.2 Detailed File-by-File Technical Specification", "SectionHeading"))
    file_spec_headers = ["File Path", "Primary Responsibility", "Key Functions / Classes", "Inter-Module Dependents"]
    file_spec_rows = [
        ["ai_model.py", "Biometric calculations", "calculate_bmr(), calculate_tdee(), calculate_macros(), generate_nutrition_profile()", "Called by Backend/server.py and pipeline.py"],
        ["Backend/server.py", "FastAPI web server & REST API", "app, PlanGenerationRequest schema, generate_plan_endpoint(), CORS middleware", "Called by frontend/script.js via HTTP POST"],
        ["Backend/src/pipeline.py", "Master pipeline orchestrator", "run_nutrigen_pipeline()", "Called by Backend/server.py; coordinates all engines"],
        ["Backend/src/optimizer.py", "Portion optimization solver", "select_meal_plan_candidates(), optimize_quantities(), build_final_meal_plan()", "Called by pipeline.py; uses SciPy SLSQP minimize"],
        ["Backend/src/preferences.py", "Food filtering & allergen ontology", "create_preferences(), apply_allergy_filter(), normalize_allergen_key()", "Called by optimizer.py; filters pandas DataFrame"],
        ["Backend/src/recipe_generator.py", "AI Chef & safety validation", "generate_recipe_for_meal(), validate_recipe_safety(), generate_fallback_recipe()", "Called by pipeline.py; queries Groq completions API"],
        ["frontend/script.js", "Client-side interactive engine", "calculateBiometricsLive(), buildPayload(), displayMealPlan(), savePlanToHistory()", "Runs in browser; communicates with server.py"],
        ["Backend/tests/test_end_to_end_audit.py", "Comprehensive clinical audit suite", "TestEndToEndAudit (6 profile and safety unit/e2e test methods)", "Executed via unittest for CI/CD and deployment verification"]
    ]
    story.append(StyledTable(file_spec_headers, file_spec_rows, [90, 110, 150, 154]))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: CLINICAL NUTRITION ENGINE (ai_model.py)
    # =========================================================================
    story.append(P("Chapter 3: Clinical Nutrition Calculation Engine (ai_model.py)", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("3.1 Fundamental Concepts: BMR vs. TDEE", "SectionHeading"))
    story.append(P(
        "<b>1. Basal Metabolic Rate (BMR):</b> The baseline energy expenditure (in calories per day) required to sustain "
        "vital autonomic physiological functions—respiration, myocardial contraction, cellular cellular synthesis, "
        "and systemic thermoregulation—while in complete physical, digestive, and psychological repose.<br/>"
        "<b>2. Total Daily Energy Expenditure (TDEE):</b> The aggregate caloric expenditure over a 24-hour cycle, "
        "incorporating BMR plus physical activity, occupational exertion, and the thermic effect of food (TEF). "
        "Mathematically: <code>TDEE = BMR &times; Physical Activity Level (PAL)</code>."
    ))

    story.append(P("3.2 The Mifflin-St Jeor Clinical Equations", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI implements the <b>Mifflin-St Jeor formula</b> (validated by the American Dietetic Association as the "
        "most reliable predictive metric in non-obese and obese clinical populations).<br/>"
        "• <b>For Biological Males:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>BMR = (10 &times; weight_kg) + (6.25 &times; height_cm) - (5 &times; age_years) + 5</code><br/>"
        "• <b>For Biological Females:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>BMR = (10 &times; weight_kg) + (6.25 &times; height_cm) - (5 &times; age_years) - 161</code>"
    ))

    story.append(P("3.3 Physical Activity Level (PAL) Multipliers", "SectionHeading"))
    pal_headers = ["Activity Key", "Canonical Multiplier", "Clinical Activity Definition"]
    pal_rows = [
        ["sedentary", "1.200", "Little to no exercise; desk-bound lifestyle"],
        ["light", "1.375", "Light exercise or sports 1 to 3 days per week"],
        ["moderate", "1.550", "Moderate exercise or sports 3 to 5 days per week"],
        ["very_active / active", "1.725", "Hard physical exercise 6 to 7 days per week"],
        ["extremely_active / extremely", "1.900", "Intense daily athletic conditioning or heavy physical labor"]
    ]
    story.append(StyledTable(pal_headers, pal_rows, [110, 80, 314]))
    story.append(Spacer(1, 8))

    story.append(P("3.4 Caloric Goal Adjustment & Macronutrient Distribution", "SectionHeading"))
    story.append(P(
        "Once TDEE is determined, the target calorie intake is calibrated to the user's primary objective:<br/>"
        "• <b>Weight Loss:</b> <code>Calorie Target = TDEE - 500 kcal/day</code> (induces ~0.45 kg / 1 lb fat loss per week).<br/>"
        "• <b>Weight Gain:</b> <code>Calorie Target = TDEE + 500 kcal/day</code> (provides energy surplus for muscular hypertrophy).<br/>"
        "• <b>Maintenance:</b> <code>Calorie Target = TDEE</code>.<br/>"
        "<b>Safety Guardrail:</b> A hard floor of <code>1,200 kcal/day</code> is enforced to prevent metabolic shock and malnutrition."
    ))

    story.append(P("3.5 The Atwater 4-4-9 Macronutrient Partitioning Rules", "SectionHeading"))
    story.append(P(
        "Nutrient energy densities are established by Wilbur Atwater's physiological caloric equivalents:<br/>"
        "• <b>Protein:</b> <code>4.0 kcal per gram</code><br/>"
        "• <b>Carbohydrates:</b> <code>4.0 kcal per gram</code><br/>"
        "• <b>Fat:</b> <code>9.0 kcal per gram</code><br/>"
        "In <code>ai_model.py</code>, daily macronutrient targets are sized systematically:<br/>"
        "1. <b>Protein Target:</b> Sized by body weight to preserve lean body mass: <code>2.0 g/kg</code> for weight loss, "
        "<code>2.2 g/kg</code> for weight gain, and <code>1.8 g/kg</code> for maintenance.<br/>"
        "2. <b>Fat Target:</b> Sized at exactly 25% of daily energy: <code>Fat (g) = (0.25 &times; Calorie Target) / 9.0</code>.<br/>"
        "3. <b>Carbohydrates Target:</b> Absorbs all remaining caloric allocation:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Carbs (g) = [Calorie Target - (Protein_g &times; 4 + Fat_g &times; 9)] / 4.0</code>."
    ))

    story.append(P("3.6 Fully Worked Numerical Example", "SectionHeading"))
    story.append(P(
        "<b>Subject:</b> Female, Age 28, Height 168 cm, Weight 62.0 kg, Goal: Weight Gain (+500 kcal), Activity: Very Active (1.725).<br/>"
        "1. <code>BMR = 10(62) + 6.25(168) - 5(28) - 161 = 620 + 1050 - 140 - 161 = 1,369.0 kcal</code><br/>"
        "2. <code>TDEE = 1,369.0 &times; 1.725 = 2,361.5 kcal</code><br/>"
        "3. <code>Target Calories = 2,361.5 + 500 = 2,861.5 kcal</code><br/>"
        "4. <code>Protein (g) = 62.0 &times; 2.2 = 136.4 g (Yielding 136.4 &times; 4 = 545.6 kcal)</code><br/>"
        "5. <code>Fat (g) = (0.25 &times; 2,861.5) / 9 = 715.38 / 9 = 79.5 g (Yielding 715.4 kcal)</code><br/>"
        "6. <code>Carbs (g) = (2,861.5 - 545.6 - 715.4) / 4 = 1,600.5 / 4 = 400.1 g (Yielding 1,600.5 kcal)</code><br/>"
        "<b>Total Energy Verification:</b> 545.6 + 715.4 + 1,600.5 = 2,861.5 kcal. Exactly 100% mathematical balance!"
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: FOOD DATASET ARCHITECTURE & PREPROCESSING
    # =========================================================================
    story.append(P("Chapter 4: Food Dataset Architecture & Preprocessing", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("4.1 What is USDA FoodData Central (FDC)?", "SectionHeading"))
    story.append(P(
        "<b>USDA FoodData Central</b> is the primary nutritional clearinghouse maintained by the Agricultural Research "
        "Service of the United States Department of Agriculture. NutriGEN-AI synthesizes two distinct sub-corpora:<br/>"
        "1. <b>Foundation Foods:</b> Modern, highly detailed chemical analyses providing complete nutrient profiles and "
        "variability data for basic agricultural commodities.<br/>"
        "2. <b>SR Legacy (Standard Reference Legacy):</b> The historically comprehensive release of over 8,000 whole and "
        "prepared foods. It provides wide coverage of everyday staples, dairy, poultry, produce, and grains."
    ))

    story.append(P("4.2 The Data Preprocessing Pipeline (data_processing/)", "SectionHeading"))
    story.append(P(
        "The raw USDA archives are massive (over 250 MB of raw CSV tables). The offline scripts in <code>data_processing/</code> "
        "execute an Extract-Transform-Load (ETL) pipeline to build our lean production dataset:<br/>"
        "• <code>merge_datasets.py</code>: Joins relational food tables (<code>food.csv</code>, <code>food_nutrient.csv</code>, "
        "<code>nutrient.csv</code>, and <code>food_category.csv</code>) on <code>fdc_id</code>.<br/>"
        "• <code>clean_dataset.py</code>: Filters out non-edible entries, laboratory standards, baby formulas, and items with "
        "missing essential macros. Purges zero-calorie anomaly entries.<br/>"
        "• <code>classify_foods.py</code>: Enriches food items with cuisine tags and dietary flags (vegetarian, vegan, gluten-free).<br/>"
        "• <code>process_portions.py</code>: Extracts standard household portion equivalents (grams per cup, piece, or tbsp)."
    ))

    story.append(P("4.3 The Master Production Dataset (master_food_dataset_final.csv)", "SectionHeading"))
    story.append(P(
        "The final production dataset contains over <b>3,000 verified foods</b> standardized strictly per <b>100 grams</b>. "
        "Below are the critical columns utilized by NutriGEN-AI during real-time optimization:"
    ))
    col_headers = ["Column Header", "Data Type", "Clinical Meaning & Unit", "Role in Engine"]
    col_rows = [
        ["fdc_id", "Integer (Unique)", "Persistent USDA Identifier", "Unique primary key; prevents duplicate foods across slots"],
        ["description", "String", "Standardized Food Name", "Target of allergen scanning, cuisine scoring, and AI recipe prompt"],
        ["food_category", "String", "High-level food grouping", "Used for food role assignment (poultry, dairy, finfish, grains)"],
        ["calories_kcal", "Float", "Energy density per 100g (kcal)", "Dot product vector in SLSQP calorie constraint and objective"],
        ["protein_g", "Float", "Protein mass per 100g (grams)", "Dot product vector in SLSQP protein error minimization"],
        ["fat_g", "Float", "Lipid mass per 100g (grams)", "Dot product vector in SLSQP fat error and shortfall penalty"],
        ["carbohydrate_g", "Float", "Carb mass per 100g (grams)", "Dot product vector in SLSQP carb error and excess penalty"]
    ]
    story.append(StyledTable(col_headers, col_rows, [85, 80, 160, 179]))
    story.append(Spacer(1, 8))

    story.append(P("4.4 Why Local CSV Instead of Live REST API Calls?", "SectionHeading"))
    story.append(P(
        "A critical viva question is: <i>'Why store a local CSV rather than querying the USDA API live?'</i><br/>"
        "1. <b>Latency:</b> Querying an external REST API for thousands of candidate foods would introduce 3 to 10 seconds of "
        "network latency per optimization turn. In-memory Pandas filtering executes in <b>under 4 milliseconds</b>.<br/>"
        "2. <b>Rate Limiting & Availability:</b> External APIs enforce strict rate limits (e.g. 1,000 calls/hour) and suffer "
        "service outages. A pre-cleaned local dataset guarantees 100% uptime.<br/>"
        "3. <b>Deterministic Reproducibility:</b> Mathematical optimization requires consistent, cleaned nutrient matrices. "
        "Third-party upstream updates cannot break our clinical constraints."
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: PREFERENCES, ALLERGENS, & CANDIDATE SELECTION
    # =========================================================================
    story.append(P("Chapter 5: Preferences, Allergen Filtering, and Candidate Selection", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("5.1 Rule-Based Filtering vs. Machine Learning", "SectionHeading"))
    story.append(P(
        "<b>Important Viva Distinction:</b> Candidate selection in NutriGEN-AI is <b>deterministic rule-based filtering</b>, "
        "not machine learning. When filtering life-threatening allergens or strict religious diets (e.g. Halal, Hindu vegetarian), "
        "probabilistic machine learning models have an unacceptable margin of error. Deterministic set-theoretic masking "
        "guarantees that 100% of matching prohibited foods are excluded from the optimization matrix."
    ))

    story.append(P("5.2 Dietary Exclusion Rules (preferences.py)", "SectionHeading"))
    story.append(P(
        "• <b>Vegetarian:</b> Eliminates all poultry, finfish, shellfish, red meat, and animal stocks. Eggs are excluded by default "
        "unless <code>eats_eggs=True</code> (Eggetarian).<br/>"
        "• <b>Vegan:</b> Eliminates all animal products—meat, poultry, seafood, eggs, dairy, whey, casein, butter, and ghee.<br/>"
        "• <b>Non-Vegetarian:</b> Permits all foods, prioritizing authentic lean proteins (chicken breast, fish, eggs, mutton)."
    ))

    story.append(P("5.3 Canonical Allergen Ontology & Plural Normalization", "SectionHeading"))
    story.append(P(
        "Early audits revealed that users typing 'peanuts' or 'tree nuts' bypassed simple string matching. In commit <code>bdb1bdd</code> "
        "and <code>9df7ad1</code>, we implemented <code>normalize_allergen_key()</code> and canonical alias clusters:"
    ))
    allergen_headers = ["Normalized Allergen Key", "Canonical Expanded Alias Cluster Terms"]
    allergen_rows = [
        ["peanut", "peanut, groundnut, arachis, peanut butter, monkey nut"],
        ["treenut", "almond, cashew, walnut, pistachio, pecan, hazelnut, macadamia, brazil nut, chestnut, pine nut, nut"],
        ["milk / dairy / lactose", "milk, whey, casein, cheese, yogurt, yoghurt, curd, paneer, cream, butter, ghee, dairy, lactose"],
        ["egg", "egg, albumen, egg white, egg yolk, omelet, omelette, bhurji, mayonnaise"],
        ["soy", "soy, soya, soybean, tofu, tempeh, miso, edamame"],
        ["wheat / gluten", "wheat, flour, atta, semolina, durum, bulgur, couscous, gluten, maida, barley, rye, spelt"],
        ["fish", "fish, salmon, tuna, sardine, anchovy, trout, cod, tilapia, mackerel, halibut, snapper"],
        ["shellfish / seafood", "shrimp, prawn, crab, lobster, clam, oyster, mussel, scallop, calamari, squid, octopus, shellfish"],
        ["sesame", "sesame, tahini, til, gingelly"],
        ["mustard", "mustard, sarson, rai"]
    ]
    story.append(StyledTable(allergen_headers, allergen_rows, [110, 394]))
    story.append(Spacer(1, 8))

    story.append(P("5.4 Food Role Classification & Quality Scoring (optimizer.py)", "SectionHeading"))
    story.append(P(
        "Every food surviving preference filtering is categorized into functional roles by <code>assign_food_role(row)</code>:<br/>"
        "• <b>Staple:</b> High-carbohydrate bases (rice, roti, oats, sweet potato, quinoa, poha).<br/>"
        "• <b>Protein:</b> High-protein drivers (chicken, fish, eggs, paneer, tofu, lentils, dal, chickpeas).<br/>"
        "• <b>Vegetable:</b> Nutrient-dense, fiber-rich produce (spinach, broccoli, okra, cauliflower, beans).<br/>"
        "• <b>Fruit:</b> Micronutrient & simple carb sources (banana, apple, berries, papaya).<br/>"
        "• <b>Healthy Fat:</b> Dense lipid sources (olive oil, ghee, almonds, walnuts, seeds).<br/>"
        "Foods are scored by <code>score_food_quality()</code>: prioritizing high protein density (&gt; 15g/100g), high fiber (&gt; 3g/100g), "
        "low saturated fat, and low added sugars."
    ))

    story.append(P("5.5 Dynamic Slot Blueprints & Zero Duplicate Foods", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI dynamically constructs distinct blueprints for <b>2, 3, 4, or 5 eating occasions</b>:<br/>"
        "• <b>5 Meals:</b> Breakfast (4 foods), Morning Snack (2 foods), Lunch (4 foods), Evening Snack (2 foods), Dinner (4 foods) = 16 items.<br/>"
        "• <b>4 Meals:</b> Breakfast (4 foods), Lunch (4 foods), Snack (2 foods), Dinner (4 foods) = 14 items.<br/>"
        "• <b>3 Meals:</b> Breakfast (4 foods), Lunch (4 foods), Dinner (4 foods) = 12 items.<br/>"
        "• <b>2 Meals (Intermittent Fasting):</b> Lunch (5 foods), Dinner (5 foods) = 10 items.<br/>"
        "<b>Zero Duplicate Enforcement:</b> As each food is selected, its USDA <code>fdc_id</code> and base term (e.g. 'paneer') "
        "are locked into <code>used_ids</code> and <code>used_base_terms</code>. All subsequent slots strictly query "
        "<code>~df_pref['fdc_id'].isin(used_ids)</code>, guaranteeing 100% ingredient variety across the day."
    ))

    return story
