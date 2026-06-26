import asyncio
import streamlit as st
import PIL.Image

# Assuming default_client is available from your services
from src.services.ai_service import extract_found_item_data, process_images_concurrently

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Lost and Found",
    page_icon="📋",
    layout="centered"
)

st.title("📋Lost and Found")
st.write("Upload photos of 'Found Article Forms' to extract data concurrently using Gemini.")

# File upload UI
uploaded_files = st.file_uploader(
    "Choose image files...", 
    accept_multiple_files=True,
    type=["jpg", "jpeg", "png", "webp"]
)

# FIXED: Removed 'not' so it runs when files ARE uploaded
if uploaded_files:
    # Extract Data button
    if st.button("Extract Form Data", type="primary"):
        
        # Load all PIL images
        uploaded_images = [PIL.Image.open(file) for file in uploaded_files]
        
        with st.spinner(f"Gemini is analyzing {len(uploaded_images)} forms concurrently..."):

            # Call the async AI service using asyncio.run()
            extracted_data = asyncio.run(
                process_images_concurrently(
                    processing_func=extract_found_item_data, 
                    images=uploaded_images, 
                    max_concurrent=200
                )
            )
            
            st.success("Data successfully extracted!")
            st.subheader("Extracted Details")
            
            # Loop through the list of results
            for i, item in enumerate(extracted_data):
                # Use an expander for each file to keep the UI clean
                with st.expander(f"Result for: {uploaded_files[i].name}", expanded=True):
                    
                    if item is None:
                        st.error("Failed to extract data for this image.")
                        continue
                    
                    # Preview how individual properties look
                    col1, col2 = st.columns(2)
                    with col1:
                        # Append unique keys using the loop index 'i' to prevent Streamlit DuplicateWidgetID errors
                        st.text_input("Item #", value=item.item_number, disabled=True, key=f"item_num_{i}")
                        st.text_input("Category", value=item.category, disabled=True, key=f"cat_{i}")
                        st.text_input("Location Found", value=item.location_found, disabled=True, key=f"loc_{i}")
                    with col2:
                        st.text_area("Description", value=item.description, disabled=True, key=f"desc_{i}")
                        st.checkbox("Matched with Lost Item", value=item.matched_with_lost_item, disabled=True, key=f"matched_{i}")
                        st.checkbox("Returned to Owner", value=item.returned_to_owner, disabled=True, key=f"returned_{i}")