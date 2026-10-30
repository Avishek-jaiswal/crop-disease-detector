import mongoose from "mongoose";

const predictionSchema = new mongoose.Schema(
  {
    label: { type: String, required: true },
    score: { type: Number, required: true }
  },
  { _id: false }
);

const diagnosisSchema = new mongoose.Schema(
  {
    filename: { type: String, required: true },
    predictions: { type: [predictionSchema], required: true }
  },
  { timestamps: true }
);

export default mongoose.model("Diagnosis", diagnosisSchema);
