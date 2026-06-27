import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq, GroqError

# Load environment variables securely
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="COOKED!",
    description="Backend for COOKED! - Intelligent Cooking Companion",
    version="1.0.0"
)

# CORS Middleware for allowing cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)

# Pydantic Model for Input Validation
class RecipeRequest(BaseModel):
    item_name: str = Field(default="") # <-- Added Desired Dish Field!
    skill_level: str = Field(default="Beginner")
    age: str = Field(default="Adult")
    diet: str = Field(default="None")
    health_goal: str = Field(default="None")
    taste_preference: str = Field(default="Balanced")
    cuisine: str = Field(default="Any")
    spice_level: str = Field(default="Medium")
    servings: int = Field(default=2, ge=1)
    budget: str = Field(default="Medium")
    cooking_time: str = Field(default="30 minutes")
    ingredients: str = Field(default="")
    avoid_ingredients: str = Field(default="")
    allergies: str = Field(default="None")

@app.get("/")
async def read_root(request: Request):
    """Returns the homepage"""
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/generate")
async def generate_recipe(request: RecipeRequest):
    """Generates a personalized recipe using Groq AI"""
    
    system_prompt = """You are COOKED!, an intelligent world-class AI cooking assistant with expertise in global cuisines, nutrition, food science, meal planning, and culinary techniques.
    
    Your goal is to generate highly personalized recipes based on the user's provided profile. 
    If requested ingredients are missing, recommend affordable substitutions. Never recommend ingredients that violate dietary restrictions or allergies.
    
    You MUST format your response strictly in Markdown, containing exactly the following sections in this order:
    
    ## Recipe Name
    ## Cuisine
    ## Difficulty
    ## Preparation Time
    ## Cooking Time
    ## Total Time
    ## Estimated Cost
    ## Calories
    ## Nutrition Facts (Protein, Fat, Carbohydrates, Fiber, Sugar, Sodium)
    ## Ingredients
    ## Missing Ingredients
    ## Ingredient Substitutions
    ## Step-by-Step Instructions
    ## Cooking Tips
    ## Common Mistakes
    ## Taste Customization
    ## Serving Suggestions
    ## Side Dish Recommendation
    ## Dessert Recommendation
    ## Beverage Pairing
    ## Storage Instructions
    ## Reheating Instructions
    ## Leftover Ideas
    ## Meal Type
    ## Healthy Alternative
    ## Kid-Friendly Version
    ## Senior-Friendly Version
    ## Meal Prep Tips
    ## Grocery Shopping List
    ## AI Chef Recommendation
    
    Keep the response visually organized and easy to read."""

    # Added the Desired Dish (item_name) parameter to the AI's prompt below!
    user_prompt = f"""
    Please create a personalized recipe with the following parameters:
    - Desired Dish: {request.item_name if request.item_name else 'Suggest any matching recipe'}
    - Cooking Skill: {request.skill_level}
    - Age Group: {request.age}
    - Diet: {request.diet}
    - Health Goal: {request.health_goal}
    - Taste Preference: {request.taste_preference}
    - Cuisine Preference: {request.cuisine}
    - Spice Level: {request.spice_level}
    - Budget: {request.budget}
    - Max Cooking Time: {request.cooking_time}
    - Number of Servings: {request.servings}
    - Available Ingredients: {request.ingredients if request.ingredients else 'None specified'}
    - Ingredients to Avoid: {request.avoid_ingredients if request.avoid_ingredients else 'None'}
    - Allergies: {request.allergies if request.allergies else 'None'}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        recipe_markdown = response.choices[0].message.content
        return {"status": "success", "data": recipe_markdown}
        
    except GroqError as e:
        raise HTTPException(status_code=502, detail=f"Groq API Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")