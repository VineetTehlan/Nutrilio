import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_recipe(food_item):
    """
    Scrapes a recipe for the given food item and returns ingredients in JSON format.
    
    Args:
        food_item (str): The name of the food item to search for
        
    Returns:
        list: JSON array of ingredients with amounts in grams/ml
    """
    
    # Search for recipe on AllRecipes
    search_url = f"https://www.allrecipes.com/search?q={food_item}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # Search for the recipe
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the first recipe link
        recipe_link = soup.find('a', {'data-recipe-id': True})
        
        if not recipe_link:
            print(f"No recipes found for '{food_item}'")
            return []
        
        recipe_url = recipe_link.get('href')
        if not recipe_url.startswith('http'):
            recipe_url = 'https://www.allrecipes.com' + recipe_url
        
        print(f"Found recipe: {recipe_url}")
        
        # Fetch the recipe page
        recipe_response = requests.get(recipe_url, headers=headers, timeout=10)
        recipe_response.raise_for_status()
        
        recipe_soup = BeautifulSoup(recipe_response.content, 'html.parser')
        
        ingredients = []
        
        # Find ingredient list
        ingredient_elements = recipe_soup.find_all('li', class_='ingredients__item')
        
        if not ingredient_elements:
            ingredient_elements = recipe_soup.find_all('span', class_='ingredient')
        
        for element in ingredient_elements:
            text = element.get_text(strip=True)
            ingredient_data = parse_ingredient(text)
            if ingredient_data:
                ingredients.append(ingredient_data)
        
        return ingredients
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

def parse_ingredient(ingredient_text):
    """
    Parses ingredient text to extract name and amount in grams/ml.
    
    Args:
        ingredient_text (str): Raw ingredient text
        
    Returns:
        dict: Dictionary with 'item' and 'amnt' keys
    """
    
    # Remove extra whitespace
    ingredient_text = ingredient_text.strip()
    
    # Common unit conversions to grams/ml
    conversions = {
        'cup': 240,
        'cups': 240,
        'tbsp': 15,
        'tablespoon': 15,
        'tsp': 5,
        'teaspoon': 5,
        'ml': 1,
        'gram': 1,
        'g': 1,
        'oz': 28.35,
        'ounce': 28.35,
        'lb': 453.6,
        'pound': 453.6,
    }
    
    # Extract amount and unit
    amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to\s+\d+(?:\.\d+)?)?\s*([a-zA-Z]+)', ingredient_text)
    
    if amount_match:
        amount_str = amount_match.group(1)
        unit = amount_match.group(2).lower()
        
        amount = float(amount_str)
        
        # Convert to grams/ml
        if unit in conversions:
            amount = amount * conversions[unit]
        
        amount = round(amount, 2)
        
        # Extract ingredient name (remove amount and unit from text)
        name = re.sub(r'\d+(?:\.\d+)?\s*(?:to\s+\d+(?:\.\d+)?)?\s*[a-zA-Z]+\s*', '', ingredient_text).strip()
        
        return {"item": name, "amnt": amount}
    
    return None

def main():
    food_item = input("Enter the food item you want to scrape a recipe for: ")
    
    print(f"\nScraping recipe for '{food_item}'...")
    ingredients = scrape_recipe(food_item)
    
    if ingredients:
        json_output = json.dumps(ingredients, indent=2)
        print("\nRecipe Ingredients (JSON):")
        print(json_output)
    else:
        print("No ingredients found.")

if __name__ == "__main__":
    main()