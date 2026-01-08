# Charles Daniel Apollo Doka
# Date: 8th Jan 2026
# Project: AI FITNESS APPLICATION

import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="AI Fitness & Diet Planner",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #e0e7ff, #fce7f3);
    }
    h1 {
        color: #764ba2;
        text-align: center;
        font-size: 3rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🏋️ AI-Powered Fitness & Diet Planner 🥗")
st.markdown("""
    <p style='text-align: center; font-size: 1.2rem; color: #555;'>
    Get personalized workout and nutrition plans powered by AI
    </p>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    hf_token = st.secrets.get("HF_TOKEN", "")

    if not hf_token:
        hf_token = st.text_input(
            "Hugging Face API Token",
            type="password",
            help="Get your token from https://huggingface.co/settings/tokens"
        )

    if hf_token:
        st.success("✅ Token configured!")
    else:
        st.warning("⚠️ Please enter your API token")

# Helper function - BMI Calculator
def calculate_bmi(weight_kg: float, height_cm: float) -> tuple[float, str]:
    height_m = height_cm / 100
    bmi: float = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25:
        bmi_category = "Normal weight"
    elif bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

    return round(bmi, 1), bmi_category


# API Function
def generate_fitness_plan(form_data, token):
    prompt = f"""You are a professional fitness and nutrition expert. Create a personalized plan:

Personal Details:
- Age: {form_data['age']} years
- Weight: {form_data['weight']} kg
- Height: {form_data['height']} cm
- Gender: {form_data['gender']}
- Fitness Goal: {form_data['fitness_goal']}
- Activity Level: {form_data['activity_level']}
- Training Days: {form_data['days_per_week']} per week

Preferences:
- Cultural Background: {form_data['cultural_background'] or 'Not specified'}
- Dietary Restrictions: {form_data['dietary_restrictions'] or 'None'}
- Available Equipment: {form_data['available_equipment'] or 'Basic'}
- Budget: {form_data['budget']}

Provide:
1. Weekly workout plan with exercises, sets, reps
2. Daily diet plan with meals and portions
3. Tips for motivation and progress"""

    api_url = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "model": "Qwen/Qwen2.5-1.5B-Instruct:hf-inference",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    try:
        r = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            data = r.json()
            return data["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error: {r.status_code} - {r.text}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Form
st.markdown("## 📝 Your Personal Information")

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age (years)", 10, 100, 25, 1)
with col2:
    weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0, 0.5)
with col3:
    height = st.number_input("Height (cm)", 100, 250, 170, 1)

col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
with col2:
    activity_level = st.selectbox(
        "Activity Level",
        ["Sedentary", "Light Activity", "Moderate Activity", "Very Active"]
    )

st.markdown("## 🎯 Goals & Preferences")

col1, col2 = st.columns(2)
with col1:
    fitness_goal = st.selectbox(
        "Fitness Goal",
        ["Weight Loss", "Muscle Gain", "Maintenance", "Endurance"]
    )
    cultural_background = st.text_input(
        "Cultural Background",
        placeholder="e.g., Indian, Asian, Mediterranean"
    )
    available_equipment = st.text_input(
        "Available Equipment",
        placeholder="e.g., Dumbbells, Gym"
    )

with col2:
    dietary_restrictions = st.text_input(
        "Dietary Restrictions",
        placeholder="e.g., Vegetarian, Vegan"
    )
    budget = st.selectbox("Food Budget", ["Budget-Friendly", "Moderate", "Premium"])

days_per_week = st.slider("Training Days per Week", 2, 6, 3, 1)

# Generate Button
st.markdown("---")
if st.button("🚀 Generate My Personalized Plan"):

    if not hf_token:
        st.error("❌ Please enter your Hugging Face API token!")
    else:
        form_data = {
            "age": age,
            "weight": weight,
            "height": height,
            "gender": gender,
            "activity_level": activity_level,
            "fitness_goal": fitness_goal,
            "cultural_background": cultural_background,
            "dietary_restrictions": dietary_restrictions,
            "available_equipment": available_equipment,
            "days_per_week": days_per_week,
            "budget": budget
        }

        with st.spinner("🤖 Generating your plan... Please wait..."):
            generated_plan = generate_fitness_plan(form_data, hf_token)

        if generated_plan:
            bmi, category = calculate_bmi(weight, height)

            st.success("✅ Your personalized plan is ready!")

            # Display BMI
            st.markdown("## 📊 Your Health Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BMI", f"{bmi}")
            with col2:
                st.metric("Category", category)
            with col3:
                st.metric("Goal", fitness_goal)

            # Display Plan
            tab1, tab2 = st.tabs(["💪 Workout Plan", "🥗 Diet Plan"])

            with tab1:
                st.markdown("### Your Personalized Workout Plan")
                st.write(generated_plan)

            with tab2:
                st.markdown("### Your Personalized Diet Plan")
                st.write(generated_plan)

            # Download
            st.download_button(
                label="📥 Download Your Plan",
                data=f"BMI: {bmi} ({category})\n\n{generated_plan}",
                file_name="fitness_plan.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
    <p><strong>AI Fitness & Diet Planner</strong></p>
    <p>Powered by Qwen2.5 | Built with Streamlit</p>
    </div>
""", unsafe_allow_html=True)
