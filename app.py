import io
import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state for nutritional goals
if 'nutritional_goals' not in st.session_state:
    st.session_state.nutritional_goals = {"calories": 2000, "proteins": 50, "fats": 70, "carbs": 300}

def get_flash_response(input_prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')  # Use flash model for text input
    response = model.generate_content(input_prompt)
    return response.text

def get_flash_response(input_prompt, image=None):
    model = genai.GenerativeModel('gemini-2.5-flash')  # Use pro model for image input
    response = model.generate_content([input_prompt] + ([image[0]] if image else []))
    return response.text

def get_gemini_response(input_prompt, image=None):
    if image:
        return get_flash_response(input_prompt, image)
    else:
        return get_flash_response(input_prompt)

def get_recipe_suggestions(ingredients):
    prompt = (
        f"Given the following ingredients: {', '.join(ingredients)}, "
        f"how many types of recipes can be made? Provide their names, "
        f"the amounts of each ingredient needed for each recipe, "
        f"and a concise cooking process for each recipe."
    )
    response = get_flash_response(prompt)
    return response

def input_image_setup(uploaded_file, mime_type):
    bytes_data = uploaded_file.getvalue() if uploaded_file else None
    return [{"mime_type": mime_type, "data": bytes_data}]

def convert_image_to_jpeg(png_image):
    image = Image.open(io.BytesIO(png_image))
    rgb_image = image.convert("RGB")
    jpeg_output = io.BytesIO()
    rgb_image.save(jpeg_output, format='JPEG')
    jpeg_output.seek(0)
    return jpeg_output.getvalue()

def safe_float_conversion(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def show_nutritional_goals():
    goals = st.session_state.nutritional_goals
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Daily Calorie Goal", value=goals["calories"])
    with col2:
        st.metric(label="Daily Protein Goal (g)", value=goals["proteins"])
    
    col3, col4 = st.columns(2)
    with col3:
        st.metric(label="Daily Fat Goal (g)", value=goals["fats"])
    with col4:
        st.metric(label="Daily Carb Goal (g)", value=goals["carbs"])

    st.subheader("Set your Nutritional Goals")
    
    # Get user input for goals
    calories = st.number_input("Calories", value=goals["calories"], min_value=0, step=100)
    proteins = st.number_input("Proteins", value=goals["proteins"], min_value=0, step=5)
    fats = st.number_input("Fats", value=goals["fats"], min_value=0, step=5)
    carbs = st.number_input("Carbohydrates", value=goals["carbs"], min_value=0, step=5)

    if st.button("Update Goals"):
        st.session_state.nutritional_goals = {
            "calories": calories,
            "proteins": proteins,
            "fats": fats,
            "carbs": carbs
        }
        st.success("Nutritional goals updated!")

def get_nutritional_info(food_item):
    prompt = (
        f"Provide the nutritional information for the following food item in the format: "
        f"Food Item | Calories | Carbohydrates | Fats | Proteins:\n{food_item}"
    )
    response = get_flash_response(prompt)  # Use flash model for nutritional information
    return response

# Streamlit App
st.set_page_config(page_title="Nutritional Analysis and Recipe Suggestions", page_icon="🥗")
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a Page", ["Nutritional Analysis", "Recipe Suggestions", "Nutritional Goals", "Nutritional Database"])

# Custom Styles with Background Image
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            rgba(50, 50, 50, 0.8), 
            rgba(50, 50, 50, 0.8)
        ), 
        url("https://images.pexels.com/photos/1092730/pexels-photo-1092730.jpeg") no-repeat center center fixed;
        background-size: cover;
        min-height: 100vh;
        width: 100vw;
        overflow: hidden;
        position: relative;
    }

    body {
        font-family: 'Arial', sans-serif;
        color: white;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
    }

    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
    }

    p, li {
        color: white !important;
        font-size: 16px;
        line-height: 1.5;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
    }

    table td {
        color: black !important;
        font-weight: bold;
        padding: 10px;
        border: 1px solid #ccc;
        text-align: left;
        background-color: rgba(255, 255, 255, 0.95);
    }

    ul li::marker, ol li::marker {
        color: #00f;
    }

    span {
        color: #00f !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }

    .stNumberInput input, .stTextInput input {
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        background-color: rgba(255, 255, 255, 0.9);
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        outline: none;
        border-color: #66b3ff;
    }

    footer {
        background-color: rgba(76, 175, 80, 0.9);
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-top: 20px;
    }

    footer a {
        color: white;
        text-decoration: underline;
    }

    @media only screen and (max-width: 768px) {
        body {
            font-size: 14px;
        }

        .stButton>button {
            padding: 8px 16px;
        }
    }

    @media only screen and (min-width: 768px) {
        body {
            font-size: 16px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

if page == "Nutritional Analysis":
    st.header("Nutritional Analysis of Uploaded Image")
    uploaded_files = st.file_uploader("Choose images of food items...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    images = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.getvalue()
            mime_type = uploaded_file.type
            
            if mime_type == "image/png":
                bytes_data = convert_image_to_jpeg(bytes_data)
                mime_type = "image/jpeg"

            image = Image.open(io.BytesIO(bytes_data))

            # Image enhancement options
            st.sidebar.header("Enhance Images")
            brightness = st.sidebar.slider("Brightness", 0.5, 3.0, 1.0)
            contrast = st.sidebar.slider("Contrast", 0.5, 3.0, 1.0)
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)

            images.append((image, mime_type))
            st.image(image, caption="Uploaded Image")

    if st.button("Analyze Nutritional Content"):
        if images:
            input_prompt = """You are an expert in nutrition. Please analyze the uploaded images 
            and provide the nutritional information for the food items in a table format:
            Food Item | Calories | Carbohydrates | Fats | Proteins
            """
            nutritional_response = ""
            data = []
            with st.spinner('Processing images...'):
                for image, mime_type in images:
                    buffer = io.BytesIO()
                    image.save(buffer, format="JPEG")
                    buffer.seek(0)
                    image_data = input_image_setup(uploaded_file=buffer, mime_type=mime_type)
                    response = get_gemini_response(input_prompt, image_data)

                    foods = []
                    for line in response.splitlines():
                        parts = line.split('|')
                        if len(parts) >= 5:
                            foods.append({
                                "food_item": parts[0].strip(),
                                "calories": parts[1].strip(),
                                "carbohydrates": parts[2].strip(),
                                "fats": parts[3].strip(),
                                "proteins": parts[4].strip(),
                            })

                    data.extend(foods)
                    nutritional_response = response
                    st.header("Nutritional Analysis Response")
                    st.markdown(nutritional_response, unsafe_allow_html=True)

                if data:
                    # Visualization of nutritional data can be added here
                    nutritional_data = {item['food_item']: [safe_float_conversion(item['calories']),
                                                            safe_float_conversion(item['carbohydrates']),
                                                            safe_float_conversion(item['fats']),
                                                            safe_float_conversion(item['proteins'])] 
                                        for item in data}

                    # Plotting the nutritional values for a selected food item
                    selected_food = st.selectbox("Select food item for detailed analysis:", list(nutritional_data.keys()))
                    if selected_food:
                        values = nutritional_data[selected_food]
                        labels = ['Calories', 'Carbs', 'Fats', 'Proteins']
                        fig, ax = plt.subplots()
                        ax.bar(labels, values, color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
                        ax.set_title(f'Nutritional Values for {selected_food}')
                        # Adjusted y-axis limit handling
                        if all(value == 0 for value in values):
                            ax.set_ylim(0, 1)  # Set a minimal range if all values are zero
                        else:
                            ax.set_ylim(0, max(values) * 1.2)  # Ensure space above the highest bar
                        st.pyplot(fig)
                else:
                    st.warning("No valid nutritional data found for the uploaded images.")
        else:
            st.error("Please upload at least one image before analyzing.")

elif page == "Recipe Suggestions":
    st.header("Get Recipe Suggestions from Ingredient Image")
    ingredient_image = st.file_uploader("Upload an image of ingredients...", type=["jpg", "jpeg", "png"])

    if st.button("Get Recipe Suggestions from Image") and ingredient_image:
        buffer = io.BytesIO()
        image = Image.open(ingredient_image)
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        
        image_input = input_image_setup(uploaded_file=buffer, mime_type="image/jpeg")
        prompt_for_ingr = ("Analyze the uploaded image and extract the food items present. "
                           "List the food items in a clear format for the recipes.")

        with st.spinner('Processing ingredient image...'):
            ingredients_response = get_gemini_response(prompt_for_ingr, image_input)
            
            # Extract the food items from the response
            ingredients = [ingredient.strip() for ingredient in ingredients_response.split(',') if ingredient.strip()]
            
            st.subheader("Extracted Ingredients:")
            if ingredients:
                st.markdown(", ".join(ingredients))
                
                # Get recipes based on the detected ingredients
                recipe_suggestions_from_image = get_recipe_suggestions(ingredients)
                
                st.subheader("Recipe Suggestions based on Uploaded Image:")
                st.markdown(recipe_suggestions_from_image, unsafe_allow_html=True)

            else:
                st.warning("No ingredients detected. Please try uploading a clearer image or different ingredients.")
    
    st.header("Get Recipe Suggestions from Manually Entered Ingredients")
    ingredient_input = st.text_input("Enter ingredient names (comma-separated):")
    
    if st.button("Get Recipe Suggestions") and ingredient_input:
        ingredients = [ingredient.strip() for ingredient in ingredient_input.split(',') if ingredient.strip()]
        if ingredients:
            with st.spinner('Fetching recipe suggestions...'):
                recipe_suggestions = get_recipe_suggestions(ingredients)
                st.subheader("Recipe Suggestions:")
                st.markdown(recipe_suggestions, unsafe_allow_html=True)

        else:
            st.error("Please enter at least one valid ingredient.")

elif page == "Nutritional Goals":
    st.header("Set Your Nutritional Goals")
    show_nutritional_goals()

elif page == "Nutritional Database":
    st.header("Nutritional Database Lookup")
    food_item = st.text_input("Enter a food item:")
    
    if st.button("Lookup Nutritional Info"):
        if food_item:
            nutrition_info = get_nutritional_info(food_item)
            st.subheader(f"Nutritional Info for {food_item.capitalize()}:")
            st.markdown(nutrition_info, unsafe_allow_html=True)
        else:
            st.warning("Please enter a food item.")

else:
    st.title("Welcome to NutriApp")