document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recipe-form');
    const loadingSection = document.getElementById('loading-section');
    const recipeDisplay = document.getElementById('recipe-display');
    const recipeContent = document.getElementById('recipe-content');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    
    const btnClear = document.getElementById('btn-clear');
    const btnRandom = document.getElementById('btn-random');

    // Handle Form Clear
    btnClear.addEventListener('click', () => {
        form.reset();
        recipeDisplay.classList.add('hidden');
        errorSection.classList.add('hidden');
    });

    // Handle Random Recipe Fill
    btnRandom.addEventListener('click', () => {
        const randomItems = {
            cuisine: ["Indian", "Italian", "Mexican", "Japanese", "Mediterranean"],
            ingredients: ["Chicken, Rice, Onion", "Pasta, Tomatoes, Garlic", "Eggs, Spinach, Cheese", "Tofu, Broccoli, Soy Sauce"],
            diet: ["None", "Vegetarian", "High Protein", "Low Carb"],
            cooking_time: ["20 minutes", "30 minutes", "60 minutes"]
        };
        
        document.getElementById('cuisine').value = randomItems.cuisine[Math.floor(Math.random() * randomItems.cuisine.length)];
        document.getElementById('ingredients').value = randomItems.ingredients[Math.floor(Math.random() * randomItems.ingredients.length)];
        document.getElementById('diet').value = randomItems.diet[Math.floor(Math.random() * randomItems.diet.length)];
        document.getElementById('cooking_time').value = randomItems.cooking_time[Math.floor(Math.random() * randomItems.cooking_time.length)];
    });

    // Handle Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!navigator.onLine) {
            showError("No internet connection detected. Please check your network.");
            return;
        }

        // Gather Data
        const requestData = {
            skill_level: document.getElementById('skill_level').value,
            age: document.getElementById('age').value,
            diet: document.getElementById('diet').value,
            health_goal: document.getElementById('health_goal').value,
            taste_preference: document.getElementById('taste_preference').value,
            cuisine: document.getElementById('cuisine').value,
            spice_level: document.getElementById('spice_level').value,
            servings: parseInt(document.getElementById('servings').value),
            budget: document.getElementById('budget').value,
            cooking_time: document.getElementById('cooking_time').value,
            ingredients: document.getElementById('ingredients').value.trim(),
            avoid_ingredients: document.getElementById('avoid_ingredients').value.trim(),
            allergies: document.getElementById('allergies').value.trim()
        };

        // UI Updates
        form.style.opacity = '0.5';
        loadingSection.classList.remove('hidden');
        recipeDisplay.classList.add('hidden');
        errorSection.classList.add('hidden');
        document.getElementById('btn-generate').disabled = true;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout

            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Server error occurred");
            }

            // Parse Markdown to HTML
            recipeContent.innerHTML = marked.parse(data.data);
            recipeDisplay.classList.remove('hidden');

        } catch (error) {
            console.error(error);
            if (error.name === 'AbortError') {
                showError("The request to ChefAI timed out. Please try again.");
            } else {
                showError(`API Error: ${error.message}`);
            }
        } finally {
            form.style.opacity = '1';
            loadingSection.classList.add('hidden');
            document.getElementById('btn-generate').disabled = false;
            
            // Scroll to results or error
            if(!recipeDisplay.classList.contains('hidden')) {
                recipeDisplay.scrollIntoView({ behavior: 'smooth' });
            } else if (!errorSection.classList.contains('hidden')) {
                errorSection.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorSection.classList.remove('hidden');
    }
});