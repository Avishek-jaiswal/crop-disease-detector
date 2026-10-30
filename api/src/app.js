import express from "express";
import multer from "multer";
import mongoose from "mongoose";
import Diagnosis from "./diagnosis.js";

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const INFERENCE_URL =
  process.env.INFERENCE_URL ?? "http://localhost:8000";

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: MAX_FILE_SIZE, files: 1 },
  fileFilter: (_request, file, callback) => {
    if (!["image/jpeg", "image/png"].includes(file.mimetype)) {
      callback(new Error("Only JPEG and PNG images are supported."));
      return;
    }

    callback(null, true);
  }
});

const app = express();

app.get("/healthz", (_request, response) => {
  const databaseReady = mongoose.connection.readyState === 1;
  response.status(databaseReady ? 200 : 503).json({
    status: databaseReady ? "ok" : "not_ready",
    database: databaseReady ? "connected" : "disconnected"
  });
});

app.post("/api/diagnoses", upload.single("image"), async (request, response, next) => {
  if (!request.file) {
    response.status(400).json({ error: "An image file is required in the 'image' field." });
    return;
  }

  try {
    const form = new FormData();
    form.append(
      "image",
      new Blob([request.file.buffer], { type: request.file.mimetype }),
      request.file.originalname
    );

    let inferenceResponse;
    try {
      inferenceResponse = await fetch(`${INFERENCE_URL}/predict`, {
        method: "POST",
        body: form,
        signal: AbortSignal.timeout(120_000)
      });
    } catch (error) {
      if (error.name === "TimeoutError") {
        response.status(504).json({ error: "AI inference timed out." });
        return;
      }

      response.status(503).json({ error: "AI inference service is unavailable." });
      return;
    }

    if (!inferenceResponse.ok) {
      if (inferenceResponse.status === 422) {
        response.status(422).json({ error: "The uploaded file is not a valid image." });
        return;
      }

      response.status(502).json({ error: "AI inference failed." });
      return;
    }

    const result = await inferenceResponse.json();
    if (!Array.isArray(result.predictions) || result.predictions.length === 0) {
      response.status(502).json({ error: "AI inference returned no predictions." });
      return;
    }

    const diagnosis = await Diagnosis.create({
      filename: request.file.originalname,
      predictions: result.predictions
    });

    response.status(201).json({
      id: diagnosis.id,
      filename: diagnosis.filename,
      predictions: diagnosis.predictions,
      createdAt: diagnosis.createdAt
    });
  } catch (error) {
    next(error);
  }
});

app.get("/api/diagnoses", async (_request, response, next) => {
  try {
    const diagnoses = await Diagnosis.find()
      .sort({ createdAt: -1 })
      .limit(50)
      .lean();
    response.json(diagnoses);
  } catch (error) {
    next(error);
  }
});

app.get("/api/diagnoses/:id", async (request, response, next) => {
  if (!mongoose.isValidObjectId(request.params.id)) {
    response.status(400).json({ error: "Invalid diagnosis ID." });
    return;
  }

  try {
    const diagnosis = await Diagnosis.findById(request.params.id).lean();
    if (!diagnosis) {
      response.status(404).json({ error: "Diagnosis not found." });
      return;
    }

    response.json(diagnosis);
  } catch (error) {
    next(error);
  }
});

app.use((error, _request, response, _next) => {
  if (error instanceof multer.MulterError) {
    const status = error.code === "LIMIT_FILE_SIZE" ? 413 : 400;
    response.status(status).json({ error: error.message });
    return;
  }

  if (error.message === "Only JPEG and PNG images are supported.") {
    response.status(415).json({ error: error.message });
    return;
  }

  console.error(error);
  response.status(500).json({ error: "Internal server error." });
});

export default app;
