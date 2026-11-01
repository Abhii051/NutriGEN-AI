# NutriGEN-AI: Comprehensive Project Guide & Mentor Q&A

**Project Title:** NutriGEN-AI: Personalized Meal Plan Generator Leveraging Optimization and Large Language Models  
**Reference Paper:** *NutriGen: Personalized Meal Plan Generator Leveraging Large Language Models to Enhance Dietary and Nutritional Adherence* (Saman Khamesian, Asiful Arefeen, Stephanie M. Carpenter, Hassan Ghasemzadeh - Arizona State University, 2025)

---

## 1. Executive Summary & Key Takeaways from the Research Paper

### The Core Problem
1. **Adherence Challenge:** People struggle to maintain healthy diets due to nutritional complexity, time constraints, and lack of domain knowledge.
2. **Traditional Algorithmic Systems (e.g., PSO, Linear Programming):** While mathematically efficient at matching calorie numbers, they produce unappetizing, robotic meal outputs (e.g., *"eat 34g raw lentils, 12g lard, 180g cabbage"*). They ignore cultural preferences, ingredient availability, and cooking reality.
3. **Pure Chatbots & LLMs:** While engaging and capable of generating creative recipes, LLMs suffer from severe **arithmetic hallucinations** and cannot reliably calculate or adhere to strict caloric and macronutrient targets.

### Key Findings of the Paper
* **Prompt Architecture:** The authors introduced a structured prompt framework $P = \{I_{\text{current}}, T_{\text{task}}, O_{\text{output}}\}$ grounded in verified USDA nutritional references.
* **Model Benchmarking (10 LLMs Evaluated):**
  * **Best Caloric Adherence:** **Llama 3.1 8B** achieved the lowest Mean Absolute Error (**1.55% error / 34.14 kcal**), followed closely by **GPT-3.5 Turbo** (**3.68% error / 54.16 kcal**).
  * **Speed vs. Accuracy Tradeoff:** Lightweight models (GPT-3.5 Turbo, Gemini 2.0 Flash, Claude 3.5 Haiku) generated plans rapidly (~20–30s). Larger models like DeepSeek-V3 took over 300s and failed on 40% of test queries due to context/reasoning overhead.
  * **Severe Hallucinations in Some Models:** GPT-4o Mini showed an error of **24.67% (329.06 kcal off target)**, demonstrating that LLMs cannot be trusted with nutrition calculations without external grounding.
* **The Hybrid Conclusion:** The ideal architecture pairs **ground-truth database validation + constrained mathematical optimization** (for precise portion math) with **LLMs** (for recipe generation, meal structuring, and user interaction).

---

## 2. Dataset Deep Dive

### Source & Database
Our system uses the **USDA FoodData Central (FDC)** database, which is the international gold standard for food composition:
1. **Foundation Foods (`data/raw/foundation`):** Advanced chemical laboratory assays on basic agricultural foods and raw ingredients.
2. **SR Legacy (`data/raw/sr_legacy`):** USDA Standard Reference Legacy database covering common prepared foods, cooked dishes, and everyday groceries.
3. **Food Portions (`food_portions.csv`):** Standard household portion conversions (grams per cup, tablespoon, slice, etc.).

### Features Extracted (23 Essential Nutrients per 100g)
* **Macronutrients:** Calories (kcal), Protein (g), Total Fat (g), Carbohydrates (g), Dietary Fiber (g), Sugar (g).
* **Minerals:** Calcium (mg), Iron (mg), Magnesium (mg), Phosphorus (mg), Potassium (mg), Sodium (mg), Zinc (mg).
* **Vitamins:** Vitamin A (ug), Vitamin E (mg), Vitamin D (ug), Vitamin C (mg), Thiamin B1 (mg), Riboflavin B2 (mg), Niacin B3 (mg), Folate (ug), Vitamin B12 (ug), Vitamin K (ug).

---

## 3. Data Cleaning Pipeline: Exact Counts & Criteria

### Step-by-Step Data Funnel & Exact Record Counts

| Pipeline Stage | Script | Initial Records | Records Removed | Remaining Records | Purpose / Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Ingestion** | USDA raw | - | - | **95,784** foods | 87,991 (Foundation) + 7,793 (SR Legacy). Total raw nutrient entries: 814,596. |
| **Nutrient Extraction & Pivot** | `data_processing/food_dataset.py` | 95,784 | 0 | **95,784** foods | Extracted 23 required nutrient IDs, pivoted vertical relational data into 1 row per food with 23 columns. Filled missing micronutrients with `0.0`. |
| **Dataset Merging** | `data_processing/merge_datasets.py` | 95,784 | 0 | **95,784** foods | Merged Foundation and SR Legacy; verified 0 conflicting duplicate `fdc_id`s. |
| **Diet Classification** | `data_processing/classify_foods.py` | 95,784 | 0 | **95,784** foods | Tagged each food as `vegan`, `vegetarian`, or `non_vegetarian`. Categorized into roles (`staple`, `protein`, `vegetable`, `fruit`, `healthy_fat`). |
| **Null Description Cleaning** | `data_processing/clean_dataset.py` | 95,784 | **8** records | **95,776** foods | Dropped 8 records that had missing/null (`NaN`) food descriptions. Saved to `master_food_dataset_final.csv`. |
| **Runtime Selection** | `Backend/src/optimizer.py` | 95,776 | ~95,740 non-matches | **~36** candidate foods | Excluded powders/isolates/baby foods/fast food. Filtered by user diet, allergies, and picked top scored foods per role. |

### Basis of Cleaning Criteria
1. **Nutrient Relevance:** USDA tracks hundreds of esoteric analytical markers (water, ash, specific fat isomers). We filter only the 23 essential nutrients that govern human nutrition.
2. **Missing Value Imputation:** Missing micronutrients are set to `0.0` to avoid linear algebra failures during optimization.
3. **Food Suitability Exclusions:** Industrial isolates (whey isolate, egg albumen powder, spirulina, gelatin, baby formula) are removed so meal plans contain real, consumable foods.
4. **Category Exclusions:** Junk categories like "Fast Foods", "Sweets", and "Snacks" are purged from the recommendation candidate pool.

---

## 4. End-to-End System Workflow

```
[ User Input (Streamlit UI) ]
(Age, Sex, Height, Weight, Activity Level, Dietary Goal)
            │
            ▼
[ Step 1: Energy & Target Calculation ]
• BMR via Mifflin-St Jeor Equation
• TDEE via Physical Activity Factor Multiplier
• Calorie Goal: Deficit (Weight Loss) / Surplus (Muscle Gain) / Maintenance
• Target Grams: Protein, Carbohydrates, Fats
            │
            ▼
[ Step 2: Preference & Allergen Filtering ]
• Diet Type: Vegan / Vegetarian / Non-Vegetarian
• Allergen Elimination: Dairy, Nuts, Gluten, Shellfish, etc.
• Cuisine Preference: Indian, Mediterranean, Continental, etc.
            │
            ▼
[ Step 3: Food Role Candidate Pool ]
Select top-scoring foods across 5 nutritional roles:
1. Staples (Oats, Rice, Quinoa, Roti)
2. Proteins (Lentils, Eggs, Paneer, Chicken, Tofu)
3. Vegetables (Spinach, Broccoli, Tomatoes, Peppers)
4. Fruits (Apples, Berries, Bananas)
5. Healthy Fats (Olive Oil, Ghee, Almonds)
            │
            ▼
[ Step 4: SciPy Numerical Optimizer ]
Solves constrained optimization to determine exact gram amounts (x_i)
for each food item to minimize nutrient deviation under portion limits.
            │
            ▼
[ Step 5: Meal Plan & Recipe Assembly ]
Distribute ingredients into Breakfast, Lunch, Dinner, and Snacks.
Generate cooking instructions, portion descriptions, and nutrient summaries.
```

---

## 5. Optimization Deep Dive

### What is Optimization?
Optimization is the mathematical formulation of finding the optimal portion weights in grams ($x = [x_1, x_2, \dots, x_n]$) for $n$ selected foods such that their combined calories and macronutrients match user targets with minimum error, while keeping all serving sizes within realistic eating limits.

### Mathematical Formulation in `optimizer.py`

#### 1. Decision Variables
Let $x_i$ be the quantity of food item $i$ in grams.
The delivered nutritional amount is computed via dot products:
$$\text{Delivered Calories} = \sum_{i=1}^n x_i \cdot \frac{\text{Calories}_i}{100}$$
$$\text{Delivered Protein} = \sum_{i=1}^n x_i \cdot \frac{\text{Protein}_i}{100}$$
$$\text{Delivered Fat} = \sum_{i=1}^n x_i \cdot \frac{\text{Fat}_i}{100}$$
$$\text{Delivered Carbs} = \sum_{i=1}^n x_i \cdot \frac{\text{Carbs}_i}{100}$$

#### 2. Realistic Portion Bounds ($l_i \le x_i \le u_i$)
* Staples: $0 \le x_i \le 250\text{g}$
* Protein sources: $0 \le x_i \le 200\text{g}$
* Vegetables: $0 \le x_i \le 250\text{g}$
* Fruits: $0 \le x_i \le 200\text{g}$
* Healthy Fats (oils/butter): $0 \le x_i \le 40\text{g}$

#### 3. Objective Function (Loss)
The optimizer minimizes the weighted normalized quadratic error:
$$\mathcal{L}(x) = 15\left(\frac{\Delta \text{Cal}}{\text{Target}_{\text{Cal}}}\right)^2 + 8\left(\frac{\Delta \text{Prot}}{\text{Target}_{\text{Prot}}}\right)^2 + 15\left(\frac{\Delta \text{Fat}}{\text{Target}_{\text{Fat}}}\right)^2 + 12\left(\frac{\Delta \text{Carb}}{\text{Target}_{\text{Carb}}}\right)^2 + \mathcal{P}_{\text{fat}} + \mathcal{P}_{\text{carb}} + \mathcal{P}_{\text{portion}}$$

Where:
* $\mathcal{P}_{\text{fat}} = 20 \times \left(\frac{\max(0, \text{Target}_{\text{Fat}} - \text{Fat})}{\text{Target}_{\text{Fat}}}\right)^2$ (severely penalizes fat deficiency).
* $\mathcal{P}_{\text{carb}} = 10 \times \left(\frac{\max(0, \text{Carbs} - \text{Target}_{\text{Carbs}})}{\text{Target}_{\text{Carbs}}}\right)^2$ (penalizes carb spikes).
* $\mathcal{P}_{\text{portion}} = 0.1 \times \sum (x_i / 200)^2$ (prevents needlessly huge food quantities).

The problem is solved using `scipy.optimize.minimize` (SLSQP / Sequential Least Squares Programming).

### What Happens If We Do NOT Optimize?
1. **Severe Macro Imbalance:** A random or unoptimized diet could match calories by loading up on 80% sugar/carbohydrates with almost zero protein or healthy fats.
2. **Absurd Portion Sizes:** Unbounded formulas may prescribe 800g of almonds (dangerous fat excess) or 10g of chicken (nutritionally useless).
3. **LLM Hallucinations:** As proven in the paper, unoptimized LLMs deviate from target calories by up to **24.67%** (over 329 kcal error) and regularly fail basic arithmetic.

---

## 6. How to Demonstrate Progress to Your Mentor

When demonstrating the project, present your results across four distinct dimensions:

1. **Target Convergence Metric:**
   * **Without Optimization / Pure LLM:** 10% to 25% deviation from target calories.
   * **NutriGEN Optimized:** **< 2% Mean Absolute Percentage Error** across calories and macronutrients.
2. **Data Pipeline Robustness:**
   * Showcase the exact data pipeline: from **95,784 raw USDA records** down to **95,776 clean categorized foods**, filtered dynamically to a tailored pool of **~36 candidates**.
3. **Nutritional Feasibility:**
   * Demonstrate 100% adherence to portion constraints ($0 \le x_{\text{fat}} \le 40\text{g}$, staples $\le 250\text{g}$) and strict allergy/diet safety (0 cross-contamination).
4. **Live Interactive UI Demo:**
   * Run the Streamlit frontend (`streamlit run Backend/app.py`).
   * Enter a test persona (e.g., Vegetarian, 2100 kcal, Muscle Gain, Indian cuisine).
   * Show the live solver output: exact gram measurements, macro target vs. achieved progress bars, and the resulting meal breakdown with recipes.
