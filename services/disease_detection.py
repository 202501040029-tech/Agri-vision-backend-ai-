"""Model adapter. No disease label is produced unless a trained model is configured."""
from pathlib import Path
from config import settings

def predict(image_path: str):
    if settings.disease_model_path and Path(settings.disease_model_path).exists():
        # Plug a validated model adapter here; model-specific preprocessing/labels are required.
        return {"disease":"Model adapter not implemented for supplied weights","confidence":None,"severity":None,"model_status":"weights_found_adapter_required"}
    return {"disease":"Unavailable","confidence":None,"severity":None,"model_status":"not_configured"}
