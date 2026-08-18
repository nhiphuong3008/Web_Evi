"""
EVI Dashboard - Student Report Export Service
Xuất Báo Cáo Học Tập Học Sinh ra các định dạng PDF (Trang in ấn), Word (.doc/.docx) và Excel (.xlsx/.csv).
"""

import logging
import io

logger = logging.getLogger(__name__)


def generate_printable_html_report(student, homework=[], grades=[], cm_notes=[], ai_assessment={}):
    """Tạo báo cáo học tập định dạng HTML cao cấp ready cho In ấn/Lưu PDF."""
    st_name = student.get('full_name', student.get('name', ''))
    en_name = student.get('english_name', '')
    st_code = student.get('code', '')
    class_name = student.get('class_name', '')
    parent_name = student.get('parent_name', '')
    phone = student.get('phone', '')
    rem_sess = student.get('remaining_sessions', 0)

    # Unit grades table rows
    grade_rows = ''
    if grades:
        for g in grades:
            pct = round((g.get('total_score', 0) / (g.get('max_score') or 10.0)) * 100, 1) if g.get('total_score') is not None else 0
            grade_rows += f"""
            <tr>
                <td><strong>{g.get('test_name', 'UNIT TEST')}</strong></td>
                <td>{g.get('class_name', '')}</td>
                <td><strong style="color: #4f46e5;">{g.get('listening') if g.get('listening') is not None else '—'}</strong> / 10</td>
                <td><strong style="color: #059669;">{g.get('reading_writing') if g.get('reading_writing') is not None else '—'}</strong> / 12</td>
                <td><strong style="color: #d97706;">{g.get('speaking') if g.get('speaking') is not None else '—'}</strong> / 10</td>
                <td><strong style="font-size: 14px; color: #1e1b4b;">{g.get('total_score') if g.get('total_score') is not None else '—'}</strong></td>
                <td><em>{g.get('comment', 'Chưa có nhận xét')}</em></td>
            </tr>
            """
    else:
        grade_rows = '<tr><td colspan="7" style="text-align: center; color: #64748b;">Chưa có dữ liệu bài kiểm tra</td></tr>'

    # Homework summary
    sub_hw = len([h for h in homework if h.get('status') == 'Đã nộp'])
    tot_hw = len(homework)

    # Strengths & Improvements HTML
    strengths_html = "".join([f"<li>{s}</li>" for s in ai_assessment.get('strengths', [])])
    improvements_html = "".join([f"<li>{imp}</li>" for imp in ai_assessment.get('improvements', [])])

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo Cáo Học Tập - {st_name} ({st_code})</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.5; margin: 0; padding: 20px; }}
        .report-container {{ max-width: 850px; margin: 0 auto; background: #ffffff; padding: 36px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
        .report-header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #6366f1; padding-bottom: 16px; margin-bottom: 24px; }}
        .logo-title {{ display: flex; align-items: center; gap: 14px; }}
        .logo-box {{ background: linear-gradient(135deg, #6366f1, #4f46e5); color: #fff; width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 800; }}
        .center-info {{ font-size: 13px; color: #64748b; text-align: right; line-height: 1.3; }}
        .title-banner {{ text-align: center; margin-bottom: 24px; }}
        .title-banner h1 {{ font-size: 24px; color: #1e1b4b; margin: 0; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
        .title-banner p {{ color: #6366f1; font-weight: 600; font-size: 14px; margin-top: 4px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; background: #f1f5f9; padding: 16px 20px; border-radius: 10px; margin-bottom: 24px; border: 1px solid #cbd5e1; font-size: 13px; }}
        .info-item strong {{ color: #334155; }}
        .section-title {{ font-size: 16px; font-weight: 700; color: #1e1b4b; border-left: 4px solid #6366f1; padding-left: 10px; margin: 24px 0 12px 0; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }}
        th {{ background: #4f46e5; color: #ffffff; padding: 10px 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        .ai-box {{ background: #eef2ff; border: 1px solid #c7d2fe; padding: 18px 20px; border-radius: 10px; margin-bottom: 24px; }}
        .ai-box h3 {{ margin-top: 0; color: #3730a3; font-size: 15px; display: flex; align-items: center; gap: 8px; }}
        .ai-box ul {{ margin: 8px 0; padding-left: 20px; font-size: 13px; color: #334155; }}
        .ai-box li {{ margin-bottom: 4px; }}
        .footer-note {{ margin-top: 36px; display: flex; justify-content: space-between; text-align: center; font-size: 13px; color: #475569; }}
        .sign-box {{ width: 200px; }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .report-container {{ box-shadow: none; border: none; padding: 0; width: 100%; max-width: 100%; }}
            .no-print {{ display: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="text-align: center; margin-bottom: 20px;">
        <button onclick="window.print();" style="padding: 10px 24px; background: #4f46e5; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);">
            🖨️ In Báo Cáo / Lưu PDF
        </button>
    </div>

    <div class="report-container">
        <!-- Header -->
        <div class="report-header">
            <div class="logo-title">
                <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 56px; height: 56px; object-fit: contain;">
                <div>
                    <h2 style="margin: 0; font-size: 20px; color: #0432ff; font-weight: 900; letter-spacing: 0.5px;">TRUNG TÂM ANH NGỮ VICARE</h2>
                    <div style="font-size: 12px; color: #e60000; font-weight: 800; letter-spacing: 0.3px;">VICARE ENGLISH CENTER</div>
                </div>
            </div>
            <div class="center-info">
                <strong>Trung Tâm Anh Ngữ Vicare</strong><br>
                Hotline: 098.xxx.xxxx | Email: info@vicare.edu.vn<br>
                Ngày xuất báo cáo: {ai_assessment.get('export_date', '2026-08-01')}
            </div>
        </div>

        <!-- Title -->
        <div class="title-banner">
            <h1>BÁO CÁO KẾT QUẢ HỌC TẬP HỌC SINH</h1>
            <p>Báo cáo tổng hợp tiến độ, điểm số & Nhận xét quá trình học</p>
        </div>

        <!-- Student Info -->
        <div class="info-grid">
            <div class="info-item">👤 <strong>Họ và tên học sinh:</strong> {st_name} {f'({en_name})' if en_name else ''}</div>
            <div class="info-item">🏷️ <strong>Mã học viên:</strong> {st_code}</div>
            <div class="info-item">🏫 <strong>Lớp đang học:</strong> {class_name or 'Chưa xếp lớp'}</div>
            <div class="info-item">👨‍👩‍👧 <strong>Phụ huynh / SĐT:</strong> {parent_name or 'Chưa cập nhật'} {f'- {phone}' if phone else ''}</div>
            <div class="info-item">⏳ <strong>Số buổi học còn lại:</strong> {rem_sess} buổi</div>
            <div class="info-item">📝 <strong>Tỷ lệ làm BTVN:</strong> {sub_hw} / {tot_hw} buổi ({ai_assessment.get('homework_rate', 100)}%)</div>
        </div>

        <!-- AI Progress Evaluation -->
        <div class="ai-box">
            <h3>✨ ĐÁNH GIÁ TỔNG QUAN QUÁ TRÌNH HỌC TẬP (AI SYNTHESIZED)</h3>
            <p style="font-size: 13.5px; font-weight: 500; color: #1e1b4b; margin-bottom: 10px;">
                {ai_assessment.get('summary', '')}
            </p>

            <strong style="color: #047857; font-size: 13px;">🌟 Điểm mạnh nổi bật:</strong>
            <ul>{strengths_html}</ul>

            <strong style="color: #b45309; font-size: 13px;">🎯 Điểm cần lưu ý & cải thiện:</strong>
            <ul>{improvements_html}</ul>

            <div style="margin-top: 10px; font-size: 13px; color: #4338ca; background: #e0e7ff; padding: 10px; border-radius: 6px;">
                💡 <strong>Khuyến nghị dành cho Phụ huynh:</strong> {ai_assessment.get('recommendations', '')}
            </div>
        </div>

        <!-- Section 1: Test Scores -->
        <div class="section-title">💯 LỊCH SỬ VÀ CHI TIẾT ĐIỂM THI CÁC KỲ TEST</div>
        <table>
            <thead>
                <tr>
                    <th>Bài kiểm tra</th>
                    <th>Lớp</th>
                    <th>Nghe (Listening)</th>
                    <th>Đọc - Viết (R&W)</th>
                    <th>Nói (Speaking)</th>
                    <th>Tổng điểm</th>
                    <th>Nhận xét của Giáo viên</th>
                </tr>
            </thead>
            <tbody>
                {grade_rows}
            </tbody>
        </table>

        <!-- Section 2: Teacher & CM Notes -->
        <div class="section-title">💬 TỔNG HỢP NHẬN XÉT CỦA GIÁO VIÊN & CLASS MANAGER (CM)</div>
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; padding: 14px; border-radius: 8px; font-size: 13px; margin-bottom: 24px;">
            <div style="margin-bottom: 8px;"><strong>👨‍🏫 Nhận xét tổng hợp từ Giáo viên:</strong></div>
            <div style="color: #334155; font-style: italic; margin-bottom: 12px; padding-left: 12px; border-left: 3px solid #6366f1;">
                "{ai_assessment.get('teacher_notes_summary', 'Con học tốt, tiếp thu bài nhanh và ngoan ngoãn.')}"
            </div>
            <div style="margin-bottom: 8px;"><strong>👩‍💼 Ghi chú theo dõi từ CM (Class Manager):</strong></div>
            <div style="color: #334155; font-style: italic; padding-left: 12px; border-left: 3px solid #10b981;">
                "{ai_assessment.get('cm_notes_summary', 'Gia đình phối hợp tốt với trung tâm.')}"
            </div>
        </div>

        <!-- Footer Signatures -->
        <div class="footer-note">
            <div class="sign-box">
                <strong>ĐẠI DIỆN TRUNG TÂM (CM)</strong><br><br><br>
                <em>(Ký và ghi rõ họ tên)</em>
            </div>
            <div class="sign-box">
                <strong>GIÁO VIÊN CHỦ PHỤ TRÁCH</strong><br><br><br>
                <em>(Ký và ghi rõ họ tên)</em>
            </div>
        </div>

        <!-- Watermark Footer -->
        <div style="margin-top: 36px; border-top: 1.5px dashed #cbd5e1; padding-top: 14px; display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; color: #64748b;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <img src="/static/images/logo.jpg" style="width: 16px; height: 16px; object-fit: contain;">
                <strong>Trung tâm Anh ngữ Vicare</strong> - Hệ thống báo cáo học tập chính thức
            </div>
            <div>✨ Thiết kế bởi: <strong style="color: #0284c7; font-weight: 800;">Nhi Phương</strong></div>
        </div>
    </div>
</body>
</html>
"""
    return html_content


def generate_word_report(student, homework=[], grades=[], cm_notes=[], ai_assessment={}):
    """Tạo báo cáo học tập file Word (.doc) tương thích Microsoft Word 100%."""
    html_body = generate_printable_html_report(student, homework, grades, cm_notes, ai_assessment)
    # Wrap in Word HTML Header
    word_html = f"""<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><title>Báo cáo học tập</title>
    <!--[if gte mso 9]>
    <xml>
    <w:WordDocument>
    <w:View>Print</w:View>
    <w:Zoom>100</w:Zoom>
    <w:DoNotOptimizeForBrowser/>
    </w:WordDocument>
    </xml>
    <![endif]-->
    </head>
    {html_body}
    </html>
    """
    return word_html.encode('utf-8')


def generate_excel_report(student, homework=[], grades=[], cm_notes=[], ai_assessment={}):
    """Tạo file báo cáo CSV/Excel UTF-8 BOM chứa toàn bộ lịch sử điểm số và nhận xét."""
    output = io.StringIO()
    output.write('\ufeff') # UTF-8 BOM for Excel

    st_name = student.get('full_name', student.get('name', ''))
    st_code = student.get('code', '')
    class_name = student.get('class_name', '')
    parent_name = student.get('parent_name', '')
    phone = student.get('phone', '')

    output.write(f"BÁO CÁO HỌC TẬP HỌC SINH EVI ACADEMY\n")
    output.write(f"Mã học viên,{st_code}\n")
    output.write(f"Họ và tên,{st_name}\n")
    output.write(f"Lớp học,{class_name}\n")
    output.write(f"Phụ huynh,{parent_name}\n")
    output.write(f"SĐT,{phone}\n\n")

    output.write("1. ĐÁNH GIÁ TỔNG QUAN VÀ TIẾN ĐỘ HỌC TẬP (AI SYNTHESIS)\n")
    output.write(f"Đánh giá chung,\"{ai_assessment.get('summary', '')}\"\n")
    output.write(f"Xếp loại trình độ,{ai_assessment.get('level_evaluation', '')}\n")
    output.write(f"Khuyên nghị Phụ huynh,\"{ai_assessment.get('recommendations', '')}\"\n\n")

    output.write("2. BẢNG ĐIỂM THI CÁC BÀI KÍỂM TRA (UNIT TESTS)\n")
    output.write("STT,Bài kiểm tra,Lớp,Nghe (Listening),Đọc - Viết (R&W),Nói (Speaking),Tổng điểm,Max điểm,Nhận xét Giáo viên\n")

    if grades:
        for idx, g in enumerate(grades, 1):
            lis = g.get('listening') if g.get('listening') is not None else ''
            rw = g.get('reading_writing') if g.get('reading_writing') is not None else ''
            spk = g.get('speaking') if g.get('speaking') is not None else ''
            tot = g.get('total_score') if g.get('total_score') is not None else ''
            max_s = g.get('max_score') or 10.0
            cmt = (g.get('comment') or '').replace('"', '""')
            output.write(f"{idx},\"{g.get('test_name','')}\",\"{g.get('class_name','')}\",{lis},{rw},{spk},{tot},{max_s},\"{cmt}\"\n")

    output.write("\n3. NHẬT KÝ BÀI VỀ NHÀ (BTVN)\n")
    output.write("STT,Ngày,Lớp,Tình trạng BTVN,Điểm số\n")
    if homework:
        for idx, h in enumerate(homework, 1):
            output.write(f"{idx},\"{h.get('date','')}\",\"{h.get('class_name','')}\",\"{h.get('status','')}\",\"{h.get('score','')}\"\n")

    return output.getvalue().encode('utf-8')
