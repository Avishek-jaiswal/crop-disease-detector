# AI Crop Disease Detector

The Streamlit interface sends uploaded leaf images to an Express REST API. The
API forwards them to a Python service that loads the existing Hugging Face
classifier once, then stores predictions and timestamps in MongoDB. Uploaded
image bytes are not retained.

## Run with Docker

Install Docker with Compose, then run:

```sh
docker compose up --build
```

The first startup downloads the model and can take several minutes. Open
<http://localhost:8501> for the Streamlit app. The API is available at
<http://localhost:3000>; MongoDB data is retained in the `mongo_data` volume.

## REST API

Create a diagnosis by sending a JPEG or PNG as multipart form field `image`:

```sh
curl -X POST http://localhost:3000/api/diagnoses \
  -F "image=@leaf.jpg"
```

The API returns the saved record, including its identifier, the top three
predictions, and creation time. Other endpoints:

- `GET /healthz` — API and database readiness
- `GET /api/diagnoses` — latest 50 diagnosis records
- `GET /api/diagnoses/:id` — retrieve one diagnosis

Uploads are limited to 10 MB. Configure `MONGODB_URI`, `INFERENCE_URL`, and
`MODEL_ID` through environment variables when running services outside Compose.
The API does not include authentication; add an appropriate access-control
layer before exposing it publicly.

## Run API tests

```sh
cd api
npm install
npm test
```
