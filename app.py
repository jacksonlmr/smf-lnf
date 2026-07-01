import asyncio
import streamlit as st
from PIL.ImageFile import ImageFile
import PIL.Image
from typing import List, cast

from src.services.ai_service import extract_found_item_data, process_images_concurrently
from src.services.data_service import to_dataframe, generate_img_zip
from src.models.llm_schemas import FoundItem

st.set_page_config(
    page_title="Lost and Found",
    page_icon="📋",
    layout="centered"
)

# --- Initialize Session State Variables ---
if "processed" not in st.session_state:
    st.session_state.processed = False
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "csv_data" not in st.session_state:
    st.session_state.csv_data = None
if "zip_data" not in st.session_state:
    st.session_state.zip_data = None
if "success_message" not in st.session_state:
    st.session_state.success_message = ""

st.title("📋Lost and Found")
st.write("Upload photos of 'Found Article Forms' to extract data concurrently using Gemini.")

# Use the dynamic key from session state to allow clearing
uploaded_files = st.file_uploader(
    "Choose image files...",
    accept_multiple_files=True,
    type=["jpg", "jpeg", "png", "webp"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    if st.button("Extract Form Data", type="primary"):

        uploaded_images = [PIL.Image.open(file) for file in uploaded_files]

        with st.spinner(f"Gemini is analyzing {len(uploaded_images)} forms concurrently..."):
            extracted_data = asyncio.run(
                process_images_concurrently(
                    processing_func=extract_found_item_data,
                    images=uploaded_images
                )
            )

        results = cast(List[FoundItem | None], extracted_data["results"])
        invalid_images = cast(List[ImageFile], extracted_data["invalid_images"])
        df = to_dataframe(results)
        zip_file = generate_img_zip(invalid_images)

        # Save the results to session state instead of displaying them directly
        st.session_state.csv_data = df.to_csv(index=False)
        st.session_state.zip_data = zip_file
        st.session_state.success_message = f"Extracted {len(df)} form(s) successfully."
        st.session_state.processed = True

# --- Render Results and Buttons outside the Extract block ---
if st.session_state.processed:
    st.success(st.session_state.success_message)
    
    st.download_button(
        label="Download CSV",
        data=st.session_state.csv_data,
        file_name="found_items.csv",
        mime="text/csv",
    )
    
    st.download_button(
        label="Download Invalid Images",
        data=st.session_state.zip_data,
        file_name="invalid_images.zip",
        mime="application/zip"
    )
    
    st.divider() # Adds a clean visual break before the clear button
    
    # --- Clear Button Logic ---
    if st.button("Clear"):
        # Reset the data states
        st.session_state.processed = False
        st.session_state.csv_data = None
        st.session_state.zip_data = None
        
        # Increment the uploader key to wipe the uploaded files from the UI
        st.session_state.uploader_key += 1
        
        # Force a rerun to immediately refresh the page
        st.rerun()