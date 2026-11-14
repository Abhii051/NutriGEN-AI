# 🥗 NutriGEN-AI

> **Algorithmic Clinical Nutrition & AI-Synthesized Meal Planning Platform**
> A deterministic, non-linear macro-optimization engine paired with generative culinary intelligence.

---

## 📌 Executive Overview

Traditional AI-generated meal plans suffer from **hallucinated portion sizes** and inaccurate nutritional values. Large Language Models cannot reliably calculate metabolic chemistry or continuous portion masses.

**NutriGEN-AI** solves this fundamental limitation using a **two-stage hybrid architecture**:
1. **Deterministic Biochemical & Mathematical Optimization (Python + SciPy SLSQP):**
   Derives precise physiological energy expenditure via the Mifflin-St Jeor equation, filters clinical allergens and dietary lifestyles across 7,900+ curated USDA food items, and solves a Sequential Least Squares Programming (SLSQP) continuous non-linear optimization problem to converge food portions to within $\pm 2.5\%$ of caloric and macronutrient targets with **zero post-optimization drift**.
2. **Generative Culinary Intelligence (Groq API + LLaMA 3.3 70B):**
   Receives the mathematically verified food items and gram portions as immutable inputs. The model acts exclusively as an **Executive Culinary Chef**, turning the exact ingredients into realistic cooking instructions, prep steps, and culinary titles without altering portions or macros.

---

## 🏛️ System Architecture

```
User Browser (HTML5 / CSS3 / Vanilla ES6 SPA)
        │
        │ HTTP POST /api/generate-plan
        ▼
FastAPI REST API Server (Backend/server.py)
        │
        ▼
Pipeline Orchestrator (Backend/src/pipeline.py)
        │
        ├──► 1. Biometric Engine (ai_model.py)
        │       └── Mifflin-St Jeor BMR ──► TDEE (Activity Multiplier) ──► Target Macros
        │
        ├──► 2. Non-Linear Optimization Engine (Backend/src/optimizer.py)
        │       ├── Ingests master_food_dataset_final.csv (7,909 items, 23 Nutrients)
        │       ├── Clinical Allergen & Diet Elimination (Backend/src/preferences.py)
        │       ├── Structured Candidate Selection (11–14 Meal Slots)
        │       └── SciPy SLSQP Solver: min L(x) subject to cal_constraint & bounds
        │
        └──► 3. AI Culinary Synthesis (Backend/src/recipe_generator.py)
                ├── Groq Cloud API (llama-3.3-70b-versatile, temp=0.3)
                ├── Regex JSON Deserializer
                └── Deterministic 3-Step Heuristic Fallback Engine
```

---

## 🛠️ Technology Stack

| Layer | Technology | Key Role |
|---|---|---|
| **Backend API** | **FastAPI** + **Uvicorn** | Asynchronous REST API service with Pydantic type validation |
| **Optimization Core** | **SciPy** (`scipy.optimize.minimize` SLSQP) | Continuous non-linear optimization with asymmetric penalties |
| **Data Engineering** | **Pandas** & **NumPy** | High-performance dataset filtering, vectorization, dot products |
| **Generative AI** | **Groq API** (`llama-3.3-70b-versatile`) | Fast LPU-accelerated culinary recipe and step generation |
| **Frontend UI** | **HTML5**, **CSS3**, **Vanilla ES6 JS** | Responsive Single-Page Application (SPA) with Chart.js |
| **Client Storage** | Browser `localStorage` | Client-side persistence (`nutrigen_meal_plans_history_v2`) |
| **Primary Datasets** | **USDA Foundation** & **SR Legacy** | 7,909 verified items with 23 per-100g nutritional attributes |

---

## 🚀 Key Features

- **Biometric Requirement Derivation:** Computes exact BMR and TDEE across 5 activity tiers with customized calorie goals (weight loss $-10\%$, maintenance, weight gain $+10\%$).
- **Strict Clinical Allergen Filtering:** Multi-select filtering for Dairy, Eggs, Nuts, Peanuts, Gluten, Soy, Fish, Shellfish, plus custom blacklist terms.
- **Dietary & Lifestyle Support:** Strict filtering for Vegetarian, Vegan, Non-Vegetarian, and Keto, with an egg-lacto toggle.
- **Zero-Drift SLSQP Portion Solver:** Directly converts mathematical portion weights (grams) into meal slots without post-optimization item dropping.
- **Robust AI Chef Recipes & Offline Fallback:** Generates culinary titles and instructions via LLaMA 3.3 70B, with transparent 3-step heuristic fallbacks if offline.
- **Household Measurement Conversion:** Automatically translates continuous grams into intuitive kitchen units (`~2 chapatis`, `~1 bowl dal`, `~2 eggs`).
- **Smart Grocery Shopping Checklist:** Modal consolidating ingredients across all meals into departmental shopping checklists with print formatting.
- **Persistent Plan History:** Off-canvas drawer caching up to 10 historical meal plans in browser storage.

---

## 📂 Project Directory Structure

```text
NutriGEN-AI/
├── Backend/
│   ├── main.py                     # Programmatic Uvicorn runner
│   ├── server.py                   # Production FastAPI REST API & static file mount
│   ├── src/
│   │   ├── optimizer.py            # SciPy SLSQP continuous solver & slot candidate logic
│   │   ├── pipeline.py             # Pipeline orchestrator
│   │   ├── preferences.py          # Diet, allergen, and cuisine filtering engine
│   │   └── recipe_generator.py     # Groq API integration & heuristic fallback generator
│   └── tests/
│       ├── test_api.py             # FastAPI TestClient API integration tests
│       └── test_groq_llm.py        # Groq prompt formatting and fallback schema tests
│
├── Frontend/
│   ├── index.html                  # Responsive Single-Page Application
│   ├── style.css                   # Modern CSS3 design system & responsive layout
│   └── script.js                   # Client controller, Chart.js graphs, localStorage
│
├── data/
│   └── processed/
│       ├── master_food_dataset_final.csv  # 7,909 active records with 23 nutrient columns
│       └── dropped_zero_calorie_foods.csv # 87,885 discarded zero-calorie lab assays
│
├── data_processing/                # Dataset ingestion and standardization scripts
├── ai_model.py                     # Core biometric engine (BMR, TDEE, Calorie, Macros)
├── requirements.txt                # Python package dependencies manifest
└── .env.example                    # Environment variable template
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Abhii051/NutriGEN-AI.git
cd NutriGEN-AI
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open `.env` and add your Groq API key:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
ALLOWED_ORIGINS=*
```
*(Note: If no Groq API key is provided, the application will automatically run in **Offline Heuristic Mode**, generating structured 3-step recipes without errors).*

---

## 🏃 Running the Application

Start the production FastAPI server using Uvicorn:

```bash
uvicorn Backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Web Application UI:** Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Interactive API Documentation (Swagger):** Open [http://localhost:8000/docs](http://localhost:8000/docs).
- **Alternative Redoc Documentation:** Open [http://localhost:8000/redoc](http://localhost:8000/redoc).

---

## 📡 API Endpoints

### 1. Generate Full Meal Plan & Recipes
- **Route:** `POST /api/generate-plan`
- **Request Body:**
  ```json
  {
    "age": 25,
    "weight_kg": 72.0,
    "height_cm": 178.0,
    "sex": "male",
    "activity_level": "moderate",
    "goal": "weight_loss",
    "diet_type": "vegetarian",
    "eats_eggs": false,
    "allergies": ["peanuts", "shellfish"],
    "disliked_foods": ["bitter gourd"],
    "number_of_meals": 3,
    "number_of_snacks": 1,
    "cuisine": "indian"
  }
  ```
- **Response:** Returns `user_requirements`, `meal_plan` (with food gram weights), `nutrition_summary` (calories, macros, and micronutrients), and `recipes` (cooking titles and steps).

### 2. Standalone Nutrition Profile
- **Route:** `POST /api/nutrition/requirements`
- **Response:** Returns BMR, TDEE, Calorie target, and macronutrient gram goals without generating meal slots.

### 3. Health Probe
- **Route:** `GET /api/health`
- **Response:** `{"status": "healthy", "service": "NutriGEN-AI API"}`

---

## 🧪 Testing

Run automated tests using `pytest`:

```bash
pytest Backend/tests
```

---

## 📄 License

This project is licensed under the MIT License.
