import streamlit as st
import openai as openai
import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

st.title("Summarize my text")

# Pobierz API key z zmiennej środowiskowej
api_key = os.getenv("AZURE_OPENAI_API_KEY")

if not api_key:
    st.error("❌ Brak API key! Skontaktuj się z administratorem aplikacji.")
    st.stop()

form_values = {
    "name": None,
    "type_of_summary": None,
    "text": None,
}

def generate_summary(text, summary_type):
    try:
        # Azure OpenAI configuration
        client = openai.AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-01",
            azure_endpoint="https://summerizetext.openai.azure.com/"
        )
        
        prompts = {
            "understandable for 5 year old": f"summarize the text for 5 years old: {text}",
            "understandable for high school student": f"summarize the text for high school student: {text}",
            "understandable for university student": f"summarize the text for university students: {text}",
            "understandable for specialist": f"summarize the text for specialist: {text}"
        }
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # TWOJE DEPLOYMENT NAME
            messages=[{"role": "user", "content": prompts[summary_type]}],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Inicjalizacja session state
if "step" not in st.session_state:
    st.session_state.step = 1 

if "info" not in st.session_state:
    st.session_state.info = {}

def go_to_next_step(form_values):
    st.session_state.info["name"] = form_values["name"]
    st.session_state.info["type_of_summary"] = form_values["type_of_summary"]
    st.session_state.info["text"] = form_values["text"]
    st.session_state.step = 2

def go_to_previous_step():
    st.session_state.step = 1

# Główna logika aplikacji
if st.session_state.step == 1:
    st.header("Please fill all the information below")
    with st.form(key='all_info'):
        form_values["name"] = st.text_input("Enter your name: ")
        form_values["type_of_summary"] = st.selectbox("Select type of summary: ", 
            ["understandable for 5 year old", "understandable for high school student", 
             "understandable for university student", "understandable for specialist"])
        form_values["text"] = st.text_area("Enter your text: ")
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if not all(form_values.values()):
                st.error("Please fill in ALL fields")
            else:
                go_to_next_step(form_values)
                st.success("Thank you for submitting your information!")
                st.rerun()

elif st.session_state.step == 2:
    st.header("Your information: ")
    st.write(f"**Name**: {st.session_state.info.get('name', '')}")
    st.write(f"**Type of summary**: {st.session_state.info.get('type_of_summary', '')}")
    st.write(f"**Text**: {st.session_state.info.get('text', '')}")

    if st.button("Generate Summary"):
        st.success(f"Thank you {st.session_state.info.get('name', '')} for submitting your text!")
        with st.spinner("Generating summary..."):
            summary = generate_summary(
                st.session_state.info["text"],
                st.session_state.info["type_of_summary"]
            )
            st.subheader("AI Summary:")
            st.write(summary)
        st.session_state.info = {}  # Clear the info after submission
        st.session_state.step = 1   # Reset to step 1
    
    if st.button("Back", on_click=go_to_previous_step):
        pass