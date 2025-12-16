import threading
import os
import datetime
from flask import request, jsonify, g
import PIL.Image

# --- IMPORTS ---
from services.llama_service import LlamaService
# [THAY ĐỔI 1] Import GroqService thay vì GeminiService
from services.groq_service import GroqService 
from services.integration_service import IntegrationService
from models.recommendation_model import RecommendationModel
from exceptions.exceptions import ValidationError

# --- INIT SERVICES ---
llama_service = LlamaService()
# [THAY ĐỔI 2] Khởi tạo GroqService
groq_service = GroqService()
integration_service = IntegrationService()
rec_model = RecommendationModel()

def async_pipeline(user_id, token, record_id, options):
    print(f"🚀 START Analysis: {record_id}")
    temp_path = None
    
    try:
        # 1. Lấy metadata
        meta = integration_service.get_medical_record_meta(record_id, token)
        if not meta: 
            print("❌ Cannot fetch record metadata")
            return
        
        # 2. Tải file về
        temp_path = integration_service.download_file(meta['fileUrl'])
        if not temp_path: 
            print("❌ Cannot download file")
            return

        # 3. Phân loại & Trích xuất dữ liệu
        ext = meta['fileUrl'].split('.')[-1].lower() if '.' in meta['fileUrl'] else 'txt'
        
        health_data = {}
        raw_text = ""

        if ext in ['jpg', 'png', 'jpeg', 'webp']:
            print("📸 Image Mode: Processing with Groq Vision")
            img = PIL.Image.open(temp_path)
            # [THAY ĐỔI 3] Dùng groq_service cho ảnh
            health_data = groq_service.extract_health_data(img, is_image=True)
            raw_text = "[Image Content Processed]"

        elif ext == 'txt':
            print("📄 Text Mode: Reading raw text file")
            with open(temp_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            # [THAY ĐỔI 4] Dùng groq_service cho text
            health_data = groq_service.extract_health_data(raw_text, is_image=False)

        elif ext == 'pdf':
            print("📑 PDF Mode: Sending to LlamaParse")
            # Dùng LlamaParse để lấy text từ PDF
            raw_text = llama_service.parse_pdf_to_markdown(temp_path)
            # [THAY ĐỔI 5] Dùng groq_service phân tích text từ PDF
            health_data = groq_service.extract_health_data(raw_text, is_image=False)
            
        else:
            print(f"⚠️ Unsupported file extension: {ext}")
            return

        # 4. CALLBACK: Cập nhật Health Service
        integration_service.callback_health_update(record_id, health_data, raw_text)

        # 5. Recommendation (AI Logic)
        # Gọi Recipe Service để lấy danh sách món ăn
        recipes = integration_service.search_recipes() 
        
        # [THAY ĐỔI 6] Dùng groq_service để gợi ý món ăn
        rec_result = groq_service.recommend_recipes(health_data, recipes, options)

        # 6. Save Recommendation
        doc = {
            "userId": user_id,
            "medicalRecordId": record_id,
            "recommendations": rec_result.get('recommendations', []),
            "analysisSummary": rec_result.get('analysisSummary', ''),
            "createdAt": datetime.datetime.utcnow().isoformat()
        }
        rec_model.create(doc)
        print(f"🎉 Analysis Pipeline Done for {record_id}")

    except Exception as e:
        print(f"🔥 Pipeline Error: {e}")
    finally:
        # Dọn dẹp file rác
        if temp_path and os.path.exists(temp_path): 
            try:
                os.remove(temp_path)
            except: pass

def trigger_analysis():
    data = request.json
    record_id = data.get('medicalRecordId')
    options = data.get('options', {})
    token = request.headers.get('Authorization')

    if not record_id:
        return jsonify({"message": "Missing medicalRecordId"}), 400

    # Chạy ngầm (Fire & Forget)
    thread = threading.Thread(target=async_pipeline, args=(g.user_id, token, record_id, options))
    thread.start()

    return jsonify({"message": "Processing started", "analysisId": record_id}), 202

def chat_with_ai():
    """
    API Chat với AI
    """
    data = request.json
    message = data.get('message')
    context = data.get('context', {})
    
    if not message:
        raise ValidationError("Message is required")
        
    # [THAY ĐỔI 7] Dùng groq_service để chat
    reply = groq_service.chat_nutrition(message, context)
    
    return jsonify({
        "message": reply,
        "conversationId": context.get("conversationId", "new_conv"),
        "relatedRecipes": [],
        "sources": [{"type": "ai_generated", "title": "Llama 3 (via Groq)"}]
    }), 200