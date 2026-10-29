
import streamlit as st
from PIL import Image
from transformers import pipeline

st.set_page_config(
    page_title="AI Crop Disease Detector",
    page_icon="🌱",
    layout="centered"
)

@st.cache_resource
def load_model():
    return pipeline(
        "image-classification",
        model="rodynaemad/plant-disease-dinov2-small"
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
    image = Image.open(uploaded_file).convert("RGB")

    st.image(
        image,
        caption="Uploaded plant image",
        use_container_width=True
    )

    if st.button("🔍 Detect Crop Disease", type="primary"):
        try:
            with st.spinner("AI is analyzing the image..."):
                classifier = load_model()
                results = classifier(image, top_k=3)

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

        except Exception as error:
            st.error(
                "Could not analyze the image. "
                "Check your internet connection and "
                "terminal error, then try again."
            )
            st.exception(error)
