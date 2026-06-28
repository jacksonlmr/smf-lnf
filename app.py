import asyncio
import streamlit as st
import PIL.Image

from src.services.ai_service import extract_found_item_data, process_images_concurrently
from src.services.data_service import to_dataframe

st.set_page_config(
    page_title="Lost and Found",
    page_icon="📋",
    layout="centered"
)

st.title("📋Lost and Found")
st.write("Upload photos of 'Found Article Forms' to extract data concurrently using Gemini.")

uploaded_files = st.file_uploader(
    "Choose image files...",
    accept_multiple_files=True,
    type=["jpg", "jpeg", "png", "webp"]
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

        df = to_dataframe(extracted_data)

        st.success(f"Extracted {len(df)} form(s) successfully.")
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name="found_items.csv",
            mime="text/csv",
        )
