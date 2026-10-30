import assert from "node:assert/strict";
import { once } from "node:events";
import { createServer } from "node:http";
import test, { after, before } from "node:test";
import app from "../src/app.js";

const server = createServer(app);
let baseUrl;

before(async () => {
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(() => {
  server.close();
});

test("diagnosis endpoint requires an image", async () => {
  const response = await fetch(`${baseUrl}/api/diagnoses`, {
    method: "POST"
  });

  assert.equal(response.status, 400);
  assert.deepEqual(await response.json(), {
    error: "An image file is required in the 'image' field."
  });
});

test("diagnosis endpoint rejects unsupported file types", async () => {
  const form = new FormData();
  form.append(
    "image",
    new Blob(["not an image"], { type: "text/plain" }),
    "notes.txt"
  );
  const response = await fetch(`${baseUrl}/api/diagnoses`, {
    method: "POST",
    body: form
  });

  assert.equal(response.status, 415);
  assert.deepEqual(await response.json(), {
    error: "Only JPEG and PNG images are supported."
  });
});

test("diagnosis lookup rejects malformed IDs", async () => {
  const response = await fetch(`${baseUrl}/api/diagnoses/not-an-id`);

  assert.equal(response.status, 400);
  assert.deepEqual(await response.json(), {
    error: "Invalid diagnosis ID."
  });
});
