import google.generativeai as genai
import os
import json
import PIL.Image

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _clean_json(self, text):
        text = text.replace('```json', '').replace('```', '').strip()
        start, end = text.find('{'), text.rfind('}')
        if start != -1 and end != -1: return text[start:end+1]
        return text

    def extract_health_data(self, text_or_image, is_image=False):
        """Trích xuất dữ liệu y tế từ Markdown hoặc Ảnh"""
        prompt = """
        Trích xuất thông tin y tế từ tài liệu này thành JSON.
        Output Schema:
        {
            "patientInfo": { "fullName": "", "age": 0, "gender": "" },
            "healthConditions": [ { "condition": "", "severity": "" } ],
            "labResults": { "bloodPressure": { "systolic": 0, "diastolic": 0 }, "bloodSugar": {"value": 0, "unit": ""} },
            "doctorNotes": ""
        }
        """
        try:
            inputs = [prompt, text_or_image] if is_image else [prompt + f"\n\nTEXT:\n{text_or_image}"]
            resp = self.model.generate_content(inputs)
            return json.loads(self._clean_json(resp.text))
        except Exception as e:
            print(f"Gemini Extract Error: {e}")
            return {}

    def recommend_recipes(self, health_data, recipes, options):
        """Gợi ý món ăn"""
        prompt = f"""
        Dựa vào hồ sơ sức khỏe: {json.dumps(health_data, ensure_ascii=False)}
        Và danh sách món ăn: {json.dumps(recipes, ensure_ascii=False)}
        Hãy chọn {options.get('maxRecommendations', 5)} món phù hợp nhất.
        Output JSON: {{"analysisSummary": "", "recommendations": [{{"recipeId": "", "reason": ""}}]}}
        """
        try:
            resp = self.model.generate_content(prompt)
            return json.loads(self._clean_json(resp.text))
        except Exception as e:
            return {"analysisSummary": "Error", "recommendations": []}
            
    def chat_nutrition(self, message, context):
        """Chatbot"""
        prompt = f"Context: {context}. User Question: {message}. Answer shortly."
        try:
            return self.model.generate_content(prompt).text
        except: return "Error generating response."