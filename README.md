# AgriVision AI Backend

FastAPI + SQLite backend for crop inspections, transparent visual indicators, irrigation assessment, zone risk prioritization, farm history, intervention estimates, scouting routes and a multilingual assistant integration.

## Important model status

The repository does **not** contain trained tomato disease weights. The disease model adapter therefore returns `Unavailable` and `confidence: null`; it never fabricates a disease prediction. Replace `services/disease_detection.py` with a model-specific adapter and set `DISEASE_MODEL_PATH` only after obtaining compatible trained weights and documenting the class mapping. The RGB colour analysis is a heuristic, not NDVI or a diagnosis. True NDVI requires red and near-infrared bands.

## Setup (Windows PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs`. SQLite tables are created automatically on startup. For another terminal use `cd backend` first. On macOS/Linux activate with `source .venv/bin/activate`.

## Environment

- `DATABASE_URL`: SQLAlchemy URL (default SQLite file in backend folder)
- `UPLOAD_DIR`: uploaded image directory
- `MAX_UPLOAD_MB`: upload limit
- `ALLOWED_ORIGINS`: comma-separated React origins; configure exact deployed origins
- `GEMINI_API_KEY`, `GEMINI_MODEL`: optional Gemini assistant
- `DISEASE_MODEL_PATH`: optional path for a future model adapter
- `WEATHER_API_KEY`: reserved for future weather provider integration

## API overview

All endpoints are prefixed with `/api`.

- `GET /health`
- Farms: `POST/GET /farms`, `GET/PUT /farms/{farm_id}`
- Zones: `POST/GET /zones`, `GET/PUT /zones/{zone_id}`; `GET /zones?farm_id=1`
- Analysis: `POST /analysis/analyze` (multipart: `zone_id`, optional `symptoms`, `notes`, and `image`), `GET /analysis/{inspection_id}`, `GET /analysis/history/{zone_id}`
- Crop doctor: `POST /doctor/second-opinion`, `GET /doctor/{inspection_id}`
- Irrigation: `POST /irrigation/analyze`, `GET /irrigation/zone/{zone_id}`, `GET /irrigation/farm/{farm_id}`
- Risk: `GET /risk/farm/{farm_id}`, `GET /risk/zone/{zone_id}`, `GET /risk/map/{farm_id}`
- Progression: `GET /progression/{zone_id}`, `GET /progression/farm/{farm_id}`
- Simulation: `POST /simulation/compare`
- Scouting: `POST /scouting/optimize`
- Assistant: `POST /assistant/chat`, `GET /assistant/history/{session_id}`
- Analytics: `GET /analytics/farm/{farm_id}`
- Reports: `GET /reports/farm/{farm_id}`

## Quick demo flow

1. `POST /api/farms`: `{"name":"Demo Farm","rows":2,"columns":2,"area_ha":1.0}`
2. `POST /api/zones`: `{"farm_id":1,"code":"Z1","row":0,"column":0,"crop":"Tomato","area_ha":0.25}` (repeat for zones)
3. `POST /api/analysis/analyze` as multipart form data with `zone_id=1` and a JPEG/PNG/WEBP image.
4. Inspect `/api/analysis/1`, `/api/risk/farm/1`, `/api/irrigation/farm/1`, and `/api/progression/farm/1`.
5. `POST /api/simulation/compare` with `{"farm_id":1,"unit_treatment_cost":100,"resource_per_ha":1,"selected_zone_ids":[1],"priority_zone_ids":[1,2]}`.
6. `POST /api/scouting/optimize` with `{"farm_id":1}`.

Irrigation soil moisture is a user-supplied reading. Set `simulated: true` only for demo values; the API labels them as simulated. The current implementation does not calculate irrigation quantities or treatment doses.

## React integration

Use `fetch`/Axios with base URL `http://127.0.0.1:8000/api`. JSON endpoints accept `Content-Type: application/json`. For image upload, use `FormData` keys `zone_id`, `symptoms`, `notes`, `image`; do not manually set the multipart content-type header because the browser supplies its boundary. Responses use JSON and `/docs` provides the live schema. Set `ALLOWED_ORIGINS` to your exact frontend origin before deployment.

## Tests

```powershell
pytest -q
```

## Limitations / next integration steps

- No trained crop disease weights are included; disease predictions remain unavailable until a real model and its preprocessing/class labels are integrated.
- Agronomic second opinion currently returns conservative uncertainty because no validated crop-specific rule database is bundled.
- Risk scores are transparent inspection-priority heuristics, not infection probabilities.
- Route distances are grid steps, not GPS distances. Voice transcription, text-to-speech, weather provider integration, and true multispectral NDVI are not implemented.
- Protect this demo with authentication, rate limiting, HTTPS, stricter upload scanning, database migrations, and production logging before public deployment.
