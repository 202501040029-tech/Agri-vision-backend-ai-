from config import settings

def reply(message, language='en', context=None):
    if not settings.gemini_api_key:
        return {"response":"Gemini is not configured. I can provide only general guidance: share the crop, observed symptoms, and available inspection data. Do not apply pesticides or change irrigation solely from an unverified AI suggestion.","provider":"fallback","language":language}
    try:
        from google import genai
        client=genai.Client(api_key=settings.gemini_api_key)
        prompt=(f"Answer in {language}. You are an agricultural information assistant. Do not invent diagnoses, pesticide doses, or measurements. Clearly state uncertainty. Context: {context or {}}\nFarmer: {message}")
        res=client.models.generate_content(model=settings.gemini_model,contents=prompt)
        return {"response":res.text or 'No response generated.',"provider":"gemini","language":language}
    except Exception as e:
        return {"response":"Assistant service is temporarily unavailable. Please try again later.","provider":"fallback","language":language,"error":str(e)}
