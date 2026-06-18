import streamlit as st
import PIL.Image

from src.services.ai_service import extract_found_item_data

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Lost and Found",
    page_icon="📋",
    layout="centered"
)

st.title("📋Lost and Found")
st.write("Upload a photo of a 'Found Article Form' to extract data using Gemini.")

# File upload UI
uploaded_file = st.file_uploader(
    "Choose an image file...", 
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
    # Display the uploaded image to the user
    image = PIL.Image.open(uploaded_file)
    st.image(image, caption="Uploaded Form", width='stretch')
    
    # Extract Data button
    if st.button("Extract Form Data", type="primary"):
        with st.spinner("Gemini is analyzing the form..."):

            # Call the AI service
            extracted_data = extract_found_item_data(image)
            
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