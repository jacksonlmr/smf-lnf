import streamlit as st
import PIL.Image
import tempfile
import os
from src.services.ai_service import extract_found_item_data

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Found Item Logger",
    page_icon="📋",
    layout="centered"
)

st.title("📋 Found Item Logger")
st.write("Upload a photo of a 'Found Article Form' to extract data using Gemini.")

# ==========================================
# FILE UPLOAD INTERFACE
# ==========================================
uploaded_file = st.file_uploader(
    "Choose an image file...", 
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
    # Display the uploaded image to the user
    image = PIL.Image.open(uploaded_file)
    st.image(image, caption="Uploaded Form", use_container_width=True)
    
    # Process button
    if st.button("Extract Form Data", type="primary"):
        with st.spinner("Gemini is analyzing the form..."):
            
            # Since our service currently expects a file path, we write the 
            # uploaded bytes to a temporary file on disk.
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name

            try:
                # Call the AI service
                extracted_data = extract_found_item_data(temp_file_path)
                
                if extracted_data:
                    st.success("Data successfully extracted!")
                    st.subheader("Extracted Details")
                    
                    # Present the data in a clean key-value format using Streamlit metrics or dataframes
                    st.json(extracted_data.model_dump())
                    
                    # Preview how individual properties look
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("Item #", value=extracted_data.item_number, disabled=True)
                        st.text_input("Category", value=extracted_data.category, disabled=True)
                        st.text_input("Location Found", value=extracted_data.location_found, disabled=True)
                    with col2:
                        st.text_area("Description", value=extracted_data.description, disabled=True)
                        st.checkbox("Matched with Lost Item", value=extracted_data.matched_with_lost_item, disabled=True)
                        st.checkbox("Returned to Owner", value=extracted_data.returned_to_owner, disabled=True)
                else:
                    st.error("Failed to extract data. Check the terminal for details.")
                    
            finally:
                # Clean up the temporary file from the disk after execution
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)