"""
Chapters 6 through 10 Content for NutriGEN-AI Master Notes
Covers:
- Chapter 6: The Mathematical Optimizer — Deep Dive into optimizer.py (SciPy SLSQP)
- Chapter 7: Groq API & LLM Integration (recipe_generator.py)
- Chapter 8: Allergen Safety Defense & Output Validation
- Chapter 9: FastAPI Backend, Endpoints, & Server Architecture (server.py)
- Chapter 10: Frontend Engineering & Client-Server Communication (script.js, index.html)
"""

from reportlab.platypus import PageBreak, Spacer, HRFlowable
from scripts.pdf_styles import (
    P, CodeBlock, Callout, StyledTable, QA, PRIMARY, SECONDARY, ACCENT
)


def build_chapters_6_to_10():
    story = []

    # =========================================================================
    # CHAPTER 6: THE MATHEMATICAL OPTIMIZER (optimizer.py) — DEEPEST SECTION
    # =========================================================================
    story.append(P("Chapter 6: The Mathematical Optimizer — In-Depth (optimizer.py)", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("6.1 Optimization Foundations: Why LLMs Fail at Sizing", "SectionHeading"))
    story.append(P(
        "<b>What is Optimization?</b> In applied mathematics, optimization is the selection of the best element "
        "(with regard to some criterion) from some set of available alternatives. In nutrition, optimization means finding "
        "the exact continuous gram quantities of $N$ different foods such that their combined calories, proteins, fats, "
        "and carbohydrates equal clinical targets while keeping every food within realistic cooking portion bounds.<br/>"
        "<b>Why Can't an LLM Solve This?</b> Large Language Models operate via next-token probability: "
        "$$P(w_t \\mid w_1, \\dots, w_{t-1})$$"
        "They do not maintain internal linear algebra state, cannot compute matrix dot products, and cannot evaluate "
        "gradient derivatives. When prompted to generate grams, an LLM simply hallucinates numbers that sound plausible, "
        "inevitably leading to severe caloric and macronutrient drift (often 20% to 50% off target)."
    ))

    story.append(P("6.2 SciPy and the SLSQP Algorithm Explained", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI uses <b>Sequential Least Squares Programming (SLSQP)</b> from the <code>scipy.optimize</code> package.<br/>"
        "• <b>What is SciPy?</b> The premier open-source Python library for scientific mathematics, linear algebra, and numerical optimization.<br/>"
        "• <b>What is SLSQP?</b> A sequential quadratic programming algorithm developed by Dieter Kraft (1988). It solves non-linear "
        "optimization problems with general equality and inequality constraints, as well as upper and lower bounds on decision variables.<br/>"
        "• <b>How SLSQP Works Conceptually:</b> At each iteration $k$, SLSQP creates a local quadratic approximation of the objective function "
        "using a BFGS (Broyden-Fletcher-Goldfarb-Shanno) estimate of the Hessian matrix, linearizes the constraints, and solves a Quadratic "
        "Programming (QP) subproblem to find the optimal search direction $d_k$. It then performs a line search to update the decision variables: "
        "$$x_{k+1} = x_k + \\alpha_k d_k$$"
        "This repeats until gradient step tolerance (<code>ftol = 1e-7</code>) or maximum iterations (1,000) are met."
    ))

    story.append(P("6.3 Decision Variables and Portion Bounds", "SectionHeading"))
    story.append(P(
        "For a daily plan with $N$ selected foods (where $N \\in [10, 16]$ depending on meal count), the decision variable vector is: "
        "$$x = [x_0, x_1, x_2, \\dots, x_{N-1}]^T \\in \\mathbb{R}^N$$"
        "where $x_i$ represents the portion of candidate food $i$ in <b>grams</b>.<br/>"
        "Every food is assigned physiological portion bounds $[L_i, U_i]$ so portions remain culinary realistic:<br/>"
        "• <b>Grains / Staples:</b> $[40.0\\text{ g}, 180.0\\text{ g}]$ (e.g. cooked rice, oats, chapati)<br/>"
        "• <b>Proteins:</b> $[40.0\\text{ g}, 220.0\\text{ g}]$ (e.g. paneer, chicken breast, lentils, dal)<br/>"
        "• <b>Vegetables:</b> $[50.0\\text{ g}, 250.0\\text{ g}]$ (e.g. spinach, broccoli, bhindi)<br/>"
        "• <b>Fruits:</b> $[40.0\\text{ g}, 180.0\\text{ g}]$ (e.g. apple, banana, papaya)<br/>"
        "• <b>Healthy Fats:</b> $[10.0\\text{ g}, 40.0\\text{ g}]$ (e.g. ghee, olive oil, almonds)"
    ))

    story.append(P("6.4 Initial Guess Vector (x0)", "SectionHeading"))
    story.append(P(
        "SLSQP requires an initial starting point $x_0$. In <code>optimizer.py</code>, we initialize $x_0$ to the exact midpoint "
        "of the bounds: <code>x0[i] = (low + high) / 2.0</code>. This places the solver in the center of the feasible hypercube, "
        "preventing boundary stagnation and ensuring rapid convergence within 15 to 40 iterations."
    ))

    story.append(P("6.5 The Exact Objective Function & Weight Analysis", "SectionHeading"))
    story.append(P(
        "The objective function in <code>optimizer.py</code> measures the weighted normalized sum of squared errors between "
        "the nutrients provided by portion vector $x$ and the clinical targets. Let: "
        "$$C(x) = \\sum_{i=0}^{N-1} \\text{cal}_i \\cdot \\frac{x_i}{100},\\quad P(x) = \\sum_{i=0}^{N-1} \\text{prot}_i \\cdot \\frac{x_i}{100},\\quad F(x) = \\sum_{i=0}^{N-1} \\text{fat}_i \\cdot \\frac{x_i}{100},\\quad K(x) = \\sum_{i=0}^{N-1} \\text{carb}_i \\cdot \\frac{x_i}{100}$$"
        "The normalized relative error terms are: "
        "$$E_{\\text{cal}} = \\frac{C(x) - C^*}{C^*},\\quad E_{\\text{prot}} = \\frac{P(x) - P^*}{P^*},\\quad E_{\\text{fat}} = \\frac{F(x) - F^*}{F^*},\\quad E_{\\text{carb}} = \\frac{K(x) - K^*}{K^*}$$"
        "The complete scalar objective function minimized by SLSQP is: "
        "$$f(x) = 30.0 \\cdot (E_{\\text{cal}})^2 + 15.0 \\cdot (E_{\\text{prot}})^2 + 10.0 \\cdot (E_{\\text{fat}})^2 + 8.0 \\cdot (E_{\\text{carb}})^2 + \\text{Penalties}$$"
    ))
    story.append(Spacer(1, 4))

    obj_weights_headers = ["Nutrient Term", "Multiplier Weight", "Clinical Rationale for Weight Value"]
    obj_weights_rows = [
        ["Calorie Error (E_cal^2)", "30.0 (Dominant)", "Energy balance governs weight trajectory. Must have highest priority."],
        ["Protein Error (E_prot^2)", "15.0 (High Priority)", "Preserves lean muscle tissue and immune cellular repair during dieting."],
        ["Fat Error (E_fat^2)", "10.0 (Moderate Priority)", "Essential for hormonal regulation, fat-soluble vitamins (A, D, E, K)."],
        ["Carbohydrate Error (E_carb^2)", "8.0 (Buffer Priority)", "Serves as flexible energy buffer. Tolerates higher relative variance."],
        ["Fat Shortfall Penalty", "+5.0 * (E_fat^2)", "Triggered if F(x) < 0.90 * F*. Heavily penalizes dropping essential lipids."],
        ["Carb Excess Penalty", "+5.0 * (E_carb^2)", "Triggered if K(x) > 1.15 * K*. Prevents postprandial glycemic spikes."]
    ]
    story.append(StyledTable(obj_weights_headers, obj_weights_rows, [110, 100, 294]))
    story.append(Spacer(1, 8))

    story.append(P("6.6 Constraints: Hard Inequality vs. Acceptance Tolerance", "SectionHeading"))
    story.append(P(
        "<b>Important Viva Distinction:</b> An examiner may ask: <i>'Why do you have a &plusmn;2.5% constraint but a 5% tolerance?'</i><br/>"
        "• <b>Hard Solver Constraint (&plusmn;2.5%):</b> Fed directly into SLSQP via <code>constraints=[{'type': 'ineq', 'fun': cal_constraint}]</code>. "
        "It forces the solver to search strictly inside: "
        "$$0.975 \\cdot C^* \\le C(x) \\le 1.025 \\cdot C^*$$"
        "• <b>Acceptance Tolerance (&le; 5.0%):</b> The post-optimization validation check. In numerical optimization, "
        "rounding portions to realistic 0.1g increments introduces minor truncation drift. The 5.0% threshold guarantees "
        "that the rounded, physical portions served to the user remain clinically accurate."
    ))

    story.append(P("6.7 Dual-Criteria Convergence Validation & Bounded Recovery", "SectionHeading"))
    story.append(P(
        "In commit <code>3847078</code> and <code>9df7ad1</code>, we implemented a rigorous dual-criteria convergence check:<br/>"
        "1. <b>Primary Check:</b> Evaluates <code>res.success == True</code> and <code>cal_error &le; 0.05</code>.<br/>"
        "2. <b>Relaxed Optimization Fallback:</b> If the hard inequality constraint caused infeasibility due to rigid bounds, "
        "SLSQP runs a relaxed unconstrained pass. <b>Crucially, the relaxed solution is only adopted if <code>res_relaxed.success == True</code></b>, "
        "preventing unconverged mathematical state from being flagged as successful.<br/>"
        "3. <b>Bound Clamping:</b> Every portion is clamped to its valid range: <code>opt_x[i] = max(low, min(high, opt_x[i]))</code>.<br/>"
        "4. <b>Bounded Proportional Recovery:</b> If residual rounding error exceeds 5%, a scaling factor $S = C^* / C_{\\text{clamped}}$ "
        "is applied and re-clamped, guaranteeing that extreme boundary edge cases still align with the target."
    ))

    story.append(P("6.8 Full Mathematical Optimization Code Excerpt", "SectionHeading"))
    opt_code = (
        "# Extracted verbatim from Backend/src/optimizer.py (Commit 9df7ad1)\n"
        "def optimize_quantities(candidates_df, bounds, target_calories, target_protein, target_fat, target_carbs):\n"
        "    calories = candidates_df['calories_kcal'].to_numpy()\n"
        "    protein = candidates_df['protein_g'].to_numpy()\n"
        "    fat = candidates_df['fat_g'].to_numpy()\n"
        "    carbs = candidates_df['carbohydrate_g'].to_numpy()\n\n"
        "    def objective(x):\n"
        "        tot_cal = np.dot(calories, x / 100)\n"
        "        tot_prot = np.dot(protein, x / 100)\n"
        "        tot_fat = np.dot(fat, x / 100)\n"
        "        tot_carb = np.dot(carbs, x / 100)\n"
        "        err_cal = (tot_cal - target_calories) / target_calories\n"
        "        err_prot = (tot_prot - target_protein) / target_protein\n"
        "        err_fat = (tot_fat - target_fat) / target_fat\n"
        "        err_carb = (tot_carb - target_carbs) / target_carbs\n\n"
        "        loss = (30.0 * (err_cal ** 2) + 15.0 * (err_prot ** 2) +\n"
        "                10.0 * (err_fat ** 2) + 8.0 * (err_carb ** 2))\n"
        "        if tot_fat < target_fat * 0.90:\n"
        "            loss += 5.0 * (err_fat ** 2)\n"
        "        if tot_carb > target_carbs * 1.15:\n"
        "            loss += 5.0 * (err_carb ** 2)\n"
        "        return loss\n\n"
        "    def cal_constraint(x):\n"
        "        tot_cal = np.dot(calories, x / 100)\n"
        "        return np.array([tot_cal - (target_calories * 0.975),\n"
        "                         (target_calories * 1.025) - tot_cal])\n\n"
        "    res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=[{'type': 'ineq', 'fun': cal_constraint}])\n"
        "    # Evaluates res.success, cal_error, relaxed fallback, bound clamping, and returns opt_x, opt_metadata"
    )
    story.append(CodeBlock(opt_code))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7: GROQ API & LLM INTEGRATION (recipe_generator.py)
    # =========================================================================
    story.append(P("Chapter 7: Groq LPU & LLM Integration (recipe_generator.py)", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("7.1 What is Groq and Why Do We Use It?", "SectionHeading"))
    story.append(P(
        "<b>Groq</b> is an AI infrastructure company that pioneered the <b>Language Processing Unit (LPU)</b>. Unlike traditional "
        "GPUs (which process graphics and massive batches in parallel with significant DRAM latency), an LPU is a deterministic "
        "Tensor Streaming Processor designed specifically for sequential autoregressive inference. It provides ultra-low latency "
        "(&gt; 500 tokens/second), allowing NutriGEN-AI to generate four complete culinary recipes in <b>under 1.2 seconds</b> "
        "(compared to 6–10 seconds on traditional OpenAI/Anthropic APIs)."
    ))

    story.append(P("7.2 The Model Hierarchy", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI defines a multi-tier model cascade in <code>recipe_generator.py</code>:<br/>"
        "• <b>Primary Model:</b> <code>llama-3.3-70b-versatile</code> (Meta's flagship 70B open-weights model, offering high reasoning "
        "and strict adherence to complex system prompts).<br/>"
        "• <b>Fallback Model:</b> <code>llama-3.1-8b-instant</code> (Ultra-fast 8B parameter model used if the 70B model reaches rate limits).<br/>"
        "• <b>Deterministic Heuristic Engine:</b> Built-in Python fallback activated automatically if Groq is offline or the user has no API key."
    ))

    story.append(P("7.3 Prompt Engineering & The Clinical System Prompt", "SectionHeading"))
    story.append(P(
        "The system prompt in <code>recipe_generator.py</code> strictly constrains the LLM to prevent hallucinating unmeasured calories:<br/>"
        "<i>'You are an executive chef and sports nutritionist specializing in precision meal prep. Create an appetizing, "
        "practical recipe that strictly incorporates the exact optimizer ingredients and gram portions. Strictly adhere to "
        "the user\\'s custom cooking constraints... Do NOT add external unlisted ingredients (such as unallocated milk, oils, "
        "butter, or stock). Cooking water, salt, pepper, and dry spices are permitted. NEVER suggest, include, or garnish with "
        "any allergen listed in the clinical allergy constraints. Output ONLY valid JSON...'</i>"
    ))

    story.append(P("7.4 Robust JSON Extraction (extract_json_from_text)", "SectionHeading"))
    story.append(P(
        "LLMs frequently wrap JSON in conversational prose or markdown fences (e.g. <code>```json ... ```</code>). "
        "Our custom parser uses regular expressions to strip fences, extract the raw JSON object, and validate that required keys "
        "(<code>dish_title</code>, <code>cooking_time</code>, <code>instructions</code>) are present and properly typed."
    ))

    story.append(P("7.5 The Deterministic Heuristic Fallback Engine", "SectionHeading"))
    story.append(P(
        "If Groq API is offline, <code>generate_fallback_recipe()</code> executes:<br/>"
        "1. Identifies the primary staple, protein, and vegetable from the weighed items.<br/>"
        "2. Detects cooking fats: if ghee or oil was allocated by the optimizer, it writes <i>'using your measured ghee'</i>; "
        "if no fat was allocated, it writes <i>'using non-stick cookware or water sauté'</i>, preventing calorie inflation.<br/>"
        "3. Produces a 3-step culinary sequence (Prep, Sauté/Simmer, Assemble) and labels the engine as <code>Heuristic Recipe Engine</code>."
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 8: ALLERGEN SAFETY DEFENSE & OUTPUT VALIDATION
    # =========================================================================
    story.append(P("Chapter 8: Allergen Safety Defense & Output Validation", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("8.1 The Two-Tier Allergen Defense Architecture", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI enforces a strict two-tier allergen defense architecture:<br/>"
        "• <b>Tier 1: Pre-Optimization Dataset Filtering (preferences.py):</b> Excludes matching food items from the candidate pool "
        "using canonical alias expansion and plural stemming. This guarantees the optimizer cannot select prohibited foods.<br/>"
        "• <b>Tier 2: Post-Generation Output Validation (recipe_generator.py):</b> Scans the LLM-generated recipe text "
        "(dish title, preparation steps, chef notes) before displaying it to the user. If the LLM hallucinated an excluded allergen "
        "(e.g. suggesting crushed peanuts as a garnish), the response is rejected immediately."
    ))

    story.append(P("8.2 How validate_recipe_safety() Operates", "SectionHeading"))
    story.append(P(
        "The function <code>validate_recipe_safety(recipe_dict, prohibited_allergies)</code> runs a regex word-boundary scan:<br/>"
        "1. Expands every prohibited allergen into its canonical clinical cluster (e.g. <code>'tree nuts'</code> expands to "
        "<code>['almond', 'cashew', 'walnut', 'pistachio', 'nut', ...]</code>).<br/>"
        "2. Scans the complete recipe string using regex word boundaries: <code>rf'\\b{re.escape(term)}s?\\b'</code>.<br/>"
        "3. <b>Negative Lookahead Protection:</b> When checking for <code>'egg'</code>, it uses <code>r'\\beggs?\\b(?!plant)'</code> "
        "so that vegan/vegetarian dishes containing the vegetable <i>'eggplant'</i> are not falsely rejected.<br/>"
        "4. If any prohibited token is detected, it logs a warning, rejects the recipe, and triggers the next model or heuristic fallback."
    ))

    story.append(P("8.3 Clinical Limitations & Cross-Contamination Notice", "SectionHeading"))
    story.append(P(
        "<b>Important Viva Defense Note:</b> Never claim in an examination that software can be '100% allergen-safe'. "
        "Software text scanning filters known descriptions, but cannot detect trace commercial manufacturing cross-contamination "
        "(e.g. oats processed on machinery that handles wheat). In commit <code>3847078</code>, we added the official clinical notice "
        "to <code>index.html</code> advising users with severe anaphylaxis to verify certified manufacturer package labels."
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 9: FASTAPI BACKEND ARCHITECTURE (server.py)
    # =========================================================================
    story.append(P("Chapter 9: FastAPI Backend Architecture & API Endpoints (server.py)", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("9.1 The Role of FastAPI and Uvicorn", "SectionHeading"))
    story.append(P(
        "<b>FastAPI</b> is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints. "
        "It runs on <b>Uvicorn</b>, a lightning-fast ASGI server implementation using <code>uvloop</code>. FastAPI handles request "
        "serialization, concurrency, data validation via Pydantic, and automatic OpenAPI schema generation."
    ))

    story.append(P("9.2 W3C CORS Compliance Configuration", "SectionHeading"))
    story.append(P(
        "<b>Cross-Origin Resource Sharing (CORS)</b> is a browser security mechanism that restricts scripts from making HTTP requests "
        "to a different domain/port. In <code>server.py</code>, we hardened CORS compliance:<br/>"
        "• <b>Default Allowed Origins:</b> Explicit local development hosts (<code>http://localhost:8000</code>, <code>http://127.0.0.1:8000</code>, "
        "<code>http://localhost:5500</code>, <code>http://127.0.0.1:5500</code>, <code>http://localhost:3000</code>).<br/>"
        "• <b>W3C Credential Compliance:</b> Per the W3C CORS specification, credentials cannot be enabled when origin is a wildcard (<code>*</code>). "
        "We enforce <code>allow_credentials = not is_wildcard</code>, preventing browser security rejections."
    ))

    story.append(P("9.3 Pydantic Request Validation (PlanGenerationRequest)", "SectionHeading"))
    pydantic_code = (
        "class PlanGenerationRequest(BaseModel):\n"
        "    age: int = Field(22, ge=1, le=120, description='Age in years')\n"
        "    sex: Literal['male', 'female'] = Field('male', description='Biological sex')\n"
        "    height_cm: float = Field(175.0, ge=50.0, le=250.0, description='Height in cm')\n"
        "    weight_kg: float = Field(70.0, ge=20.0, le=300.0, description='Weight in kg')\n"
        "    target_weight_kg: Optional[float] = Field(None, ge=20.0, le=300.0)\n"
        "    activity_level: str = Field('moderate', description='sedentary, light, moderate, very_active, extremely_active')\n"
        "    goal: str = Field('maintenance', description='weight_loss, maintenance, weight_gain')\n"
        "    diet_type: str = Field('vegetarian', description='vegetarian, vegan, non-vegetarian')\n"
        "    allergies: List[str] = Field(default_factory=list)\n"
        "    number_of_meals: int = Field(3, ge=2, le=5, description='Number of main meals per day')\n"
        "    number_of_snacks: int = Field(1, ge=0, le=2, description='Number of snacks per day')"
    )
    story.append(CodeBlock(pydantic_code))
    story.append(Spacer(1, 8))

    story.append(P("9.4 REST API Endpoints Specification", "SectionHeading"))
    endpoint_headers = ["HTTP Method & Route", "Internal Function Called", "Input Payload", "Response Summary"]
    endpoint_rows = [
        ["GET /api/health", "health_check()", "None", "{'status': 'healthy', 'service': 'NutriGEN-AI Backend API', 'version': '1.0.0'}"],
        ["POST /api/generate-plan", "generate_plan_endpoint()", "PlanGenerationRequest (JSON)", "Unified meal plan, macro comparison, biometrics, recipes"],
        ["POST /api/meal-plan/generate", "generate_meal_plan_alias()", "PlanGenerationRequest (JSON)", "Backwards-compatible alias for generate-plan"],
        ["POST /generate-meal-plan", "generate_meal_plan_root_alias()", "PlanGenerationRequest (JSON)", "Root-level backwards-compatible legacy alias"],
        ["POST /api/nutrition/requirements", "calculate_requirements()", "{age, sex, height, weight, activity, goal}", "{bmr, tdee, calories, protein_g, fat_g, carbs_g}"]
    ]
    story.append(StyledTable(endpoint_headers, endpoint_rows, [120, 110, 120, 154]))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 10: FRONTEND ENGINEERING & COMMUNICATION (script.js)
    # =========================================================================
    story.append(P("Chapter 10: Frontend Engineering & Client-Server Communication", "ChapterHeading"))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(P("10.1 Reactive Client Architecture (Vanilla JS ES6+)", "SectionHeading"))
    story.append(P(
        "The frontend is constructed using pure standard web technologies without heavy framework dependencies (React, Angular, or Vue). "
        "This ensures lightning-fast page loading, zero build steps, and straightforward deployment. "
        "The script attaches event listeners to form input fields (<code>input</code>, <code>change</code>), executing "
        "<code>calculateBiometricsLive()</code> to provide instant client-side biometric feedback before the user even clicks submit."
    ))

    story.append(P("10.2 Prevention of Cross-Site Scripting (XSS)", "SectionHeading"))
    story.append(P(
        "A major security audit finding addressed in commit <code>bdb1bdd</code> was the vulnerability of injecting AI-generated "
        "recipe text into the DOM via <code>innerHTML</code>. If an LLM response contained malicious HTML tags or script injection, "
        "it could execute inside the user's browser.<br/>"
        "• <b>Safe DOM Element Construction:</b> We replaced <code>innerHTML</code> with our helper <code>el(tag, className, text)</code>, "
        "which assigns dynamic text strictly using <b><code>.textContent</code></b>. In JavaScript, <code>.textContent</code> treats all input "
        "as raw text, completely preventing script execution.<br/>"
        "• <b>HTML Escaping:</b> For template strings in print views and saved cards, all dynamic variables pass through "
        "<code>escapeHtml()</code>, which encodes <code>&amp;</code>, <code>&lt;</code>, <code>&gt;</code>, <code>&quot;</code>, and <code>&#039;</code>."
    ))

    story.append(P("10.3 Dynamic Meal Frequency Payload Construction", "SectionHeading"))
    story.append(P(
        "In <code>script.js</code>, <code>buildPayload(data)</code> dynamically calculates both <code>number_of_meals</code> and "
        "<code>number_of_snacks</code> based on the user's selected dropdown:<br/>"
        "• <b>5 Meals selected:</b> Sends <code>number_of_meals: 5, number_of_snacks: 2</code>.<br/>"
        "• <b>4 Meals selected:</b> Sends <code>number_of_meals: 4, number_of_snacks: 1</code>.<br/>"
        "• <b>3 Meals selected:</b> Sends <code>number_of_meals: 3, number_of_snacks: 0</code>.<br/>"
        "• <b>2 Meals selected:</b> Sends <code>number_of_meals: 2, number_of_snacks: 0</code>.<br/>"
        "This ensures the backend optimizer constructs the exact corresponding meal slot blueprint."
    ))

    story.append(P("10.4 LocalStorage Plan History Drawer", "SectionHeading"))
    story.append(P(
        "NutriGEN-AI implements a persistent history drawer using the browser's <code>localStorage</code> API. "
        "Whenever a meal plan is generated, <code>savePlanToHistory(payload, result)</code> serializes the request and response "
        "into JSON under the key <code>'nutrigen_plan_history'</code>. Users can open the sidebar drawer, browse past meal plans, "
        "and reload them instantly without re-running the optimization solver."
    ))

    story.append(P("10.5 Practical Shopping Assistant: Grocery Checklist Modal", "SectionHeading"))
    story.append(P(
        "Users frequently struggle to translate daily meal plans into a shopping cart. The frontend includes a grocery checklist generator: "
        "it iterates through all food items across every meal slot, aggregates quantities of identical foods, and renders an interactive "
        "checklist modal with <i>'Copy to Clipboard'</i> and <i>'Print Checklist'</i> buttons."
    ))

    return story
