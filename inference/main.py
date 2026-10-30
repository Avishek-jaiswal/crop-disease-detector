import io
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from transformers import pipeline


logger = logging.getLogger(__name__)
MODEL_ID = os.getenv(
    "MODEL_ID",
    "rodynaemad/plant-disease-dinov2-small"
)
MAX_FILE_SIZE = 10 * 1024 * 1024
classifier = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global classifier
    classifier = pipeline("image-classification", model=MODEL_ID)
    yield
    classifier = None


app = FastAPI(title="Crop Disease Inference", lifespan=lifespan)


@app.get("/healthz")
def health():
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model is not ready.")
    return {"status": "ok"}


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    contents = await image.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Image exceeds the 10 MB limit.")

    try:
        with Image.open(io.BytesIO(contents)) as uploaded_image:
            if uploaded_image.width * uploaded_image.height > 25_000_000:
                raise HTTPException(
                    status_code=422,
                    detail="Image dimensions exceed the supported limit."
                )
            uploaded_image.load()
            rgb_image = uploaded_image.convert("RGB")
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise HTTPException(status_code=422, detail="Uploaded file is not a valid image.") from error

    if classifier is None:
        raise HTTPException(status_code=503, detail="Model is not ready.")

    try:
        predictions = classifier(rgb_image, top_k=3)
    except Exception as error:
        logger.exception("Model inference failed")
        raise HTTPException(status_code=500, detail="Model inference failed.") from error

    return {"predictions": predictions}
