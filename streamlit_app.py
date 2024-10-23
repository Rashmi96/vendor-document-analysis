import streamlit as st
import requests

# Streamlit App
st.title("Vendor Document Analysis")

# Health Check Route
st.subheader("Health Check")
if st.button("Ping Server"):
    try:
        response = requests.get("http://localhost:5002/ping")
        if response.status_code == 200:
            st.success("Server is healthy")
            st.json(response.json())
        else:
            st.error("Failed to ping the server")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Ask a Question Route
st.subheader("Ask a Question")
question = st.text_input("Enter your question:")
if st.button("Ask Question"):
    if question:
        try:
            response = requests.post("http://localhost:5002/ask/", json={"question": question})
            if response.status_code == 200:
                st.success("Answer retrieved")
                st.json(response.json())
            else:
                st.error("Failed to get answer")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# File Upload Route
st.subheader("Upload Document")
uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
if uploaded_files and st.button("Upload"):
    files = [('files', (file.name, file, file.type)) for file in uploaded_files]
    try:
        response = requests.post("http://localhost:5002/uploadDocument", files=files)
        if response.status_code == 200:
            st.success("File uploaded successfully")
            st.json(response.json())
        else:
            st.error("Failed to upload file")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# List Files Route
st.subheader("List Files")
dir_path = st.selectbox("Choose directory:", ["uploads", "downloads"])
if st.button("List Files"):
    try:
        response = requests.get(f"http://localhost:5002/list-files?dir_path={dir_path}")
        if response.status_code == 200:
            st.success("Files retrieved")
            st.json(response.json())
        else:
            st.error("Failed to retrieve files")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Download Report Route
st.subheader("Download Report")
filename = st.text_input("Enter the filename to download:")
if filename and st.button("Download Report"):
    try:
        response = requests.get(f"http://localhost:5002/reportDownload/{filename}", stream=True)
        if response.status_code == 200:
            st.success(f"Report {filename} downloaded successfully")
            st.download_button("Download", response.content, filename)
        else:
            st.error("Failed to download report")
    except Exception as e:
        st.error(f"Error: {str(e)}")
