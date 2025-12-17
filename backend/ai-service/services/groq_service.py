import os
import json
import base64
import io
from groq import Groq

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Model cho text/chat (Logic mạnh)
        self.text_model = "llama-3.3-70b-versatile"
        # Model cho ảnh (Vision)
        self.vision_model = "llama-3.2-11b-vision-preview"

    def _image_to_base64(self, pil_image):
        """Chuyển đổi PIL Image sang Base64 string"""
        buffered = io.BytesIO()
        # Convert sang RGB để tránh lỗi mode RGBA của PNG
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        pil_image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def extract_health_data(self, content_input, is_image=False):
        """Trích xuất dữ liệu từ Text hoặc Ảnh"""
        
        system_prompt = """
        Bạn là trợ lý y tế AI. Nhiệm vụ: Trích xuất thông tin từ tài liệu thành JSON.
        Output JSON Schema bắt buộc:
        {
            "patientInfo": { "fullName": "", "age": 0, "gender": "" },
            "healthConditions": [ { "condition": "", "severity": "" } ],
            "labResults": { "bloodPressure": { "systolic": 0, "diastolic": 0 }, "bloodSugar": {"value": 0, "unit": ""} },
            "doctorNotes": ""
        }
        """

        messages = []
        model = self.text_model

        if is_image:
            # Xử lý input là Ảnh
            model = self.vision_model
            base64_image = self._image_to_base64(content_input)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]
        else:
            # Xử lý input là Text
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"DOCUMENT CONTENT:\n{content_input}"}
            ]

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=0.1,
                response_format={"type": "json_object"} # Ép buộc trả về JSON
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"❌ Groq Extract Error: {e}")
            return {
                "patientInfo": {}, "healthConditions": [], "labResults": {}, "doctorNotes": "Error extracting data"
            }

    def recommend_recipes(self, health_data, recipes, options):
        prompt = f"""
        Vai trò: Chuyên gia dinh dưỡng.
        Hồ sơ bệnh nhân: {json.dumps(health_data, ensure_ascii=False)}
        Kho món ăn: {json.dumps(recipes, ensure_ascii=False)}
        
        Yêu cầu: Chọn {options.get('maxRecommendations', 5)} món phù hợp nhất.
        Output JSON Format: 
        {{
            "analysisSummary": "Giải thích ngắn gọn tình trạng sức khỏe", 
            "recommendations": [{{"recipeId": "ID_MON_AN", "reason": "Lý do chọn"}}]
        }}
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON generator."},
                    {"role": "user", "content": prompt}
                ],
                model=self.text_model,
                response_format={"type": "json_object"} # Ép buộc trả về JSON
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"❌ Groq Recommend Error: {e}")
            return {"analysisSummary": "Lỗi kết nối AI", "recommendations": []}

    def chat_nutrition(self, message, context):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"Context: {context}. Answer helpful and short."},
                    {"role": "user", "content": message}
                ],
                model=self.text_model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq Chat Error: {e}")
            return "Xin lỗi, hệ thống đang bận."