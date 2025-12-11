import threading
import os
import datetime
from flask import request, jsonify, g
from services.llama_service import LlamaService
from services.gemini_service import GeminiService
from services.integration_service import IntegrationService
from models.recommendation_model import RecommendationModel
from exceptions.exceptions import ValidationError

llama_service = LlamaService()
gemini_service = GeminiService()
integration_service = IntegrationService()
rec_model = RecommendationModel()

def async_pipeline(user_id, token, record_id, options):
    print(f"🚀 START Analysis: {record_id}")
    temp_path = None
    try:
        # 1. Lấy info để có fileUrl
        meta = integration_service.get_medical_record_meta(record_id, token)
        if not meta: return
        
        # 2. Tải file
        temp_path = integration_service.download_file(meta['fileUrl'])
        if not temp_path: return

        # 3. Trích xuất dữ liệu (Ảnh vs PDF)
        ext = meta['fileUrl'].split('.')[-1].lower()
        health_data = {}
        raw_text = ""

        if ext in ['jpg', 'png', 'jpeg']:
            print("📸 Image Mode")
            img = PIL.Image.open(temp_path)
            health_data = gemini_service.extract_health_data(img, is_image=True)
            raw_text = "[Image Content]"
        else:
            print("📄 PDF Mode (LlamaParse)")
            raw_text = llama_service.parse_pdf_to_markdown(temp_path)
            health_data = gemini_service.extract_health_data(raw_text, is_image=False)

        # 4. CALLBACK: Cập nhật Health Service ngay lập tức
        integration_service.callback_health_update(record_id, health_data, raw_text)

        # 5. Recommendation (AI Logic)
        recipes = integration_service.search_recipes()
        rec_result = gemini_service.recommend_recipes(health_data, recipes, options)

        # 6. Save Recommendation
        doc = {
            "userId": user_id,
            "medicalRecordId": record_id,
            "recommendations": rec_result.get('recommendations'),
            "analysisSummary": rec_result.get('analysisSummary'),
            "createdAt": datetime.datetime.utcnow().isoformat()
        }
        rec_model.create(doc)
        print("🎉 Analysis Pipeline Done")

    except Exception as e:
        print(f"Pipeline Error: {e}")
    finally:
        if temp_path and os.path.exists(temp_path): os.remove(temp_path)

def trigger_analysis():
    data = request.json
    record_id = data.get('medicalRecordId')
    options = data.get('options', {})
    token = request.headers.get('Authorization')

    # Chạy ngầm
    thread = threading.Thread(target=async_pipeline, args=(g.user_id, token, record_id, options))
    thread.start()

    return jsonify({"message": "Processing...", "analysisId": record_id}), 202

def chat_with_ai():
    """
    API Chat với AI
    """
    data = request.json
    message = data.get('message')
    context = data.get('context', {})
    
    if not message:
        raise ValidationError("Message is required")
        
    reply = gemini_service.chat_nutrition(message, context)
    
    return jsonify({
        "message": reply,
        "conversationId": context.get("conversationId", "new_conv"),
        "relatedRecipes": [],
        "sources": [{"type": "ai_generated", "title": "Gemini 1.5 Flash"}]
    }), 200