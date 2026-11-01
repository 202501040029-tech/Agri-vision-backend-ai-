def assess(prediction, symptoms, observations):
    if prediction.get('confidence') is None:
        return {"status":"Uncertain diagnosis","explanation":"No configured, validated disease model prediction is available. Visual symptoms alone cannot confirm a disease.","next_action":"Upload a clear image of affected and healthy leaves and seek local agronomist advice if symptoms persist."}
    if not symptoms and not observations:
        return {"status":"Requires another image","explanation":"There are no farmer observations or symptom labels to compare with the model output.","next_action":"Provide observed symptoms and another well-lit image."}
    return {"status":"Uncertain diagnosis","explanation":"The model output has not been independently validated against a crop-specific agronomic rule set.","next_action":"Treat this as a preliminary flag and request expert inspection before treatment."}
