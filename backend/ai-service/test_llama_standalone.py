import os
import sys
from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Load biến môi trường (API KEY)
load_dotenv()

# Import Service (Đảm bảo bạn đang đứng ở thư mục gốc ai-service)
try:
    from services.llama_service import LlamaService
except ImportError:
    # Hack để python tìm thấy module nếu chạy lỗi path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from services.llama_service import LlamaService

FILE_NAME = "test_llama_input.pdf"

def create_complex_pdf():
    """Tạo một file PDF có cả Text và Table để test LlamaParse"""
    print(f"ℹ️  Đang tạo file PDF mẫu: {FILE_NAME}...")
    doc = SimpleDocTemplate(FILE_NAME, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # 1. Tiêu đề
    story.append(Paragraph("PHIEU KET QUA XET NGHIEM (Test LlamaParse)", styles['Title']))
    story.append(Spacer(1, 12))

    # 2. Đoạn văn bản (Text thường)
    story.append(Paragraph("Thong tin benh nhan:", styles['Heading2']))
    story.append(Paragraph("Ho ten: Nguyen Van Llama", styles['Normal']))
    story.append(Paragraph("Ma so: 123456 - Tuoi: 30", styles['Normal']))
    story.append(Spacer(1, 12))

    # 3. Bảng biểu (Table) - Phần khó nhất với các parser thường
    story.append(Paragraph("Ket qua chi tiet:", styles['Heading2']))
    data = [
        ['Ten Xet Nghiem', 'Ket Qua', 'Don Vi', 'Tri So Binh Thuong'], # Header
        ['Glucose (Doi)', '150', 'mg/dL', '70 - 100'],
        ['Cholesterol TP', '240', 'mg/dL', '< 200'],
        ['HDL-C', '35', 'mg/dL', '> 40'],
        ['LDL-C', '160', 'mg/dL', '< 130']
    ]
    
    # Style cho bảng đẹp
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    
    # 4. Footer text
    story.append(Spacer(1, 12))
    story.append(Paragraph("Ket luan bac si: Roi loan lipid mau, nghi ngo tieu duong.", styles['Normal']))

    doc.build(story)
    print("✅ Đã tạo file PDF thành công!\n")

def run_test():
    # 1. Kiểm tra API Key
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("❌ LỖI: Chưa cấu hình LLAMA_CLOUD_API_KEY trong file .env")
        return

    # 2. Tạo file PDF
    create_complex_pdf()

    # 3. Khởi tạo Service
    service = LlamaService()

    print("🚀 Bắt đầu gửi file lên LlamaCloud...")
    print("   (Quá trình này có thể mất 20-40 giây tùy độ dài hàng đợi của Llama)...")
    
    try:
        # 4. Gọi hàm Parse
        start_time = time.time()
        markdown_result = service.parse_pdf_to_markdown(FILE_NAME)
        end_time = time.time()

        print("\n================ KẾT QUẢ TRẢ VỀ ================")
        print(markdown_result)
        print("==================================================")
        print(f"✅ Xử lý thành công trong {round(end_time - start_time, 2)} giây.")

        # 5. Kiểm tra nhanh xem có đọc được dữ liệu trong bảng không
        if "150" in markdown_result and "Glucose" in markdown_result:
            print("🌟 KIỂM TRA: LlamaParse đã đọc đúng dữ liệu trong Bảng!")
        else:
            print("⚠️ KIỂM TRA: Có vẻ thiếu dữ liệu bảng, hãy check lại markdown.")

    except Exception as e:
        print(f"\n❌ LỖI KHI GỌI LLAMA SERVICE: {e}")
    finally:
        # Dọn dẹp file
        # if os.path.exists(FILE_NAME): os.remove(FILE_NAME)
        pass

if __name__ == "__main__":
    import time # Import lại time ở đây để dùng đo giờ
    run_test()