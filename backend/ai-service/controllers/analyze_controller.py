import threading
import os
from flask import request, jsonify
from services.llama_service import LlamaService
from services.groq_service import GroqService 
from services.integration_service import IntegrationService
from models.recommendation_model import RecommendationModel
from exceptions.exceptions import ValidationError

# --- INIT SERVICES ---
llama_service = LlamaService()
groq_service = GroqService()
integration_service = IntegrationService()
rec_model = RecommendationModel()

# --- 1. HÀM XỬ LÝ NGẦM (PIPELINE) ---
def async_pipeline(record_id, token):
    """
    Hàm này chạy trong Thread riêng.
    Nhiệm vụ: Tải file -> Parse PDF -> Extract Data -> Gọi ngược về Health Service cập nhật
    """
    print(f"🚀 [Async] START Analysis for Record: {record_id}")
    temp_path = None
    
    try:
        # Bước 1: Lấy metadata từ Health Service (để lấy File URL)
        meta = integration_service.get_medical_record_meta(record_id, token)
        if not meta: 
            print(f"❌ [Async] Cannot fetch metadata for {record_id}")
            return
        
        # Đảm bảo có userId trong meta
        user_id_from_meta = meta.get('userId')
        if not user_id_from_meta:
            print(f"❌ [Async] Missing userId in medical record meta for {record_id}")
            return
        print(f"👤 [Async] Medical record userId: {user_id_from_meta}")
        
        # Lấy title từ meta để lưu vào recommendation
        medical_record_title = meta.get('title', 'Untitled')
        print(f"📋 [Async] Medical record title: {medical_record_title}")
        
        file_url = meta.get('fileUrl')
        print(f"📥 [Async] Downloading file from: {file_url}...")

        # Bước 2: Tải file về máy
        temp_path = integration_service.download_file(file_url)
        if not temp_path: 
            print(f"❌ [Async] Download failed.")
            integration_service.update_medical_record(record_id, token, {
                "status": "failed",
                "errorMessage": "Cannot download file from Media Service"
            })
            return

        # Bước 3: Phân tích AI (LlamaParse + Groq)
        print("🤖 [Async] Parsing PDF with LlamaParse...")
        markdown_text = llama_service.parse_pdf_to_markdown(temp_path)
        
        print("🧠 [Async] Extracting data with Groq...")
        extracted_data = groq_service.extract_health_data(markdown_text, is_image=False)
        print(f"✅ [Async] Data extraction completed")
        
        # Bước 4: Tạo Recommendation (Gợi ý món ăn) - TỰ ĐỘNG TẠO KHI UPLOAD HEALTH RECORD
        print("🍳 [Async] Generating recipe recommendations...")
        user_id = user_id_from_meta  # Dùng userId đã kiểm tra ở bước 1
        print(f"👤 [Async] Using userId for recommendation: {user_id}")
        
        try:
            # Lấy danh sách recipes từ Recipe Service
            recipes = integration_service.search_recipes()
            print(f"📋 [Async] Found {len(recipes)} recipes from Recipe Service")
            
            if len(recipes) > 0:
                # Gọi AI để gợi ý món ăn dựa trên health data
                options = {"maxRecommendations": 5}
                ai_recommendation = groq_service.recommend_recipes(extracted_data, recipes, options)
                
                recommendations_list = ai_recommendation.get('recommendations', [])
                print(f"✅ [Async] AI generated {len(recommendations_list)} recommendations")
                
                # Lưu recommendation vào MongoDB
                recommendation_data = {
                    "userId": user_id,
                    "medicalRecordId": record_id,
                    "medicalRecordTitle": medical_record_title,  # Lưu title để không cần fetch lại
                    "analysisSummary": ai_recommendation.get("analysisSummary", "Đã phân tích hồ sơ sức khỏe và gợi ý món ăn phù hợp"),
                    "recommendations": recommendations_list,
                    "healthData": extracted_data
                }
                
                rec_id = rec_model.create(recommendation_data)
                print(f"💾 [Async] Recommendation saved with ID: {rec_id} for userId: {user_id}")
            else:
                print("⚠️ [Async] No recipes available, skipping recommendation generation")
        except Exception as e:
            print(f"⚠️ [Async] Recommendation generation failed: {e}")
            import traceback
            traceback.print_exc()
            # Không fail toàn bộ pipeline nếu recommendation fail
        
        # Bước 5: Gọi Callback về Health Service
        print("🔄 [Async] Sending results back to Health Service...")
        update_payload = {
            "status": "processed",
            "extractedText": markdown_text[:1000] + "...", # Lưu tóm tắt text (optional)
            "extractedData": extracted_data  
        }
        
        success = integration_service.update_medical_record(record_id, token, update_payload)
        
        if success:
            print(f"✅ [Async] Pipeline COMPLETED for {record_id}")
        else:
            print(f"⚠️ [Async] Pipeline finished but failed to update Health Service")

    except Exception as e:
        print(f"🔥 [Async] Pipeline Error: {e}")
        # Báo lỗi về Health Service
        integration_service.update_medical_record(record_id, token, {
            "status": "failed",
            "errorMessage": str(e)
        })
        
    finally:
        # Dọn dẹp file tạm
        if temp_path and os.path.exists(temp_path): 
            try:
                os.remove(temp_path)
                print("🧹 [Async] Temp file cleaned.")
            except: pass

# --- 2. HÀM CONTROLLER (NHẬN REQUEST TỪ HEALTH SERVICE) ---
def trigger_analysis():
    """
    API Handler: POST /analyze
    Nhiệm vụ: Nhận request, khởi động Thread, trả về 200 OK ngay lập tức.
    """
    try:
        # Lấy dữ liệu từ Health Service gửi sang
        data = request.json
        record_id = data.get('medicalRecordId')
        
        # Lấy Token từ header (để lát nữa dùng gọi ngược lại Health Service)
        token = request.headers.get('Authorization')

        print(f"📥 [Controller] Received request for Record ID: {record_id}")

        if not record_id:
            return jsonify({"error": "Missing medicalRecordId"}), 400

        # --- CHẠY ASYNC PIPELINE ---
        # Truyền record_id và token vào luồng xử lý
        thread = threading.Thread(target=async_pipeline, args=(record_id, token))
        thread.start()

        # --- QUAN TRỌNG: TRẢ VỀ KẾT QUẢ NGAY (KHẮC PHỤC LỖI 500) ---
        return jsonify({
            "message": "AI analysis started successfully",
            "status": "processing",
            "medicalRecordId": record_id
        }), 200

    except Exception as e:
        print(f"❌ [Controller] Error: {e}")
        return jsonify({"error": str(e)}), 500

# --- 3. HÀM CHAT (GIỮ NGUYÊN) ---
def chat_with_ai():
    try:
        data = request.json
        message = data.get('message')
        context = data.get('context', {})
        
        if not message:
            raise ValidationError("Message is required")
            
        response_text = groq_service.chat_nutrition(message, str(context))
        return jsonify({"message": response_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500