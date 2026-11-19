// =====================================================================
// NutriGEN-AI: Clinical Nutrition & AI-Optimized Meal Planner
// Frontend Client Logic (Vanilla JS, Zero External Dependencies)
// =====================================================================

// Use relative API path so it works seamlessly on localhost:8000, 127.0.0.1, or network host
const API_URL = "/api/generate-plan";
const STORAGE_KEY = "nutrigen_meal_plans_history_v2";

// DOM Elements
const form = document.getElementById("nutritionForm");
const generateBtn = document.getElementById("generateBtn");
const mealResults = document.getElementById("mealResults");
const demoBtn = document.getElementById("demoBtn");

// History Drawer Elements
const historyDrawer = document.getElementById("historyDrawer");
const historyDrawerBackdrop = document.getElementById("historyDrawerBackdrop");
const historyDrawerList = document.getElementById("historyDrawerList");
const historyBadge = document.getElementById("historyBadge");
const topbarHistoryCount = document.getElementById("topbarHistoryCount");
const historyCountLabel = document.getElementById("historyCountLabel");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const openHistoryBtn = document.getElementById("openHistoryBtn");
const historyNavBtn = document.getElementById("historyNavBtn");
const heroHistoryBtn = document.getElementById("heroHistoryBtn");
const historyPreviewViewAll = document.getElementById("historyPreviewViewAll");
const historyDrawerCloseBtn = document.getElementById("historyDrawerCloseBtn");
const historyPreviewList = document.getElementById("historyPreviewList");

// Grocery Modal Elements
const groceryModal = document.getElementById("groceryModal");
const groceryModalBackdrop = document.getElementById("groceryModalBackdrop");
const groceryModalCloseBtn = document.getElementById("groceryModalCloseBtn");
const groceryContent = document.getElementById("groceryContent");
const groceryItemCount = document.getElementById("groceryItemCount");
const copyGroceryBtn = document.getElementById("copyGroceryBtn");
const printGroceryBtn = document.getElementById("printGroceryBtn");
const sidebarGroceryBtn = document.getElementById("sidebarGroceryBtn");
const sidebarPrintBtn = document.getElementById("sidebarPrintBtn");

// Swap Modal Elements
const swapModal = document.getElementById("swapModal");
const swapModalBackdrop = document.getElementById("swapModalBackdrop");
const swapModalCloseBtn = document.getElementById("swapModalCloseBtn");
const swapModalTitle = document.getElementById("swapModalTitle");
const swapModalSubtitle = document.getElementById("swapModalSubtitle");
const swapModalOriginal = document.getElementById("swapModalOriginal");
const swapModalBody = document.getElementById("swapModalBody");

// Current active plan & customization state in memory
let currentActivePlan = null;
let currentExcludedFdcIds = new Set();
let currentVariationSeed = 1;
let currentActiveDayIndex = 1;


// ─── Utility Helpers ─────────────────────────────────────────────────────────

function escapeHtml(s) {
    if (s === null || s === undefined) return "";
    return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function el(tag, className, text) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
}

function fmt(n, decimals = 1) {
    if (n === null || n === undefined || isNaN(n)) return "--";
    return Number(n).toFixed(decimals);
}

function capitalize(s) {
    if (!s) return "";
    return s.charAt(0).toUpperCase() + s.slice(1);
}


// ─── Real-Time Live Biometric Calculations ───────────────────────────────────

function calculateBiometricsLive() {
    const age = Number(document.getElementById("age").value);
    const gender = document.getElementById("gender").value || "male";
    const weight = Number(document.getElementById("weight").value);
    const targetWeight = Number(document.getElementById("target_weight").value);
    const height = Number(document.getElementById("height").value);
    const activity = document.getElementById("activity").value || "moderate";
    const goal = document.getElementById("goal").value || "maintenance";

    if (!weight || weight <= 0 || !height || height <= 0 || !age || age <= 0) {
        return;
    }

    // 1. BMI Calculation
    const hMeters = height / 100.0;
    const bmi = weight / (hMeters * hMeters);
    const bmiEl = document.getElementById("bmiValue");
    const bmiStatusEl = document.getElementById("bmiStatus");

    bmiEl.textContent = bmi.toFixed(1);

    if (bmi < 18.5) {
        bmiStatusEl.textContent = "Underweight";
        bmiStatusEl.className = "stat-pill alert";
    } else if (bmi < 25.0) {
        bmiStatusEl.textContent = "Normal Healthy Weight";
        bmiStatusEl.className = "stat-pill success";
    } else if (bmi < 30.0) {
        bmiStatusEl.textContent = "Overweight";
        bmiStatusEl.className = "stat-pill warn";
    } else {
        bmiStatusEl.textContent = "Obese Range";
        bmiStatusEl.className = "stat-pill alert";
    }

    // 2. BMR Calculation (Mifflin-St Jeor)
    let bmr = 10 * weight + 6.25 * height - 5 * age;
    if (gender === "male") {
        bmr += 5;
    } else if (gender === "female") {
        bmr -= 161;
    } else {
        bmr -= 78;
    }
    document.getElementById("bmrValue").innerHTML = `${Math.round(bmr)} <small>kcal</small>`;

    // 3. TDEE Calculation
    const activityFactors = {
        sedentary: 1.20,
        light: 1.375,
        moderate: 1.55,
        very_active: 1.725,
        extremely_active: 1.90,
        // Backward-compatibility aliases
        active: 1.725,
        extremely: 1.90
    };
    const factor = activityFactors[activity] || 1.55;
    const tdee = bmr * factor;
    document.getElementById("tdeeValue").innerHTML = `${Math.round(tdee)} <small>kcal</small>`;

    // 4. Calorie Target & Deficit/Surplus
    let calorieTarget = tdee;
    const deltaBadge = document.getElementById("calorieDeltaBadge");

    if (goal === "weight_loss") {
        calorieTarget = tdee * 0.90;
        const deficit = Math.round(tdee - calorieTarget);
        deltaBadge.textContent = `-${deficit} kcal/day Deficit`;
        deltaBadge.className = "stat-pill normal";
    } else if (goal === "weight_gain") {
        calorieTarget = tdee * 1.10;
        const surplus = Math.round(calorieTarget - tdee);
        deltaBadge.textContent = `+${surplus} kcal/day Surplus`;
        deltaBadge.className = "stat-pill warn";
    } else {
        deltaBadge.textContent = "Balanced Maintenance";
        deltaBadge.className = "stat-pill neutral";
    }

    document.getElementById("calorieValue").innerHTML = `${Math.round(calorieTarget)} <small>kcal</small>`;

    // 5. Target Weight & Timeline Projection
    const targetDisplay = document.getElementById("targetWeightDisplay");
    const timelineEl = document.getElementById("targetWeightTimeline");
    const paceEl = document.getElementById("targetWeightPace");

    if (targetWeight && targetWeight > 0) {
        const weightDiff = targetWeight - weight;
        targetDisplay.innerHTML = `${targetWeight.toFixed(1)} <small>kg</small>`;

        const dailyDelta = Math.abs(calorieTarget - tdee);
        const weeklyRateKg = (dailyDelta * 7.0) / 7700.0; // 7700 kcal per kg of body weight change

        if (Math.abs(weightDiff) < 0.2) {
            timelineEl.textContent = "At target goal weight!";
            paceEl.textContent = "Focus on maintenance nutrition";
        } else if (weeklyRateKg > 0.05) {
            const weeks = Math.abs(weightDiff) / weeklyRateKg;
            const diffText = weightDiff < 0 ? `${weightDiff.toFixed(1)} kg` : `+${weightDiff.toFixed(1)} kg`;
            timelineEl.textContent = `${diffText} in ~${Math.ceil(weeks)} weeks`;
            paceEl.textContent = `Projected safe rate: ~${weeklyRateKg.toFixed(2)} kg/wk`;
        } else {
            const diffText = weightDiff < 0 ? `${weightDiff.toFixed(1)} kg` : `+${weightDiff.toFixed(1)} kg`;
            timelineEl.textContent = `Goal: ${diffText}`;
            paceEl.textContent = "Select weight loss or gain for timeline";
        }
    } else {
        targetDisplay.innerHTML = `-- <small>kg</small>`;
        timelineEl.textContent = "Optional: Set target weight";
        paceEl.textContent = "Estimates weeks to reach goal";
    }

    // 6. Clinical Hydration Target (35 ml per kg)
    const waterLiters = (weight * 0.035).toFixed(1);
    const glasses = Math.round((weight * 0.035) / 0.25); // ~250 ml glass
    document.getElementById("waterValue").innerHTML = `${waterLiters} <small>L/day</small>`;
    document.getElementById("waterGlasses").textContent = `~${glasses} standard glasses daily`;
}

// Bind live recalculation to all form input changes
[
    "age", "gender", "weight", "target_weight", "height", "activity", "goal"
].forEach(id => {
    const elem = document.getElementById(id);
    if (elem) {
        elem.addEventListener("input", calculateBiometricsLive);
        elem.addEventListener("change", calculateBiometricsLive);
    }
});


// ─── Extract Form Data & Build Backend Payload ───────────────────────────────

function getFormData() {
    return {
        name: document.getElementById("name").value.trim() || "User",
        age: Number(document.getElementById("age").value),
        gender: document.getElementById("gender").value || "male",
        weight: Number(document.getElementById("weight").value),
        target_weight: Number(document.getElementById("target_weight").value) || null,
        height: Number(document.getElementById("height").value),
        activity: document.getElementById("activity").value || "moderate",
        goal: document.getElementById("goal").value || "maintenance",
        diet: document.getElementById("diet").value || "vegetarian",
        cuisine: document.getElementById("cuisine").value || "indian",
        meals: Number(document.getElementById("meals").value) || 4,
        plan_days: Number(document.getElementById("plan_days")?.value || 1),
        allergies: document.getElementById("allergies").value.trim(),
        user_prompt: document.getElementById("user_prompt").value.trim()
    };
}

function buildPayload(data) {
    let diet_type = data.diet || data.diet_type || "vegetarian";
    let eats_eggs = false;

    if (diet_type === "eggetarian") {
        diet_type = "vegetarian";
        eats_eggs = true;
    } else if (diet_type === "non_vegetarian") {
        diet_type = "non-vegetarian";
    }

    const sex = data.gender === "female" || data.sex === "female" ? "female" : "male";
    const totalMeals = Number(data.meals || data.number_of_meals) || 4;
    const number_of_meals = totalMeals;
    const number_of_snacks = totalMeals === 4 ? 1 : (totalMeals === 5 ? 2 : 0);

    const allergies = data.allergies
        ? (Array.isArray(data.allergies) ? data.allergies : data.allergies.split(",").map(s => s.trim()).filter(Boolean))
        : [];

    return {
        age: Number(data.age),
        sex: sex,
        height_cm: Number(data.height || data.height_cm),
        weight_kg: Number(data.weight || data.weight_kg),
        target_weight_kg: data.target_weight || data.target_weight_kg || null,
        activity_level: data.activity || data.activity_level || "moderate",
        goal: data.goal || "maintenance",
        diet_type: diet_type,
        eats_eggs: eats_eggs,
        allergies: allergies,
        cuisine: data.cuisine || "indian",
        number_of_meals: number_of_meals,
        number_of_snacks: number_of_snacks,
        user_prompt: data.user_prompt || "",
        plan_days: Number(data.plan_days || 1),
        variation_seed: Number(data.variation_seed || 1),
        exclude_fdc_ids: Array.isArray(data.exclude_fdc_ids) ? data.exclude_fdc_ids : []
    };
}


// ─── Household Serving Hints Generator ───────────────────────────────────────

function getServingHint(foodName, grams) {
    const fn = (foodName || "").toLowerCase();
    const g = Number(grams) || 0;

    if (fn.includes("roti") || fn.includes("chapati")) {
        const count = Math.max(1, Math.round(g / 40));
        return `~${count} ${count === 1 ? 'chapati' : 'chapatis'}`;
    }
    if (fn.includes("poha") || fn.includes("upma") || fn.includes("khichdi") || fn.includes("rice")) {
        const bowls = (g / 130).toFixed(1);
        return `~${bowls} katori / bowl`;
    }
    if (fn.includes("dal") || fn.includes("sambar") || fn.includes("curry") || fn.includes("chana") || fn.includes("rajma")) {
        const bowls = (g / 150).toFixed(1);
        return `~${bowls} medium bowl`;
    }
    if (fn.includes("paneer") || fn.includes("tofu")) {
        const cubes = Math.round(g / 25);
        return `~${cubes} cubes`;
    }
    if (fn.includes("pita")) {
        const count = Math.max(1, Math.round(g / 60));
        return `~${count} pita`;
    }
    if (fn.includes("hummus")) {
        const tbsp = Math.max(1, Math.round(g / 15));
        return `~${tbsp} tbsp`;
    }
    if (fn.includes("egg")) {
        const count = Math.max(1, Math.round(g / 50));
        return `~${count} whole`;
    }
    if (fn.includes("chicken") || fn.includes("salmon") || fn.includes("fish")) {
        return `~${(g / 100).toFixed(1)} palm portion`;
    }
    if (fn.includes("oats")) {
        const cups = (g / 40).toFixed(1);
        return `~${cups} cup cooked`;
    }
    if (fn.includes("almond") || fn.includes("peanut") || fn.includes("walnut")) {
        return `~${Math.round(g / 1.2)} nuts`;
    }
    if (fn.includes("ghee") || fn.includes("olive oil") || fn.includes("oil")) {
        const tsp = Math.max(1, Math.round(g / 5));
        return `~${tsp} tsp`;
    }
    return `~${Math.round(g)}g serving`;
}


// ─── Render Complete Meal Plan on Screen ─────────────────────────────────────

function displayMealPlan(response, optionalUserData = null) {
    currentActivePlan = { response, user: optionalUserData || getFormData() };
    currentActiveDayIndex = 1;
    renderCurrentPlanView();
}

function renderCurrentPlanView() {
    mealResults.replaceChildren();
    if (!currentActivePlan || !currentActivePlan.response) return;

    const response = currentActivePlan.response;
    const optionalUserData = currentActivePlan.user;
    const nr = response.nutrition_requirements || {};
    const mp = response.meal_plan || {};
    const isMultiDay = Array.isArray(mp.days) && mp.days.length > 1;

    // Resolve active day data
    let activeMealPlanData = mp.meal_plan || {};
    let activeTotals = mp.totals || {};
    let activeRecipesData = response.recipes || mp.recipes || {};

    if (isMultiDay) {
        const dayIdx = Math.max(0, Math.min(mp.days.length - 1, currentActiveDayIndex - 1));
        const dayObj = mp.days[dayIdx] || mp.days[0];
        activeMealPlanData = dayObj.meal_plan || {};
        activeTotals = dayObj.totals || {};
        activeRecipesData = dayObj.recipes || activeRecipesData;
    }

    // 1. Action Toolbar
    const toolbar = el("div", "results-toolbar");

    const leftGroup = el("div", "toolbar-group");
    const printBtn = el("button", "tool-action-btn", "🖨️ Print / Export PDF");
    printBtn.addEventListener("click", () => exportPlanToPrint(currentActivePlan));

    const groceryBtn = el("button", "tool-action-btn", "🛒 View Grocery List");
    groceryBtn.addEventListener("click", () => openGroceryModal(currentActivePlan));

    // Option A: Full Plan Regeneration Button
    const regenBtn = el("button", "tool-action-btn btn-regenerate-alt", "🔄 Regenerate Alternative Plan");
    regenBtn.title = "Generate a completely fresh diet plan with zero duplicate ingredients";
    regenBtn.addEventListener("click", () => handleRegenerateAlternative(regenBtn));

    leftGroup.appendChild(printBtn);
    leftGroup.appendChild(groceryBtn);
    leftGroup.appendChild(regenBtn);

    // Quick Cuisine Switcher Pills
    const rightGroup = el("div", "toolbar-group");
    const cuisineLabel = el("span", "cuisine-quick-label", "Switch Cuisine:");
    rightGroup.appendChild(cuisineLabel);

    const cuisines = [
        { id: "indian", label: "🇮🇳 Indian" },
        { id: "mediterranean", label: "🫒 Mediterranean" },
        { id: "japanese", label: "🍱 Japanese" },
        { id: "western", label: "🥗 Western" }
    ];

    const currentCuisine = optionalUserData?.cuisine || document.getElementById("cuisine").value || "indian";

    cuisines.forEach(c => {
        const pill = el("button", `cuisine-pill-btn ${c.id === currentCuisine ? 'active' : ''}`, c.label);
        pill.addEventListener("click", () => {
            document.getElementById("cuisine").value = c.id;
            document.querySelectorAll(".cuisine-pill-btn").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            form.requestSubmit();
        });
        rightGroup.appendChild(pill);
    });

    toolbar.appendChild(leftGroup);
    toolbar.appendChild(rightGroup);
    mealResults.appendChild(toolbar);

    // Option C: Multi-Day Variety Tabs
    if (isMultiDay) {
        const tabsContainer = el("div", "day-tabs-container");
        const tabsLabel = el("div", "day-tabs-label", "📅 Multi-Day Variety Plan:");
        const tabBar = el("div", "day-tab-bar");

        mp.days.forEach((dayObj, idx) => {
            const dayNum = idx + 1;
            const dayCal = Math.round(dayObj.totals?.calories || nr.calories || 2000);
            const tabBtn = el("button", `day-tab-btn ${dayNum === currentActiveDayIndex ? 'active' : ''}`, `Day ${dayNum} (${dayCal} kcal)`);
            tabBtn.addEventListener("click", () => {
                currentActiveDayIndex = dayNum;
                renderCurrentPlanView();
            });
            tabBar.appendChild(tabBtn);
        });

        tabsContainer.appendChild(tabsLabel);
        tabsContainer.appendChild(tabBar);
        mealResults.appendChild(tabsContainer);
    }

    // 2. Optimization Precision & Macro Energy Distribution Card
    const targetCal = Number(nr.calories) || 1;
    const actualCal = Number(activeTotals.calories) || 0;
    const variancePercent = Math.abs((actualCal - targetCal) / targetCal) * 100;
    const rawAccuracy = 100 - variancePercent;
    const accuracyScore = Math.max(0, Math.min(100, rawAccuracy)).toFixed(1);

    const optCard = el("div", "optimization-card");
    optCard.innerHTML = `
        <div class="opt-card-header">
            <div>
                <span class="opt-badge-pill">🎯 ${accuracyScore}% Precision Match (±${variancePercent.toFixed(1)}% delta)</span>
                <span class="opt-solver-tag" style="margin-left: 10px;">SciPy SLSQP Constrained Solver · Bounded Portions</span>
            </div>
            <div class="opt-solver-tag">
                ${response.llm_engine ? `✦ Recipes: ${escapeHtml(response.llm_engine)}` : "✦ Verified Clinical Macro Engine"}
            </div>
        </div>

        <div class="macro-comparison-grid">
            <div class="macro-comp-card">
                <div class="mcc-icon">🔥</div>
                <div class="mcc-label">Calories</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(activeTotals.calories, 0)} <small>kcal</small></div>
                    <div class="mcc-target">Target: ${fmt(nr.calories, 0)} kcal</div>
                </div>
                <span class="mcc-diff ${variancePercent < 3 ? 'diff-match' : 'diff-close'}">
                    ${variancePercent < 1 ? 'Perfect Match' : `${variancePercent.toFixed(1)}% variance`}
                </span>
            </div>

            <div class="macro-comp-card">
                <div class="mcc-icon">💪</div>
                <div class="mcc-label">Protein</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(activeTotals.protein_g, 1)}g</div>
                    <div class="mcc-target">Target: ${fmt(nr.protein_g, 1)}g</div>
                </div>
                <span class="mcc-diff diff-match">${Math.round((activeTotals.protein_g * 4 / (activeTotals.calories || 1)) * 100)}% of energy</span>
            </div>

            <div class="macro-comp-card">
                <div class="mcc-icon">🌾</div>
                <div class="mcc-label">Carbohydrates</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(activeTotals.carbs_g, 1)}g</div>
                    <div class="mcc-target">Target: ${fmt(nr.carbs_g, 1)}g</div>
                </div>
                <span class="mcc-diff diff-match">${Math.round((activeTotals.carbs_g * 4 / (activeTotals.calories || 1)) * 100)}% of energy</span>
            </div>

            <div class="macro-comp-card">
                <div class="mcc-icon">🥑</div>
                <div class="mcc-label">Healthy Fats</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(activeTotals.fat_g, 1)}g</div>
                    <div class="mcc-target">Target: ${fmt(nr.fat_g, 1)}g</div>
                </div>
                <span class="mcc-diff diff-match">${Math.round((activeTotals.fat_g * 9 / (activeTotals.calories || 1)) * 100)}% of energy</span>
            </div>
        </div>

        <div class="macro-ratio-container">
            <div class="mrc-title-row">
                <span>MACRONUTRIENT CALORIC RATIO (4:4:9 kcal/g)</span>
                <span>Total: ${fmt(activeTotals.calories, 0)} kcal</span>
            </div>
            <div class="macro-split-bar">
                <div class="split-protein" style="width: ${(activeTotals.protein_g * 4 / (activeTotals.calories || 1) * 100).toFixed(1)}%;"></div>
                <div class="split-carbs" style="width: ${(activeTotals.carbs_g * 4 / (activeTotals.calories || 1) * 100).toFixed(1)}%;"></div>
                <div class="split-fat" style="width: ${(activeTotals.fat_g * 9 / (activeTotals.calories || 1) * 100).toFixed(1)}%;"></div>
            </div>
            <div class="mrc-legend">
                <span><span class="legend-dot" style="background: #e06d53;"></span> Protein (${(activeTotals.protein_g * 4 / (activeTotals.calories || 1) * 100).toFixed(0)}%)</span>
                <span><span class="legend-dot" style="background: #468ca8;"></span> Carbs (${(activeTotals.carbs_g * 4 / (activeTotals.calories || 1) * 100).toFixed(0)}%)</span>
                <span><span class="legend-dot" style="background: #e5b33d;"></span> Fat (${(activeTotals.fat_g * 9 / (activeTotals.calories || 1) * 100).toFixed(0)}%)</span>
            </div>
        </div>
    `;
    mealResults.appendChild(optCard);

    // 3. Render Per-Meal Cards
    const preferredOrder = ["Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner", "Snack"];
    const allMealKeys = Object.keys(activeMealPlanData);
    const mealOrder = [
        ...preferredOrder.filter(m => allMealKeys.includes(m)),
        ...allMealKeys.filter(m => !preferredOrder.includes(m))
    ];

    const mealsGrid = el("div", "meals-grid");

    const mealEmojis = {
        Breakfast: "🌅",
        "Morning Snack": "☕",
        Lunch: "☀️",
        "Evening Snack": "🍎",
        Dinner: "🌙",
        Snack: "🍎"
    };

    mealOrder.forEach(mealName => {
        const foods = activeMealPlanData[mealName];
        if (!foods || foods.length === 0) return;

        const recipe = activeRecipesData[mealName] || {};
        const card = el("div", "meal-card-full");

        const header = el("div", "meal-card-header");
        const nameRow = el("div", "meal-name-row");

        const leftNameGroup = el("div", "");
        leftNameGroup.style.display = "flex";
        leftNameGroup.style.alignItems = "center";
        leftNameGroup.style.gap = "8px";
        leftNameGroup.appendChild(el("span", "meal-emoji", mealEmojis[mealName] || "🍽️"));
        leftNameGroup.appendChild(el("span", "meal-name", mealName));
        nameRow.appendChild(leftNameGroup);

        // Option B: Swap Entire Meal Button
        const swapMealBtn = el("button", "btn-swap-meal", "🔁 Swap Meal");
        swapMealBtn.title = `Regenerate all dishes in ${mealName} with fresh ingredients`;
        swapMealBtn.addEventListener("click", () => executeMealSwap(mealName, swapMealBtn));
        nameRow.appendChild(swapMealBtn);

        header.appendChild(nameRow);

        if (recipe.dish_title) {
            header.appendChild(el("div", "dish-title", recipe.dish_title));
        }
        if (recipe.cooking_time) {
            header.appendChild(el("div", "cook-time", `⏱ Cook Time: ${recipe.cooking_time}`));
        }
        card.appendChild(header);

        // Foods Table with Swap Action Column
        const tableWrap = el("div", "meal-table-wrap");
        const table = el("table", "meal-food-table");

        const thead = document.createElement("thead");
        thead.innerHTML = `
            <tr>
                <th class="col-food">Food &amp; Serving</th>
                <th class="col-qty">Weight</th>
                <th class="col-num">Cal</th>
                <th class="col-num">Protein</th>
                <th class="col-num">Carbs</th>
                <th class="col-num">Fat</th>
                <th class="col-swap">Swap</th>
            </tr>
        `;
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        foods.forEach(f => {
            const tr = document.createElement("tr");

            const tdFood = el("td", "col-food");
            const foodCell = el("div", "food-cell");
            const raw = f.food || "—";
            const parts = raw.split(",");
            const mainTitle = parts[0].trim();
            const subTitle = parts.length > 1 ? parts.slice(1).join(",").trim() : "";
            const serving = getServingHint(f.food, f.grams);

            const strong = el("strong", "food-title", mainTitle);
            strong.title = raw;
            const desc = el("span", "food-desc", serving + (subTitle ? ` · ${subTitle}` : ''));
            foodCell.appendChild(strong);
            foodCell.appendChild(desc);
            tdFood.appendChild(foodCell);

            const tdQty = el("td", "col-qty", `${fmt(f.grams, 0)}g`);
            const tdCal = el("td", "col-num col-cal", fmt(f.calories, 0));
            const tdProt = el("td", "col-num col-macro", `${fmt(f.protein_g, 1)}g`);
            const tdCarb = el("td", "col-num col-macro", `${fmt(f.carbs_g, 1)}g`);
            const tdFat = el("td", "col-num col-macro", `${fmt(f.fat_g, 1)}g`);

            // Option B: Single Food Swap Button
            const tdSwap = el("td", "col-swap");
            const swapFoodBtn = el("button", "btn-swap-food", "⇄ Swap");
            swapFoodBtn.title = `Swap ${mainTitle} with a nutritionally equivalent food`;
            swapFoodBtn.addEventListener("click", () => openSwapFoodModal(f, mealName));
            tdSwap.appendChild(swapFoodBtn);

            tr.appendChild(tdFood);
            tr.appendChild(tdQty);
            tr.appendChild(tdCal);
            tr.appendChild(tdProt);
            tr.appendChild(tdCarb);
            tr.appendChild(tdFat);
            tr.appendChild(tdSwap);
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        tableWrap.appendChild(table);
        card.appendChild(tableWrap);

        // Recipe Drawer
        if (recipe.instructions && recipe.instructions.length > 0) {
            const toggle = el("button", "recipe-toggle", "▸ View AI Chef Recipe & Steps");
            const drawer = el("div", "recipe-drawer");
            drawer.style.display = "none";

            recipe.instructions.forEach((step, i) => {
                const s = el("div", "recipe-step");
                const num = el("span", "step-num", String(i + 1));
                const text = el("span", "", String(step));
                s.appendChild(num);
                s.appendChild(text);
                drawer.appendChild(s);
            });

            if (recipe.chef_notes) {
                const notes = el("p", "chef-notes", `✦ Chef's Note: ${recipe.chef_notes}`);
                drawer.appendChild(notes);
            }

            toggle.addEventListener("click", () => {
                const isOpen = drawer.style.display !== "none";
                drawer.style.display = isOpen ? "none" : "block";
                toggle.textContent = isOpen ? "▸ View AI Chef Recipe & Steps" : "▾ Hide Recipe";
            });

            card.appendChild(toggle);
            card.appendChild(drawer);
        }

        mealsGrid.appendChild(card);
    });

    mealResults.appendChild(mealsGrid);
}


// ─── Plan Customization & Interactive Swapping Engines ───────────────────────

function collectAllFdcIds(response) {
    const ids = [];
    if (!response || !response.meal_plan) return ids;
    const mp = response.meal_plan;
    if (mp.days && Array.isArray(mp.days)) {
        mp.days.forEach(d => {
            if (d.meal_plan) {
                Object.values(d.meal_plan).forEach(foods => {
                    if (Array.isArray(foods)) {
                        foods.forEach(f => { if (f.fdc_id) ids.push(Number(f.fdc_id)); });
                    }
                });
            }
        });
    }
    if (mp.meal_plan) {
        Object.values(mp.meal_plan).forEach(foods => {
            if (Array.isArray(foods)) {
                foods.forEach(f => { if (f.fdc_id) ids.push(Number(f.fdc_id)); });
            }
        });
    }
    return Array.from(new Set(ids));
}

function getActiveDayMealPlan() {
    if (!currentActivePlan || !currentActivePlan.response) return {};
    const mp = currentActivePlan.response.meal_plan;
    if (mp.days && Array.isArray(mp.days) && mp.days.length > 0) {
        const dayIdx = Math.max(0, Math.min(mp.days.length - 1, currentActiveDayIndex - 1));
        const dayObj = mp.days[dayIdx] || mp.days[0];
        return {
            meal_plan: dayObj.meal_plan,
            totals: dayObj.totals,
            status: "Optimal"
        };
    }
    return mp;
}

function updateActiveDayMealPlan(updatedMealPlan, updatedRecipes) {
    if (!currentActivePlan || !currentActivePlan.response) return;
    const mp = currentActivePlan.response.meal_plan;
    if (mp.days && Array.isArray(mp.days) && mp.days.length > 0) {
        const dayIdx = Math.max(0, Math.min(mp.days.length - 1, currentActiveDayIndex - 1));
        if (mp.days[dayIdx]) {
            mp.days[dayIdx].meal_plan = updatedMealPlan.meal_plan;
            mp.days[dayIdx].totals = updatedMealPlan.totals;
            if (updatedRecipes) {
                mp.days[dayIdx].recipes = Object.assign(mp.days[dayIdx].recipes || {}, updatedRecipes);
            }
        }
    }
    if (currentActiveDayIndex === 1 || !mp.days) {
        currentActivePlan.response.meal_plan.meal_plan = updatedMealPlan.meal_plan;
        currentActivePlan.response.meal_plan.totals = updatedMealPlan.totals;
        if (updatedRecipes) {
            currentActivePlan.response.recipes = Object.assign(currentActivePlan.response.recipes || {}, updatedRecipes);
        }
    }
}

// Option A Handler: Full Plan Regeneration
async function handleRegenerateAlternative(btnElement) {
    if (!currentActivePlan || !currentActivePlan.response) return;

    const existingIds = collectAllFdcIds(currentActivePlan.response);
    existingIds.forEach(id => currentExcludedFdcIds.add(id));
    currentVariationSeed += 1;

    if (btnElement) {
        btnElement.disabled = true;
        btnElement.innerHTML = "<span>⏳</span> Solving Alternative Plan…";
    }

    try {
        const user = currentActivePlan.user;
        const payload = buildPayload(user);
        payload.exclude_fdc_ids = Array.from(currentExcludedFdcIds);
        payload.variation_seed = currentVariationSeed;
        payload.plan_days = Number(user.plan_days || document.getElementById("plan_days")?.value || 1);

        const res = await fetch("/api/plan/regenerate-alternative", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Could not generate alternative plan.");
        }

        const result = await res.json();
        savePlanToHistory(payload, result);
        displayMealPlan(result, user);
    } catch (err) {
        alert("Alternative plan generation failed: " + err.message);
    } finally {
        if (btnElement) {
            btnElement.disabled = false;
            btnElement.innerHTML = "<span>🔄</span> Regenerate Alternative Plan";
        }
    }
}

// Option B Handler: Swap Entire Meal
async function executeMealSwap(mealName, btnElement) {
    if (btnElement) {
        btnElement.disabled = true;
        btnElement.textContent = "⏳ Swapping…";
    }

    try {
        const user = currentActivePlan.user;
        const activeDayPlan = getActiveDayMealPlan();
        const targets = currentActivePlan.response.nutrition_requirements || {};
        currentVariationSeed += 1;

        const allergies = user.allergies
            ? (Array.isArray(user.allergies) ? user.allergies : user.allergies.split(",").map(s => s.trim()).filter(Boolean))
            : [];

        const payload = {
            current_plan: activeDayPlan,
            targets: {
                calories: Number(targets.calories) || 2000,
                protein_g: Number(targets.protein_g) || 100,
                carbs_g: Number(targets.carbs_g) || 250,
                fat_g: Number(targets.fat_g) || 60
            },
            meal_name: mealName,
            cuisine: user.cuisine || "indian",
            diet_type: user.diet || user.diet_type || "vegetarian",
            user_prompt: user.user_prompt || "",
            allergies: allergies,
            variation_seed: currentVariationSeed
        };

        const res = await fetch("/api/plan/swap-meal", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Meal swap failed.");
        }

        const data = await res.json();
        updateActiveDayMealPlan(data.meal_plan, data.recipes);
        renderCurrentPlanView();
    } catch (err) {
        alert("Could not swap meal: " + err.message);
        if (btnElement) {
            btnElement.disabled = false;
            btnElement.textContent = "🔁 Swap Meal";
        }
    }
}

// Option B Handler: Food Item Swap Modal & Execution
async function openSwapFoodModal(foodItem, mealName) {
    if (!foodItem || !foodItem.fdc_id) {
        alert("Cannot swap this food item: identifier missing.");
        return;
    }
    const user = currentActivePlan?.user || getFormData();
    if (swapModalTitle) swapModalTitle.textContent = `⇄ Swap: ${foodItem.food.split(",")[0]}`;
    if (swapModalSubtitle) swapModalSubtitle.textContent = `Select a nutritionally matched replacement for ${mealName}. Portions will re-optimize automatically.`;

    if (swapModalOriginal) {
        swapModalOriginal.innerHTML = `
            <div>
                <strong>Current item:</strong> ${escapeHtml(foodItem.food)}
            </div>
            <div style="display: flex; gap: 8px; font-weight: 600;">
                <span>${fmt(foodItem.grams, 0)}g</span>
                <span>· ${fmt(foodItem.calories, 0)} kcal</span>
                <span>· ${fmt(foodItem.protein_g, 1)}g P</span>
                <span>· ${fmt(foodItem.carbs_g, 1)}g C</span>
                <span>· ${fmt(foodItem.fat_g, 1)}g F</span>
            </div>
        `;
    }

    if (swapModalBody) {
        swapModalBody.replaceChildren();
        const loader = el("div", "loader-box");
        loader.innerHTML = `
            <div class="loader-spinner"></div>
            <p>Finding nutritionally compatible alternatives…</p>
        `;
        swapModalBody.appendChild(loader);
    }

    if (swapModal) {
        swapModal.classList.add("active");
        swapModal.setAttribute("aria-hidden", "false");
    }
    if (swapModalBackdrop) {
        swapModalBackdrop.classList.add("active");
    }

    try {
        const allergies = user.allergies
            ? (Array.isArray(user.allergies) ? user.allergies : user.allergies.split(",").map(s => s.trim()).filter(Boolean))
            : [];

        const payload = {
            fdc_id: Number(foodItem.fdc_id),
            diet_type: user.diet || user.diet_type || "vegetarian",
            cuisine: user.cuisine || "indian",
            allergies: allergies,
            limit: 6
        };

        const res = await fetch("/api/plan/alternatives", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Could not fetch alternative foods.");
        const data = await res.json();
        const alts = data.alternatives || [];
        renderAlternativeList(foodItem, alts, mealName);
    } catch (err) {
        swapModalBody.innerHTML = `
            <div class="error-box">
                <p>Could not load alternatives: ${escapeHtml(err.message)}</p>
            </div>
        `;
    }
}

function renderAlternativeList(originalFood, alternatives, mealName) {
    swapModalBody.replaceChildren();
    if (alternatives.length === 0) {
        swapModalBody.innerHTML = `
            <div style="text-align: center; padding: 30px; color: var(--muted);">
                <p>No compatible alternatives found matching the current diet and allergen filters.</p>
            </div>
        `;
        return;
    }

    alternatives.forEach(alt => {
        const card = el("div", "alt-food-card");
        const parts = (alt.food || "").split(",");
        const mainTitle = parts[0].trim();
        const sub = parts.slice(1).join(",").trim();

        const info = el("div", "alt-food-info");
        info.innerHTML = `
            <div class="alt-food-title">${escapeHtml(mainTitle)} ${sub ? `<small style="font-weight: normal; color: #777;">(${escapeHtml(sub)})</small>` : ''}</div>
            <div class="alt-food-macros">
                <span class="alt-macro-pill">🔥 ${fmt(alt.calories_per_100g, 0)} kcal/100g</span>
                <span class="alt-macro-pill">💪 ${fmt(alt.protein_g, 1)}g P</span>
                <span class="alt-macro-pill">🌾 ${fmt(alt.carbs_g, 1)}g C</span>
                <span class="alt-macro-pill">🥑 ${fmt(alt.fat_g, 1)}g F</span>
            </div>
        `;

        const selectBtn = el("button", "btn-select-swap", "⇄ Select & Recalculate");
        selectBtn.addEventListener("click", async () => {
            selectBtn.disabled = true;
            selectBtn.textContent = "⏳ Optimizing…";
            await executeFoodSwap(originalFood.fdc_id, alt.fdc_id, mealName);
        });

        card.appendChild(info);
        card.appendChild(selectBtn);
        swapModalBody.appendChild(card);
    });
}

async function executeFoodSwap(fdcIdToReplace, replacementFdcId, mealName) {
    try {
        const user = currentActivePlan.user;
        const activeDayPlan = getActiveDayMealPlan();
        const targets = currentActivePlan.response.nutrition_requirements || {};

        const payload = {
            current_plan: activeDayPlan,
            targets: {
                calories: Number(targets.calories) || 2000,
                protein_g: Number(targets.protein_g) || 100,
                carbs_g: Number(targets.carbs_g) || 250,
                fat_g: Number(targets.fat_g) || 60
            },
            fdc_id_to_replace: Number(fdcIdToReplace),
            replacement_fdc_id: Number(replacementFdcId),
            cuisine: user.cuisine || "indian",
            diet_type: user.diet || user.diet_type || "vegetarian",
            user_prompt: user.user_prompt || ""
        };

        const res = await fetch("/api/plan/swap-item", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Swap optimization failed.");
        }

        const data = await res.json();
        updateActiveDayMealPlan(data.meal_plan, data.recipes);
        closeSwapModal();
        renderCurrentPlanView();
    } catch (err) {
        alert("Could not swap food: " + err.message);
    }
}

function closeSwapModal() {
    if (swapModal) {
        swapModal.classList.remove("active");
        swapModal.setAttribute("aria-hidden", "true");
    }
    if (swapModalBackdrop) {
        swapModalBackdrop.classList.remove("active");
    }
}

if (swapModalCloseBtn) swapModalCloseBtn.addEventListener("click", closeSwapModal);
if (swapModalBackdrop) swapModalBackdrop.addEventListener("click", closeSwapModal);


// ─── LocalStorage History Management ─────────────────────────────────────────

function getHistory() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        console.error("Failed to read history from localStorage:", e);
        return [];
    }
}

function savePlanToHistory(payload, result) {
    const history = getHistory();
    const entry = {
        id: "plan_" + Date.now(),
        timestamp: new Date().toISOString(),
        formattedDate: new Date().toLocaleDateString(undefined, {
            month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
        }),
        user: payload,
        response: result
    };

    // Prepend and keep top 15 plans
    history.unshift(entry);
    if (history.length > 15) history.pop();

    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
        console.warn("Could not save history to localStorage (quota exceeded?):", e);
    }

    updateHistoryUI();
}

function deleteHistoryItem(id) {
    let history = getHistory();
    history = history.filter(item => item.id !== id);
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {}
    updateHistoryUI();
    renderHistoryDrawer();
}

function clearAllHistory() {
    if (confirm("Are you sure you want to clear all saved meal plans?")) {
        try {
            localStorage.removeItem(STORAGE_KEY);
        } catch (e) {}
        updateHistoryUI();
        renderHistoryDrawer();
    }
}

function updateHistoryUI() {
    const history = getHistory();
    const count = history.length;

    if (historyBadge) historyBadge.textContent = count;
    if (topbarHistoryCount) topbarHistoryCount.textContent = count;
    if (historyCountLabel) historyCountLabel.textContent = `${count} saved plans in local memory`;

    // Update the sidebar preview card
    if (historyPreviewList) {
        historyPreviewList.replaceChildren();

        if (count === 0) {
            historyPreviewList.innerHTML = `<p class="empty-history-text">No plans saved yet. Generate a plan to see it here!</p>`;
        } else {
            // Show up to 3 recent plans
            history.slice(0, 3).forEach((item, idx) => {
                const div = el("div", "hp-item");
                const cal = item.response?.nutrition_requirements?.calories || item.response?.meal_plan?.totals?.calories || "--";
                const cuisine = capitalize(item.user?.cuisine || "General");

                div.innerHTML = `
                    <div class="hp-info">
                        <h5>${escapeHtml(cuisine)} · ${Math.round(cal)} kcal</h5>
                        <small>${escapeHtml(item.formattedDate)}</small>
                    </div>
                `;

                const loadBtn = el("button", "hp-load-btn", "Load");
                loadBtn.addEventListener("click", () => {
                    loadPlanFromHistory(item);
                });

                div.appendChild(loadBtn);
                historyPreviewList.appendChild(div);
            });
        }
    }
}

function renderHistoryDrawer() {
    const history = getHistory();
    historyDrawerList.replaceChildren();

    if (history.length === 0) {
        historyDrawerList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📜</div>
                <h3>No saved plans yet</h3>
                <p>Plans you generate are automatically saved here so you can reload them anytime without re-running.</p>
            </div>
        `;
        return;
    }

    history.forEach(item => {
        const nr = item.response?.nutrition_requirements || {};
        const mp = item.response?.meal_plan?.totals || {};
        const u = item.user || {};

        const card = el("div", "saved-plan-card");
        card.innerHTML = `
            <div class="spc-top">
                <span class="spc-time">${escapeHtml(item.formattedDate)}</span>
                <span class="spc-cuisine-tag">${escapeHtml(capitalize(u.cuisine || 'indian'))}</span>
            </div>
            <h4 class="spc-title">${escapeHtml(u.name || 'Personalized')} Plan (${Math.round(nr.calories || mp.calories || 2000)} kcal)</h4>
            <div class="spc-chips">
                <span class="spc-chip">${escapeHtml(capitalize(u.diet_type || 'Vegetarian'))}</span>
                <span class="spc-chip">${escapeHtml(capitalize(u.goal?.replace('_', ' ') || 'Maintenance'))}</span>
                <span class="spc-chip">${u.weight_kg ? `${escapeHtml(u.weight_kg)} kg` : ''}</span>
                ${u.target_weight_kg ? `<span class="spc-chip">Goal: ${escapeHtml(u.target_weight_kg)} kg</span>` : ''}
            </div>
            <div class="spc-macros">
                <div class="spc-macro-item">
                    <span>Calories</span>
                    <strong>${fmt(mp.calories || nr.calories, 0)}</strong>
                </div>
                <div class="spc-macro-item">
                    <span>Protein</span>
                    <strong>${fmt(mp.protein_g || nr.protein_g, 1)}g</strong>
                </div>
                <div class="spc-macro-item">
                    <span>Carbs</span>
                    <strong>${fmt(mp.carbs_g || nr.carbs_g, 1)}g</strong>
                </div>
                <div class="spc-macro-item">
                    <span>Fat</span>
                    <strong>${fmt(mp.fat_g || nr.fat_g, 1)}g</strong>
                </div>
            </div>
        `;

        const actions = el("div", "spc-actions");
        const loadBtn = el("button", "btn-load-plan", "⚡ Load This Plan");
        loadBtn.addEventListener("click", () => {
            loadPlanFromHistory(item);
            closeHistoryDrawer();
        });

        const deleteBtn = el("button", "btn-delete-plan", "🗑️");
        deleteBtn.title = "Delete this plan";
        deleteBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            deleteHistoryItem(item.id);
        });

        actions.appendChild(loadBtn);
        actions.appendChild(deleteBtn);
        card.appendChild(actions);

        historyDrawerList.appendChild(card);
    });
}

function loadPlanFromHistory(historyItem) {
    if (!historyItem || !historyItem.response) return;

    // Restore form values if present
    const u = historyItem.user || {};
    if (u.name) document.getElementById("name").value = u.name;
    if (u.age) document.getElementById("age").value = u.age;
    if (u.sex || u.gender) document.getElementById("gender").value = u.sex || u.gender;
    if (u.weight_kg || u.weight) document.getElementById("weight").value = u.weight_kg || u.weight;
    if (u.target_weight_kg || u.target_weight) document.getElementById("target_weight").value = u.target_weight_kg || u.target_weight;
    if (u.height_cm || u.height) document.getElementById("height").value = u.height_cm || u.height;
    if (u.activity_level || u.activity) document.getElementById("activity").value = u.activity_level || u.activity;
    if (u.goal) document.getElementById("goal").value = u.goal;
    if (u.diet_type || u.diet) {
        const dietVal = (u.diet_type || u.diet).replace("-", "_");
        document.getElementById("diet").value = dietVal;
    }
    if (u.cuisine) document.getElementById("cuisine").value = u.cuisine;
    if (u.plan_days && document.getElementById("plan_days")) document.getElementById("plan_days").value = String(u.plan_days);
    if (u.user_prompt) document.getElementById("user_prompt").value = u.user_prompt;

    // Re-calculate biometrics
    calculateBiometricsLive();

    // Render the meal plan directly
    displayMealPlan(historyItem.response, u);

    // Smooth scroll to results
    document.getElementById("meal-section").scrollIntoView({ behavior: "smooth" });
}

function openHistoryDrawer() {
    renderHistoryDrawer();
    historyDrawer.classList.add("active");
    historyDrawerBackdrop.classList.add("active");
    historyDrawer.setAttribute("aria-hidden", "false");
}

function closeHistoryDrawer() {
    historyDrawer.classList.remove("active");
    historyDrawerBackdrop.classList.remove("active");
    historyDrawer.setAttribute("aria-hidden", "true");
}

[openHistoryBtn, historyNavBtn, heroHistoryBtn, historyPreviewViewAll].forEach(btn => {
    if (btn) btn.addEventListener("click", openHistoryDrawer);
});

if (historyDrawerCloseBtn) historyDrawerCloseBtn.addEventListener("click", closeHistoryDrawer);
if (historyDrawerBackdrop) historyDrawerBackdrop.addEventListener("click", closeHistoryDrawer);
if (clearHistoryBtn) clearHistoryBtn.addEventListener("click", clearAllHistory);


// ─── Smart Grocery Shopping List Generator ───────────────────────────────────

function categorizeFood(foodName) {
    const fn = (foodName || "").toLowerCase();

    if (
        fn.includes("spinach") || fn.includes("palak") || fn.includes("methi") ||
        fn.includes("tomato") || fn.includes("onion") || fn.includes("potato") ||
        fn.includes("cucumber") || fn.includes("bell pepper") || fn.includes("capsicum") ||
        fn.includes("carrot") || fn.includes("cauliflower") || fn.includes("gobi") ||
        fn.includes("peas") || fn.includes("mushroom") || fn.includes("apple") ||
        fn.includes("banana") || fn.includes("lettuce") || fn.includes("salad") ||
        fn.includes("edamame") || fn.includes("lemon") || fn.includes("ginger") ||
        fn.includes("garlic") || fn.includes("vegetable")
    ) {
        return "🥬 Fresh Produce";
    }

    if (
        fn.includes("chapati") || fn.includes("roti") || fn.includes("wheat") ||
        fn.includes("rice") || fn.includes("poha") || fn.includes("upma") ||
        fn.includes("oats") || fn.includes("quinoa") || fn.includes("bread") ||
        fn.includes("pita") || fn.includes("khichdi") || fn.includes("flour")
    ) {
        return "🌾 Grains, Cereals & Flours";
    }

    if (
        fn.includes("milk") || fn.includes("yogurt") || fn.includes("curd") ||
        fn.includes("paneer") || fn.includes("cheese") || fn.includes("butter")
    ) {
        return "🥛 Dairy & Alternatives";
    }

    if (
        fn.includes("dal") || fn.includes("lentil") || fn.includes("chana") ||
        fn.includes("chickpea") || fn.includes("rajma") || fn.includes("tofu") ||
        fn.includes("chicken") || fn.includes("egg") || fn.includes("fish") ||
        fn.includes("salmon") || fn.includes("souvlaki") || fn.includes("turkey")
    ) {
        return "🫘 Legumes, Lentils & Proteins";
    }

    if (
        fn.includes("ghee") || fn.includes("oil") || fn.includes("almond") ||
        fn.includes("peanut") || fn.includes("walnut") || fn.includes("nut") ||
        fn.includes("chia") || fn.includes("flax")
    ) {
        return "🌰 Healthy Fats, Nuts & Seeds";
    }

    return "🧂 Pantry, Spices & Condiments";
}

function generateGroceryData(plan) {
    if (!plan || !plan.response || !plan.response.meal_plan) return {};

    const mp = plan.response.meal_plan;
    const consolidated = {};

    function addMeals(mealData) {
        if (!mealData) return;
        Object.keys(mealData).forEach(mealType => {
            const items = mealData[mealType] || [];
            items.forEach(item => {
                const rawName = (item.food || "").trim();
                if (!rawName) return;

                const category = categorizeFood(rawName);
                if (!consolidated[category]) consolidated[category] = {};

                if (consolidated[category][rawName]) {
                    consolidated[category][rawName] += Number(item.grams) || 0;
                } else {
                    consolidated[category][rawName] = Number(item.grams) || 0;
                }
            });
        });
    }

    if (mp.days && Array.isArray(mp.days) && mp.days.length > 0) {
        mp.days.forEach(d => addMeals(d.meal_plan));
    } else {
        addMeals(mp.meal_plan || {});
    }

    return consolidated;
}

function openGroceryModal(plan) {
    if (!plan) {
        alert("Please generate or load a meal plan first to view its grocery list.");
        return;
    }

    const categorized = generateGroceryData(plan);
    groceryContent.replaceChildren();

    let totalItems = 0;

    Object.keys(categorized).forEach(cat => {
        const itemsObj = categorized[cat];
        const itemNames = Object.keys(itemsObj);
        if (itemNames.length === 0) return;

        totalItems += itemNames.length;

        const block = el("div", "grocery-category-block");
        const title = el("div", "gcb-title", cat);
        block.appendChild(title);

        const itemsContainer = el("div", "gcb-items");

        itemNames.forEach(itemName => {
            const grams = itemsObj[itemName];
            const row = el("div", "grocery-item-row");

            const left = el("div", "grocery-item-left");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.addEventListener("change", () => {
                row.classList.toggle("checked", checkbox.checked);
            });

            const nameSpan = el("span", "item-title", itemName);
            left.appendChild(checkbox);
            left.appendChild(nameSpan);

            const qtySpan = el("span", "item-qty", grams >= 1000 ? `${(grams/1000).toFixed(2)} kg` : `${Math.round(grams)} g`);

            row.appendChild(left);
            row.appendChild(qtySpan);
            itemsContainer.appendChild(row);
        });

        block.appendChild(itemsContainer);
        groceryContent.appendChild(block);
    });

    if (groceryItemCount) groceryItemCount.textContent = `${totalItems} distinct items`;

    groceryModal.classList.add("active");
    groceryModalBackdrop.classList.add("active");
    groceryModal.setAttribute("aria-hidden", "false");
}

function closeGroceryModal() {
    groceryModal.classList.remove("active");
    groceryModalBackdrop.classList.remove("active");
    groceryModal.setAttribute("aria-hidden", "true");
}

if (groceryModalCloseBtn) groceryModalCloseBtn.addEventListener("click", closeGroceryModal);
if (groceryModalBackdrop) groceryModalBackdrop.addEventListener("click", closeGroceryModal);
if (sidebarGroceryBtn) sidebarGroceryBtn.addEventListener("click", () => openGroceryModal(currentActivePlan));

// Copy Grocery List to Clipboard
if (copyGroceryBtn) {
    copyGroceryBtn.addEventListener("click", () => {
        if (!currentActivePlan) return;
        const categorized = generateGroceryData(currentActivePlan);
        let text = "🛒 NUTRIGEN-AI GROCERY SHOPPING LIST\n====================================\n\n";

        Object.keys(categorized).forEach(cat => {
            text += `[ ${cat} ]\n`;
            Object.keys(categorized[cat]).forEach(name => {
                const g = categorized[cat][name];
                const qty = g >= 1000 ? `${(g/1000).toFixed(2)} kg` : `${Math.round(g)} g`;
                text += `  • [ ] ${name} — ${qty}\n`;
            });
            text += "\n";
        });

        navigator.clipboard.writeText(text).then(() => {
            const original = copyGroceryBtn.textContent;
            copyGroceryBtn.textContent = "✓ Copied to Clipboard!";
            setTimeout(() => { copyGroceryBtn.textContent = original; }, 2000);
        }).catch(err => {
            console.error("Clipboard write error:", err);
            alert("Could not copy automatically. Please select text manually.");
        });
    });
}

// Print Grocery List
if (printGroceryBtn) {
    printGroceryBtn.addEventListener("click", () => {
        window.print();
    });
}


// ─── Clinical Print / PDF Export ─────────────────────────────────────────────

function exportPlanToPrint(plan) {
    if (!plan) {
        alert("Please generate or load a meal plan first to print.");
        return;
    }

    const printContainer = document.getElementById("printableReport");
    const u = plan.user || {};
    const nr = plan.response?.nutrition_requirements || {};
    const totals = plan.response?.meal_plan?.totals || {};
    const bio = plan.response?.biometrics || {};

    printContainer.innerHTML = `
        <div class="print-report-header">
            <div>
                <h1>NutriGEN-AI Clinical Nutrition Report</h1>
                <p>Personalized Precision Nutrition & Meal Prescription</p>
                <p><strong>Patient / User:</strong> ${escapeHtml(u.name || "Client")} | <strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
            </div>
            <div style="text-align: right;">
                <p><strong>Calorie Target:</strong> ${fmt(totals.calories || nr.calories, 0)} kcal/day</p>
                <p><strong>BMR:</strong> ${fmt(bio.bmr || nr.bmr, 0)} kcal | <strong>TDEE:</strong> ${fmt(bio.tdee || nr.tdee, 0)} kcal</p>
                <p><strong>BMI:</strong> ${fmt(bio.bmi, 1)} (${escapeHtml(bio.bmi_category || 'Normal')})</p>
            </div>
        </div>
    `;

    window.print();
}

if (sidebarPrintBtn) {
    sidebarPrintBtn.addEventListener("click", () => exportPlanToPrint(currentActivePlan));
}


// ─── Demo Auto-Fill (For Rapid Evaluation & Presentation) ─────────────────────

if (demoBtn) {
    demoBtn.addEventListener("click", () => {
        document.getElementById("name").value = "Abhinav Sharma";
        document.getElementById("age").value = "23";
        document.getElementById("gender").value = "male";
        document.getElementById("weight").value = "76.0";
        document.getElementById("target_weight").value = "70.0";
        document.getElementById("height").value = "176";
        document.getElementById("activity").value = "moderate";
        document.getElementById("goal").value = "weight_loss";
        document.getElementById("diet").value = "vegetarian";
        document.getElementById("cuisine").value = "indian";
        document.getElementById("meals").value = "4";
        if (document.getElementById("plan_days")) document.getElementById("plan_days").value = "1";
        document.getElementById("allergies").value = "Peanuts";
        document.getElementById("user_prompt").value = "Quick authentic meals, high protein, flavorful spices, no oven";

        // Trigger recalculation immediately
        calculateBiometricsLive();

        // Give quick visual indicator on button
        const oldText = demoBtn.innerHTML;
        demoBtn.innerHTML = "<span>✓</span> Loaded Demo";
        setTimeout(() => { demoBtn.innerHTML = oldText; }, 1500);
    });
}


// ─── Main Form Submission ────────────────────────────────────────────────────

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = getFormData();

    if (!data.age || data.age < 15 || !data.weight || data.weight <= 0 || !data.height || data.height <= 0) {
        alert("Please enter valid clinical health details (age >= 15, positive weight and height).");
        return;
    }

    calculateBiometricsLive();

    generateBtn.disabled = true;
    generateBtn.innerHTML = "Solving Optimization & Crafting Recipes… <span>⏳</span>";

    mealResults.replaceChildren();
    const loader = el("div", "loader-box");
    loader.innerHTML = `
        <div class="loader-spinner"></div>
        <h3>NutriGEN-AI Optimizer Running</h3>
        <p>Executing SciPy SLSQP constrained numerical solver & Groq Llama 3.1 AI Chef recipe generation…</p>
    `;
    mealResults.appendChild(loader);

    try {
        const payload = buildPayload(data);

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errBody = await response.json().catch(() => ({}));
            throw new Error(
                errBody.detail || `Server Error (${response.status}): ${response.statusText}`
            );
        }

        const result = await response.json();

        // Save plan to localStorage history automatically
        savePlanToHistory(payload, result);

        // Display results
        displayMealPlan(result, data);

        // Scroll down smoothly to results section
        document.getElementById("meal-section").scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        console.error("Meal plan generation error:", error);
        mealResults.replaceChildren();

        const errBox = el("div", "error-box");
        errBox.innerHTML = `
            <div class="error-icon">⚠️</div>
            <h3>Could Not Generate Meal Plan</h3>
            <p>${escapeHtml(error.message) || "Ensure your backend server is active at http://127.0.0.1:8000"}</p>
            <p style="margin-top: 10px; font-size: 11px; color: #777;">
                To launch the server: <code>python -m uvicorn Backend.server:app --reload --port 8000</code>
            </p>
        `;
        mealResults.appendChild(errBox);

    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = "Generate Clinically Optimized Meal Plan <span>→</span>";
    }
});


// ─── Initial Page Load Initialization ────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    // Populate default biometrics
    calculateBiometricsLive();

    // Load any existing history from localStorage
    updateHistoryUI();
});
