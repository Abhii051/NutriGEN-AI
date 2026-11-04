// NutriGEN-AI Frontend Logic
// Connects to the FastAPI backend at http://127.0.0.1:8000

const API_URL = "http://127.0.0.1:8000/api/generate-plan";

const form = document.getElementById("nutritionForm");
const generateBtn = document.getElementById("generateBtn");
const mealResults = document.getElementById("mealResults");


// ─── Helpers ─────────────────────────────────────────────────────────────────

function el(tag, className, text) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    if (text !== undefined) e.textContent = text;
    return e;
}

function fmt(n, decimals = 1) {
    return Number(n).toFixed(decimals);
}


// ─── BMI & stat-card update ───────────────────────────────────────────────────

function updateStatCards(data) {
    const h = data.height / 100;
    const bmi = data.weight / (h * h);

    let bmiStatus = "Normal weight";
    if (bmi < 18.5) bmiStatus = "Underweight";
    else if (bmi >= 25 && bmi < 30) bmiStatus = "Overweight";
    else if (bmi >= 30) bmiStatus = "Obese range";

    // Mifflin-St Jeor
    let bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age;
    if (data.gender === "male") bmr += 5;
    else if (data.gender === "female") bmr -= 161;
    else bmr -= 78;

    const activityFactors = {
        sedentary: 1.2, light: 1.375, moderate: 1.55,
        active: 1.725, very_active: 1.9
    };
    let calories = bmr * (activityFactors[data.activity] || 1.55);
    if (data.goal === "weight_loss") calories -= 300;
    if (data.goal === "weight_gain") calories += 300;

    document.getElementById("bmiValue").textContent = bmi.toFixed(1);
    document.getElementById("bmiStatus").textContent = bmiStatus;
    document.getElementById("calorieValue").innerHTML =
        `${Math.round(calories)} <small>kcal</small>`;

    const goalNames = {
        weight_loss: "Weight Loss",
        weight_gain: "Weight Gain",
        maintenance: "Maintenance"
    };
    document.getElementById("goalValue").textContent =
        goalNames[data.goal] || data.goal;
}


// ─── Collect form data ────────────────────────────────────────────────────────

function getFormData() {
    return {
        name:       document.getElementById("name").value.trim(),
        age:        Number(document.getElementById("age").value),
        gender:     document.getElementById("gender").value,
        weight:     Number(document.getElementById("weight").value),
        height:     Number(document.getElementById("height").value),
        activity:   document.getElementById("activity").value,
        goal:       document.getElementById("goal").value,
        diet:       document.getElementById("diet").value,
        cuisine:    document.getElementById("cuisine").value || "indian",
        allergies:  document.getElementById("allergies").value.trim(),
        meals:      Number(document.getElementById("meals").value),
        user_prompt: document.getElementById("user_prompt").value.trim()
    };
}


// ─── Map form → backend schema ────────────────────────────────────────────────

function buildPayload(data) {
    // diet_type mapping
    let diet_type = data.diet;
    let eats_eggs = false;
    if (data.diet === "eggetarian") {
        diet_type = "vegetarian";
        eats_eggs = true;
    } else if (data.diet === "non_vegetarian") {
        diet_type = "non-vegetarian";
    }

    // sex: backend only accepts "male" / "female"
    const sex = (data.gender === "female") ? "female" : "male";

    // meals → number_of_meals + number_of_snacks
    // 3 → 3 meals, 0 snacks
    // 4 → 3 meals, 1 snack
    // 5 → 3 meals, 2 snacks
    const number_of_snacks = Math.max(0, data.meals - 3);
    const number_of_meals  = 3;

    // allergies: comma-separated string → array, filter blanks
    const allergies = data.allergies
        ? data.allergies.split(",").map(s => s.trim()).filter(Boolean)
        : [];

    return {
        age:             data.age,
        sex,
        height_cm:       data.height,
        weight_kg:       data.weight,
        activity_level:  data.activity,
        goal:            data.goal,
        diet_type,
        eats_eggs,
        allergies,
        cuisine:         data.cuisine,
        number_of_meals,
        number_of_snacks,
        user_prompt:     data.user_prompt || ""
    };
}


// ─── Render the API response ──────────────────────────────────────────────────

function displayMealPlan(response) {
    mealResults.replaceChildren();

    // ── Macro summary bar ──────────────────────────────────────────────────────
    const nr = response.nutrition_requirements || {};
    const mp = response.meal_plan || {};
    const totals = mp.totals || {};

    const summarySection = el("div", "nr-summary");

    const summaryTitle = el("h3", "nr-title", "Nutrition Targets");
    summarySection.appendChild(summaryTitle);

    const macroGrid = el("div", "macro-grid");

    const macros = [
        { label: "Calories",   target: nr.calories,   actual: totals.calories,   unit: "kcal", icon: "🔥" },
        { label: "Protein",    target: nr.protein_g,  actual: totals.protein_g,  unit: "g",    icon: "💪" },
        { label: "Carbs",      target: nr.carbs_g,    actual: totals.carbs_g,    unit: "g",    icon: "🌾" },
        { label: "Fat",        target: nr.fat_g,      actual: totals.fat_g,      unit: "g",    icon: "🥑" }
    ];

    macros.forEach(m => {
        const card = el("div", "macro-card");
        card.innerHTML = `
            <div class="macro-icon">${m.icon}</div>
            <div class="macro-label">${m.label}</div>
            <div class="macro-target">${m.target != null ? fmt(m.target, 0) : "--"} ${m.unit}</div>
            <div class="macro-actual">${m.actual != null ? fmt(m.actual, 0) : "--"} ${m.unit} <span>achieved</span></div>
        `;
        macroGrid.appendChild(card);
    });

    summarySection.appendChild(macroGrid);

    // LLM engine badge
    if (response.llm_engine) {
        const badge = el("div", "engine-badge", `✦ Generated by ${response.llm_engine}`);
        summarySection.appendChild(badge);
    }

    mealResults.appendChild(summarySection);

    // ── Per-meal cards ─────────────────────────────────────────────────────────
    const mealPlanData = mp.meal_plan || {};   // { Breakfast: [...], Lunch: [...], ... }
    const recipesData  = response.recipes || mp.recipes || {};

    const mealOrder = ["Breakfast", "Lunch", "Dinner", "Snack"];

    // Build meal cards in a grid
    const mealsGrid = el("div", "meals-grid");

    mealOrder.forEach(mealName => {
        const foods = mealPlanData[mealName];
        if (!foods || foods.length === 0) return;

        const recipe = recipesData[mealName] || {};

        const card = el("div", "meal-card-full");

        // Card header
        const cardHeader = el("div", "meal-card-header");
        const mealEmojis = { Breakfast: "🌅", Lunch: "☀️", Dinner: "🌙", Snack: "🍎" };
        cardHeader.innerHTML = `
            <div class="meal-name-row">
                <span class="meal-emoji">${mealEmojis[mealName] || "🍽️"}</span>
                <span class="meal-name">${mealName}</span>
            </div>
            ${recipe.dish_title ? `<div class="dish-title">${recipe.dish_title}</div>` : ""}
            ${recipe.cooking_time ? `<div class="cook-time">⏱ ${recipe.cooking_time}</div>` : ""}
        `;
        card.appendChild(cardHeader);

        // Food items table
        const foodTable = el("div", "food-table");
        const tableHeader = el("div", "food-row food-row-header");
        tableHeader.innerHTML = `
            <span>Food</span>
            <span>Amount</span>
            <span>Cal</span>
            <span>P</span>
            <span>C</span>
            <span>F</span>
        `;
        foodTable.appendChild(tableHeader);

        foods.forEach(food => {
            const row = el("div", "food-row");
            row.innerHTML = `
                <span class="food-name" title="${food.food || ""}">${food.food || "—"}</span>
                <span class="food-grams">${fmt(food.grams, 0)}g</span>
                <span class="food-cal">${fmt(food.calories, 0)}</span>
                <span class="food-macro">${fmt(food.protein_g, 1)}g</span>
                <span class="food-macro">${fmt(food.carbs_g, 1)}g</span>
                <span class="food-macro">${fmt(food.fat_g, 1)}g</span>
            `;
            foodTable.appendChild(row);
        });

        card.appendChild(foodTable);

        // Recipe section
        if (recipe.instructions && recipe.instructions.length > 0) {
            const recipeToggle = el("button", "recipe-toggle", "▸ View Recipe");
            const recipeDrawer = el("div", "recipe-drawer");
            recipeDrawer.style.display = "none";

            recipe.instructions.forEach((step, i) => {
                const stepEl = el("div", "recipe-step");
                stepEl.innerHTML = `<span class="step-num">${i + 1}</span><span>${step}</span>`;
                recipeDrawer.appendChild(stepEl);
            });

            if (recipe.chef_notes) {
                const notes = el("p", "chef-notes", `✦ ${recipe.chef_notes}`);
                recipeDrawer.appendChild(notes);
            }

            recipeToggle.addEventListener("click", () => {
                const open = recipeDrawer.style.display !== "none";
                recipeDrawer.style.display = open ? "none" : "block";
                recipeToggle.textContent = open ? "▸ View Recipe" : "▾ Hide Recipe";
            });

            card.appendChild(recipeToggle);
            card.appendChild(recipeDrawer);
        }

        mealsGrid.appendChild(card);
    });

    mealResults.appendChild(mealsGrid);
}


// ─── Form submission ──────────────────────────────────────────────────────────

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = getFormData();

    // Basic validation
    if (
        !Number.isFinite(data.age)    || data.age    <= 0 ||
        !Number.isFinite(data.weight) || data.weight <= 0 ||
        !Number.isFinite(data.height) || data.height <= 0
    ) {
        alert("Please enter valid health details (age, weight, height).");
        return;
    }

    // Update stat cards immediately with client-side estimates
    updateStatCards(data);

    // Disable button & show loader
    generateBtn.disabled = true;
    generateBtn.textContent = "Generating your meal plan…";

    mealResults.replaceChildren();
    const loader = el("div", "loader-box");
    loader.innerHTML = `
        <div class="loader-spinner"></div>
        <p>Analysing your profile and crafting a personalised meal plan with AI chef recipes…</p>
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
                errBody.detail ||
                `Backend error: ${response.status} ${response.statusText}`
            );
        }

        const result = await response.json();

        displayMealPlan(result);

        document.getElementById("meal-section").scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        console.error("Meal plan generation error:", error);
        mealResults.replaceChildren();

        const errorBox = el("div", "error-box");
        errorBox.innerHTML = `
            <div class="error-icon">⚠️</div>
            <h3>Could not generate meal plan</h3>
            <p>${error.message || "Make sure your backend server is running at http://127.0.0.1:8000"}</p>
            <p class="error-hint">Start the server with: <code>python Backend/main.py</code></p>
        `;
        mealResults.appendChild(errorBox);

    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = 'Generate My Meal Plan <span>→</span>';
    }
});
