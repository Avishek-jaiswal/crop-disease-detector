
import os

import streamlit as st
import requests


API_URL = os.getenv("API_URL", "http://localhost:3000/api/diagnoses")

st.set_page_config(
    page_title="AI Crop Disease Detector",
    page_icon="🌱",
    layout="centered"
)

st.title("🌱 AI Crop Disease Detector")

st.write(
    "Upload a plant leaf image to identify a possible "
    "crop condition using artificial intelligence."
)

st.info(
    "This prototype uses an image-classification model "
    "trained on 38 crop-condition classes."
)

uploaded_file = st.file_uploader(
    "Upload a leaf photograph",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="Uploaded plant image",
        use_container_width=True
    )

    if st.button("🔍 Detect Crop Disease", type="primary"):
        try:
            with st.spinner("AI is analyzing the image..."):
                response = requests.post(
                    API_URL,
                    files={
                        "image": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    },
                    timeout=120
                )
                response.raise_for_status()
                diagnosis = response.json()
                results = diagnosis["predictions"]

            st.subheader("Analysis Results")

            best_result = results[0]
            label = best_result["label"]
            confidence = best_result["score"]

            readable_label = (
                label.replace("___", " — ")
                     .replace("_", " ")
            )

            st.write("**Top prediction:**", readable_label)
            st.metric(
                "Model confidence score",
                f"{confidence:.1%}"
            )

            st.write("**Other possible predictions**")

            for result in results:
                name = (
                    result["label"]
                    .replace("___", " — ")
                    .replace("_", " ")
                )

                st.write(
                    f"- {name}: {result['score']:.1%}"
                )

            st.warning(
                "This is an AI prediction, not a confirmed "
                "agricultural diagnosis. The model may be "
                "wrong, especially on field photographs. "
                "Consult an agricultural expert before "
                "choosing a treatment."
            )

        except (requests.RequestException, KeyError, ValueError) as error:
            st.error(
                "Could not analyze the image. "
                "Check that the backend is running and "
                "try again."
            )
            st.exception(error)
