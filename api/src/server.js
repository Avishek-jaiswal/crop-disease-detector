import mongoose from "mongoose";
import app from "./app.js";

const port = Number(process.env.PORT ?? 3000);
const mongoUri =
  process.env.MONGODB_URI ?? "mongodb://localhost:27017/crop_disease";

try {
  await mongoose.connect(mongoUri);
  app.listen(port, "0.0.0.0", () => {
    console.log(`Crop disease API listening on port ${port}`);
  });
} catch (error) {
  console.error("Could not connect to MongoDB:", error);
  process.exitCode = 1;
}
