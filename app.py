import streamlit as st

st.set_page_config(
    page_title="Scholarship Verification System",
    page_icon="🎓"
)

st.title("🎓 Scholarship Verification System")

st.write(
    "Upload scholarship documents for verification."
)

uploaded_file = st.file_uploader(
    "Upload Document",
    type=["jpg", "jpeg", "png", "pdf"]
)

if uploaded_file:
    st.success("Document Uploaded Successfully!")
    st.write("Filename:", uploaded_file.name)