from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Bao cao Tien do Du an JEDM', border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Trang {self.page_no()}', align='C')

pdf = PDF()
pdf.add_font('Arial', '', r'C:\Windows\Fonts\arial.ttf')
pdf.add_font('Arial', 'B', r'C:\Windows\Fonts\arialbd.ttf')
pdf.add_font('Arial', 'I', r'C:\Windows\Fonts\ariali.ttf')

pdf.add_page()
pdf.set_font('Arial', '', 12)

content = """
Dưới đây là báo cáo tiến độ chi tiết về dự án Sparse-Concept and Calibration (JEDM) tính đến thời điểm hiện tại:

1. Hoàn thành Giai đoạn W2 (Xác minh và Sửa lỗi số liệu)
- Kịch bản C (DeLong Test): Đã sửa lại phương pháp ghép cặp (pairing) bằng cách định nghĩa lại instance_id = user_id + item_id + timestamp + kc_id + cumcount(). Kết quả đã khôi phục 100% dữ liệu bị loại bỏ trước đó. Các p-value mới đạt mức siêu nhỏ (ví dụ: ASSISTments: p = 7.10e-82), bảo vệ vững chắc kết luận thống kê rằng "DKT tốt hơn SimpleKT".
- Kịch bản D (Fold Misalignment): Đã tìm ra lỗi đánh giá nhầm trên Fold 0 đối với mô hình Junyi SimpleKT (seed 2024 và 2025). Đã chạy lại dữ liệu, trích xuất số mới và lập danh sách các bảng LaTeX bị ảnh hưởng để chuẩn bị cập nhật (Table 3, Table 5, Table 9).
- Events Reconciliation: Đối chiếu 45 dòng qua pipeline, chứng minh quá trình giữ lại C4 hoàn toàn chính xác, không có sự rò rỉ (leakage).

2. Hoàn thành Kiểm toán Nội dung Bài báo (Audits)
- Scientific Logic Chain: Chuỗi logic khoa học cực kỳ chặt chẽ (từ Vấn đề -> Đóng góp -> RQ -> Kết quả). Đề xuất bổ sung một dòng làm rõ lý do tại sao chỉ dùng Baseline thay vì SOTA.
- Plagiarism & Readability: Phát hiện một số đoạn văn khuôn mẫu (formulaic sentences) ở phần Related Work có nguy cơ bị tool check đạo văn quét trúng. Đã đề xuất viết lại. Các câu văn dài phần Experiments/Conclusion cũng được kiến nghị tách nhỏ.
- Formula Consistency: Tất cả các công thức toán học về ECE và Brier Score đều khớp hoàn toàn với định nghĩa bằng chữ trong bài.

3. Bước tiếp theo (Giai đoạn W3 - Cập nhật Bản thảo LaTeX)
- Sẽ cập nhật tự động các file Table bị đổi số: table_03, table_05, table_09.
- Sẽ cập nhật số liệu DeLong Test p-value vào phần text của main_jedm.tex.
- Tiến hành tinh chỉnh ngôn từ tránh đạo văn.
"""

pdf.multi_cell(0, 8, content, new_x="LMARGIN", new_y="NEXT")

output_path = r"c:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\w2_verification\report\Bao_cao_tien_do_W2.pdf"
pdf.output(output_path)
print("PDF created at", output_path)
