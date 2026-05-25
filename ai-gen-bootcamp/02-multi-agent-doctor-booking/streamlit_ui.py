import streamlit as st
import requests

API_URL = "http://127.0.0.1:8005/execute"

st.title("🩺 Doctor Appointment System")

user_id = st.text_input("Enter your ID number:", "")
query = st.text_area("Enter your query:", "Can you check if a dentist is available tomorrow at 10 AM?")

if st.button("Submit Query"):
    if user_id and query:
        try:
            user_id_int = int(user_id)
            response = requests.post(API_URL, json={'messages': query, 'id_number': user_id_int}, verify=True)
            if response.status_code == 200:
                st.success("Response Received:")
                print("**********my response******************")
                print(response.status_code)
                print(response.json())
                st.write(response.json()["messages"])
            else:
                st.error(f"Error {response.status_code}: Could not process the request.")
        except ValueError:
            st.error("Invalid ID number. Please enter a valid integer.")
        except Exception as e:
            st.error(f"Exception occurred: {e}")
    else:
        st.warning("Please enter both ID and query.")






# python3.13 -m venv .venv

# source .venv/bin/activate


# pip3.13 install uvicorn click





# uvicorn main:app --reload --port 8003

# streamlit run streamlit_ui.py



