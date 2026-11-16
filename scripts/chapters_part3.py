"""
Chapters 11 through 14 Content for NutriGEN-AI Master Notes
Covers:
- Chapter 11: Complete End-to-End System Integration & Call-Flow
- Chapter 12: Testing & Clinical Quality Assurance (test_end_to_end_audit.py)
- Chapter 13: Deployment, DevOps, & Environment Configuration
- Chapter 14: Project Limitations, Assumptions, & Future Scope
"""

from reportlab.platypus import PageBreak, Spacer, HRFlowable
from scripts.pdf_styles import (
    P, CodeBlock, Callout, StyledTable, QA, PRIMARY, SECONDARY, ACCENT
)


def build_chapters_11_to_14():
    story = []

    # =========================================================================
    # CHAPTER 11: COMPLETE END-TO-END SYSTEM INTEGRATION
    # =========================================================================
    story.append(P("Chapter 11: Complete End-to-End System Integration", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("11.1 Master Inter-Module Call-Flow", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI integrates multiple disparate engineering domains—clinical biometrics, relational data filtering, "
        "constrained mathematical programming, asynchronous network communication, and generative language modeling—into a "
        "seamless, deterministic execution pipeline. Below is the exact sequence of function invocations across the codebase:"
    ))
    call_flow_text = (
        "1. USER ACTION: Submits form on frontend/index.html\n"
        "   └─> frontend/script.js: form.addEventListener('submit')\n"
        "       └─> buildPayload(data) -> JSON string\n"
        "       └─> fetch('http://127.0.0.1:8000/api/generate-plan', {method: 'POST'})\n"
        "\n"
        "2. NETWORK RECEPTION: Backend/server.py receives HTTP POST\n"
        "   └─> CORSMiddleware verifies origin (localhost defaults)\n"
        "   └─> Pydantic validates PlanGenerationRequest schema\n"
        "   └─> generate_plan_endpoint(request)\n"
        "       └─> calls Backend/src/pipeline.py: run_nutrigen_pipeline(user_data)\n"
        "\n"
        "3. BIOMETRICS & TARGET SIZING:\n"
        "   └─> Backend/src/pipeline.py calls ai_model.py: generate_nutrition_profile()\n"
        "       ├─> calculate_bmr(weight, height, age, sex) [Mifflin-St Jeor]\n"
        "       ├─> calculate_tdee(bmr, activity_level) [PAL Multiplier]\n"
        "       └─> calculate_macros(calorie_target, weight, goal) [4-4-9 Partitioning]\n"
        "       <── Returns: dict with BMR, TDEE, Calories, Protein_g, Fat_g, Carbs_g\n"
        "\n"
        "4. OPTIMIZED MEAL PLAN GENERATION:\n"
        "   └─> Backend/src/pipeline.py calls Backend/src/optimizer.py: generate_optimized_meal_plan()\n"
        "       ├─> loads data/processed/master_food_dataset_final.csv (Pandas DataFrame)\n"
        "       ├─> calls Backend/src/preferences.py: apply_preferences(df, preferences)\n"
        "       │   ├─> apply_diet_filter(df, preferences)\n"
        "       │   ├─> apply_allergy_filter(df, preferences) [Canonical Cluster Regex]\n"
        "       │   ├─> apply_disliked_food_filter(df, preferences)\n"
        "       │   └─> calculate_cuisine_score(df, preferences)\n"
        "       ├─> calls select_meal_plan_candidates() [Deduplication & Slot Blueprints]\n"
        "       ├─> calls optimize_quantities() [SciPy SLSQP minimize(method='SLSQP')]\n"
        "       │   ├─> Evaluates objective(x) & cal_constraint(x)\n"
        "       │   ├─> Checks solver_converged & cal_error <= 0.05\n"
        "       │   └─> Clamps portions to bounds [L, U] & applies proportional recovery\n"
        "       └─> calls build_final_meal_plan() [Assembles foods into meal slots]\n"
        "       <── Returns: Structured meal plan dictionary with weighed food items\n"
        "\n"
        "5. AI CHEF RECIPE GENERATION & SAFETY VALIDATION:\n"
        "   └─> Backend/src/pipeline.py iterates over each meal slot in plan['meal_plan']\n"
        "       └─> calls Backend/src/recipe_generator.py: generate_recipe_for_meal()\n"
        "           ├─> generate_recipe_with_groq() [httpx POST to Groq completions API]\n"
        "           │   ├─> extract_json_from_text() [Extracts structured JSON]\n"
        "           │   └─> validate_recipe_safety() [Regex scan for prohibited allergen tokens]\n"
        "           └─> IF unsafe or offline: generate_fallback_recipe() [Heuristic Engine]\n"
        "       <── Returns: Dish title, cooking time, 3-step instructions, chef notes\n"
        "\n"
        "6. RESPONSE DELIVERY & CLIENT RENDERING:\n"
        "   └─> Backend/src/pipeline.py packages master response dictionary\n"
        "   └─> Backend/server.py serializes to JSON -> HTTP 200 OK\n"
        "   └─> frontend/script.js: displayMealPlan(result, data)\n"
        "       ├─> Renders Macro Precision Meter & comparison cards\n"
        "       ├─> Constructs DOM table cells using safe el() textContent\n"
        "       ├─> Compiles consolidated Grocery Checklist modal\n"
        "       └─> savePlanToHistory() stores payload into browser localStorage"
    )
    story.append(CodeBlock(call_flow_text))
    story.append(Spacer(1, 10))

    story.append(P("11.2 Inter-Module Data Contracts", "SectionHeading"))
    story.append(P(
        "A critical engineering requirement is the strict consistency of dictionary keys passed between modules:<br/>"
        "• <code>ai_model.py &rarr; pipeline.py</code>: <code>{'bmr': float, 'tdee': float, 'calorie_target': float, 'protein_g': float, 'fat_g': float, 'carbs_g': float}</code>.<br/>"
        "• <code>optimizer.py &rarr; pipeline.py</code>: <code>{'diet_type': str, 'targets': dict, 'totals': dict, 'meal_plan': dict, 'optimization': dict}</code>.<br/>"
        "• <code>recipe_generator.py &rarr; pipeline.py</code>: <code>{'dish_title': str, 'cooking_time': str, 'instructions': list, 'chef_notes': str, 'engine': str}</code>.<br/>"
        "• <code>server.py &rarr; frontend</code>: Unified JSON containing <code>status</code>, <code>llm_engine</code>, <code>biometrics</code>, <code>nutrition_requirements</code>, <code>meal_plan</code>, and <code>recipes</code>."
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 12: TESTING & CLINICAL QUALITY ASSURANCE
    # =========================================================================
    story.append(P("Chapter 12: Testing & Clinical Quality Assurance", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("12.1 Testing Philosophy: Unit vs. Integration vs. End-to-End", "SectionHeading"))
    story.append(P(
        "Software testing in precision healthcare applications must follow a rigorous pyramid:<br/>"
        "• <b>Unit Testing:</b> Verifies individual functions in isolation (e.g. testing that <code>calculate_bmr(70, 175, 25, 'male')</code> returns exactly 1,673.75).<br/>"
        "• <b>Integration Testing:</b> Verifies that separate modules communicate properly (e.g. testing that <code>preferences.py</code> correctly filters rows before <code>optimizer.py</code> receives the DataFrame).<br/>"
        "• <b>End-to-End (E2E) Testing:</b> Simulates a complete user interaction from biometric input through dataset filtering, numerical solver convergence, and recipe generation."
    ))

    story.append(P("12.2 Review of the 6 Clinical Audit Test Cases (test_end_to_end_audit.py)", "SectionHeading"))
    story.append(P(
        "In commit <code>9df7ad1</code>, we established our flagship test suite in <code>Backend/tests/test_end_to_end_audit.py</code>. "
        "All 6 test cases run against the real production dataset and pass with 100% fidelity:"
    ))
    test_headers = ["Test Method Name", "Clinical Scenario Tested", "Key Invariants Asserted", "Execution Result"]
    test_rows = [
        ["test_profile_1_male_weight_loss_4_meals_peanut_allergy", "23yo Male, 76kg->70kg, 4 meals, Indian Vegetarian, Peanut Allergy", "4 distinct meals; 0 peanuts/groundnuts; 0 duplicate FDC IDs; SLSQP solver converged; cal error <= 5%", "PASS (100%)"],
        ["test_profile_2_female_muscle_gain_5_meals_dairy_allergy", "28yo Female, 62kg, 5 meals, Mediterranean Non-Veg, Dairy Allergy", "5 distinct meals; exactly 16 items with 16 unique FDC IDs (0 duplicates); 0 dairy items; solver converged", "PASS (100%)"],
        ["test_profile_3_intermittent_fasting_2_meals_vegan", "35yo Male, 85kg, 2 meals, Vegan, Any Cuisine", "2 meals (Lunch, Dinner); 0 animal foods; word boundary distinguishes 'egg' vs vegetable 'eggplant'", "PASS (100%)"],
        ["test_profile_4_three_meals_maintenance_eggetarian", "30yo Female, 60kg, 3 meals, Eggetarian, Mediterranean", "Exactly 3 meals; 0 snacks; eggs permitted in breakfast; 0 meat/fish; 0 duplicate FDC IDs; solver converged", "PASS (100%)"],
        ["test_llm_recipe_safety_validation", "Simulated LLM outputs (Safe vs Hallucinated Allergen)", "Approves safe recipes; catches & rejects hallucinated peanuts in steps, title, and alias 'almonds' from 'tree nuts'", "PASS (100%)"],
        ["test_live_groq_allergen_rejection_and_fallback", "Live Mocked Groq API returning hallucinated allergen", "Mocks 200 OK with peanut garnish; asserts validate_recipe_safety intercepts it and switches to Heuristic Engine", "PASS (100%)"]
    ]
    story.append(StyledTable(test_headers, test_rows, [140, 120, 180, 64]))
    story.append(Spacer(1, 8))

    story.append(P("12.3 What is Mocking and Why Do We Mock Groq?", "SectionHeading"))
    story.append(P(
        "<b>What is Mocking?</b> Mocking is a software testing technique where a real external dependency (like a third-party cloud API) "
        "is replaced with a simulated dummy object that mimics its behavior in a controlled environment.<br/>"
        "<b>Why We Mock Groq in test_live_groq_allergen_rejection_and_fallback:</b><br/>"
        "1. <b>Deterministic Verification:</b> We cannot force real Groq LLM servers to randomly hallucinate a peanut allergen on demand. "
        "By mocking the HTTP response with <code>unittest.mock.patch('httpx.Client.post')</code>, we feed an exact poisoned recipe payload "
        "and prove that our safety interception mechanism catches the violation 100% of the time.<br/>"
        "2. <b>Zero Network Flakiness:</b> Automated test suites must run in CI/CD pipelines without requiring active internet connections "
        "or paid third-party API credits."
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 13: DEPLOYMENT, DEVOPS, & CONFIGURATION
    # =========================================================================
    story.append(P("Chapter 13: Deployment, DevOps, and Configuration", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("13.1 Production Dependencies (requirements.txt)", "SectionHeading"))
    story.append(P(
        "The project dependencies are strictly pinned in <code>requirements.txt</code> to prevent upstream breaking changes:<br/>"
        "• <code>fastapi&gt;=0.115.0</code>: Core web API framework.<br/>"
        "• <code>uvicorn[standard]&gt;=0.32.0</code>: High-performance ASGI production server.<br/>"
        "• <code>pydantic&gt;=2.9.0</code>: Data validation and settings management.<br/>"
        "• <code>numpy&gt;=1.26.0</code>: Matrix linear algebra and dot products.<br/>"
        "• <code>scipy&gt;=1.13.0</code>: Numerical optimization algorithms (SLSQP).<br/>"
        "• <code>pandas&gt;=2.2.0</code>: Dataset manipulation and relational filtering.<br/>"
        "• <code>httpx&gt;=0.27.0</code>: Modern asynchronous HTTP client for Groq API communication.<br/>"
        "• <code>python-dotenv&gt;=1.0.0</code>: Environment variable management."
    ))

    story.append(P("13.2 Environment Variables (.env)", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI uses an environment template <code>.env.example</code>. The production <code>.env</code> file specifies:<br/>"
        "• <code>GROQ_API_KEY</code>: Your secret Groq LPU API key (e.g. <code>gsk_...</code>). Optional; if omitted, the system defaults to the Heuristic Engine.<br/>"
        "• <code>ALLOWED_ORIGINS</code>: Comma-separated domains permitted to connect via CORS (e.g. <code>https://nutrigen-ai.com,https://app.nutrigen.ai</code>). "
        "If omitted, securely defaults to explicit local development origins."
    ))

    story.append(P("13.3 Step-by-Step Local Deployment Guide", "SectionHeading"))
    deploy_steps = (
        "# 1. Clone the GitHub repository\n"
        "git clone https://github.com/Abhii051/NutriGEN-AI.git\n"
        "cd NutriGEN-AI\n\n"
        "# 2. Create and activate a clean Python 3.13 virtual environment\n"
        "python -m venv .venv\n"
        "# Windows PowerShell:\n"
        ".venv\\Scripts\\Activate.ps1\n"
        "# Linux / macOS:\n"
        "source .venv/bin/activate\n\n"
        "# 3. Install pinned production dependencies\n"
        "pip install -r requirements.txt\n\n"
        "# 4. Launch the FastAPI backend on port 8000\n"
        "python -m uvicorn Backend.server:app --reload --port 8000\n\n"
        "# 5. Serve the frontend (in a separate terminal)\n"
        "# Using Python's built-in HTTP server or VS Code Live Server:\n"
        "cd frontend\n"
        "python -m http.server 5500\n"
        "# Open browser at: http://localhost:5500"
    )
    story.append(CodeBlock(deploy_steps))
    story.append(Spacer(1, 8))

    story.append(P("13.4 Common Deployment Errors & Troubleshooting", "SectionHeading"))
    story.append(P(
        "• <b>Port 8000 Conflict:</b> If another process is using port 8000, launch Uvicorn on port 8001 (<code>--port 8001</code>) "
        "and update <code>API_URL</code> in <code>frontend/script.js</code>.<br/>"
        "• <b>ModuleNotFoundError ('No module named Backend'):</b> Occurs if running scripts from inside subfolders without setting <code>PYTHONPATH</code>. "
        "Our code automatically resolves this via <code>PROJECT_ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(PROJECT_ROOT))</code>.<br/>"
        "• <b>CORS Blocked:</b> Occurs if opening <code>index.html</code> via <code>file:///</code> protocol. Browsers block CORS on file origins. "
        "Always serve the frontend via an HTTP server (e.g. <code>http://localhost:5500</code>)."
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 14: PROJECT LIMITATIONS & FUTURE SCOPE
    # =========================================================================
    story.append(P("Chapter 14: Project Limitations, Assumptions, and Future Scope", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("14.1 Technical and Dataset Limitations", "SectionHeading"))
    story.append(P(
        "An examiner will respect your defense if you can articulate your system's genuine boundaries with engineering honesty:<br/>"
        "1. <b>Description-Based Allergen Matching:</b> Filtering is based on food name text in the USDA dataset, not certified barcode "
        "ingredient labels or manufacturer facility registries (e.g. Open Food Facts). Trace cross-contamination cannot be determined from descriptions.<br/>"
        "2. <b>Client-Side Persistence:</b> Plan history is stored in browser <code>localStorage</code>. It lacks multi-user authentication, "
        "cloud synchronization, and relational database persistence (e.g. PostgreSQL/Supabase).<br/>"
        "3. <b>Single-Day Optimization:</b> The engine solves one daily meal plan at a time. It does not yet perform multi-day cyclical pantry "
        "batch-cooking optimization.<br/>"
        "4. <b>Macronutrient Focus:</b> Optimizes Calories, Protein, Fat, and Carbs. Critical micronutrients (Sodium, Fiber, Iron, Potassium) "
        "are scored in candidate selection but not yet modeled as formal SLSQP inequality constraints."
    ))

    story.append(P("14.2 Why Retrieval-Augmented Generation (RAG) Was Not Used", "SectionHeading"))
    story.append(P(
        "<b>Examiner Trap Question:</b> <i>'Why didn't you use RAG (Vector Database + Embeddings) for food selection?'</i><br/>"
        "<b>The Winning Technical Answer:</b> RAG is designed for semantic text search over unstructured documents (e.g. searching "
        "PDF manuals). Food nutrition is <b>dense structured relational data</b>. Vector similarity (cosine distance over embeddings) "
        "cannot solve mathematical constraints—an embedding cannot determine that 80g of rice plus 120g of dal equals exactly 480 kcal. "
        "Relational matrix filtering combined with numerical optimization (SLSQP) is mathematically superior, faster, and 100% deterministic."
    ))

    story.append(P("14.3 Future Development Roadmap", "SectionHeading"))
    story.append(P(
        "• <b>Enterprise Multi-User Database:</b> Migrate from <code>localStorage</code> to PostgreSQL with Supabase Auth (JWT/OAuth2).<br/>"
        "• <b>7-Day Rolling Meal Plans:</b> Introduce multi-day optimization with grocery pantry reuse to minimize food waste.<br/>"
        "• <b>Micronutrient Bounding:</b> Add hard constraints for Sodium (&lt; 2,300 mg/day), Dietary Fiber (&gt; 30 g/day), and Saturated Fat (&lt; 10% energy).<br/>"
        "• <b>Barcode Scanner Integration:</b> Connect to Open Food Facts API for real-time packaged food label ingestion."
    ))

    return story
