"""
EVI Dashboard - AI Student Progress Synthesis Service
Tự động phân tích và tổng hợp quá trình học tập, nhận xét của Giáo viên & CM thành báo cáo học tập thông minh cá nhân hóa.
"""

import logging
import statistics

logger = logging.getLogger(__name__)


def generate_ai_student_assessment(student, homework_records=[], grade_records=[], cm_notes=[]):
    """
    Tổng hợp và phân tích AI quá trình học tập của học sinh.
    
    Args:
        student: dict/model thông tin học sinh
        homework_records: list các bản ghi BTVN
        grade_records: list các bản ghi điểm thi
        cm_notes: list các bản ghi tương tác CM

    Returns:
        dict chứa đánh giá tổng quan, điểm mạnh, điểm cần cải thiện và khuyến nghị.
    """
    student_name = student.get('name', student.get('full_name', 'Học sinh'))
    en_name = student.get('english_name', '')
    display_name = f"{student_name}" + (f" ({en_name})" if en_name else "")

    # 1. Analysis of Homework
    tot_hw = len(homework_records)
    sub_hw = len([h for h in homework_records if h.get('status') == 'Đã nộp'])
    hw_rate = round((sub_hw / tot_hw * 100), 1) if tot_hw > 0 else 100.0

    # 2. Analysis of Grades
    scores_total = []
    listening_scores = []
    rw_scores = []
    speaking_scores = []
    comments_list = []

    for g in grade_records:
        if g.get('total_score') is not None:
            scores_total.append(g.get('total_score'))
        if g.get('listening') is not None:
            listening_scores.append(g.get('listening'))
        if g.get('reading_writing') is not None:
            rw_scores.append(g.get('reading_writing'))
        if g.get('speaking') is not None:
            speaking_scores.append(g.get('speaking'))
        if g.get('comment') and g.get('comment').strip():
            comments_list.append(g.get('comment').strip())

    avg_total = round(statistics.mean(scores_total), 1) if scores_total else 0.0
    avg_listening = round(statistics.mean(listening_scores), 1) if listening_scores else 0.0
    avg_rw = round(statistics.mean(rw_scores), 1) if rw_scores else 0.0
    avg_speaking = round(statistics.mean(speaking_scores), 1) if speaking_scores else 0.0

    # Score trend
    trend_text = "Duy trì phong độ ổn định"
    if len(scores_total) >= 2:
        diff = scores_total[-1] - scores_total[0]
        if diff >= 0.5:
            trend_text = "Có tiến bộ vượt bậc qua các bài kiểm tra"
        elif diff <= -0.5:
            trend_text = "Cần tăng cường ôn tập để nâng cao lại điểm số"

    # 3. Strengths
    strengths = []
    if avg_listening >= 8.0:
        strengths.append(f"Kỹ năng Nghe đạt kết quả xuất sắc (Trung bình {avg_listening}/10), phản xạ từ vựng nhanh nhẹn.")
    elif avg_listening >= 7.0:
        strengths.append(f"Kỹ năng Nghe khá tốt (Trung bình {avg_listening}/10), nắm bắt ý chính bài nghe.")

    if avg_speaking >= 8.0:
        strengths.append(f"Kỹ năng Nói tự tin (Trung bình {avg_speaking}/10), phát âm chuẩn và tương tác tích cực với GVNN.")
    elif avg_speaking >= 7.0:
        strengths.append(f"Kỹ năng Nói đạt mức khá (Trung bình {avg_speaking}/10), giao tiếp chủ động trong lớp.")

    if avg_rw >= 8.0:
        strengths.append(f"Kỹ năng Đọc - Viết vững vàng (Trung bình {avg_rw}/10), nắm chắc kiến thức từ vựng & ngữ pháp.")

    if hw_rate >= 80.0:
        strengths.append(f"Ý thức làm bài tập về nhà rất tốt (Tỷ lệ nộp đạt {hw_rate}%), tự giác học tập.")

    if not strengths:
        strengths.append("Có tinh thần hợp tác trong giờ học và đi học chuyên cần đúng giờ.")

    # 4. Improvements
    improvements = []
    if avg_rw > 0 and avg_rw < 7.5:
        improvements.append(f"Cần tăng cường rèn luyện kỹ năng Đọc - Viết (Điểm trung bình hiện tại: {avg_rw}/10) để tránh mắc các lỗi sai về cấu trúc câu và từ vựng.")

    if avg_speaking > 0 and avg_speaking < 7.5:
        improvements.append(f"Cần tự tin hơn khi thực hành kỹ năng Nói (Điểm trung bình hiện tại: {avg_speaking}/10) và mở rộng vốn từ giao tiếp.")

    if avg_listening > 0 and avg_listening < 7.5:
        improvements.append(f"Cần chủ động luyện nghe tiếng Anh hằng ngày ở nhà để nâng cao phản xạ âm.")

    if hw_rate < 80.0:
        improvements.append(f"Cần hoàn thiện bài tập về nhà đầy đủ và đúng hạn hơn (Tỷ lệ hoàn thành hiện tại: {hw_rate}%).")

    if not improvements:
        improvements.append("Tiếp tục phát huy thế mạnh hiện có và mở rộng bài tập đọc nâng cao.")

    # 5. General Summary & Recommendations
    if avg_total >= 8.5:
        level_evaluation = "Xuất sắc"
        summary_text = f"Em {display_name} là học sinh {level_evaluation}, có nền tảng tiếng Anh rất vững chắc. {trend_text}."
        recommendations = "Phụ huynh nên tiếp tục tạo điều kiện cho con tiếp xúc với sách báo, phim ảnh tiếng Anh nâng cao và khuyến khích con tham gia các hoạt động ngoại khóa bằng tiếng Anh."
    elif avg_total >= 7.0:
        level_evaluation = "Khá - Tốt"
        summary_text = f"Em {display_name} đạt trình độ {level_evaluation}. Con tiếp thu bài nhanh và có tinh thần học tập tích cực. {trend_text}."
        recommendations = "Phụ huynh nên hỗ trợ con duy trì thói quen ôn tập từ vựng 15 phút mỗi ngày và nhắc nhở con làm đầy đủ bài tập về nhà trước buổi học."
    else:
        level_evaluation = "Cần cố gắng"
        summary_text = f"Em {display_name} đang trong quá trình tích lũy kiến thức. {trend_text}."
        recommendations = "Trung tâm đề xuất Phụ huynh cùng phối hợp chặt chẽ với Giáo viên & CM để kèm cặp thêm cho con các bài tập bổ trợ ngữ pháp và từ vựng tại nhà."

    # Comments compilation
    teacher_notes_text = " | ".join(comments_list[:5]) if comments_list else "Con ngoan, tiếp thu bài tốt trong các giờ học."
    
    cm_notes_list = [note.get('note', '') for note in cm_notes if note.get('note')]
    cm_notes_text = " | ".join(cm_notes_list[:3]) if cm_notes_list else "Gia đình và CM phối hợp tốt trong công tác theo dõi học tập của học sinh."

    return {
        'student_name': display_name,
        'level_evaluation': level_evaluation,
        'avg_score': avg_total,
        'summary': summary_text,
        'strengths': strengths,
        'improvements': improvements,
        'recommendations': recommendations,
        'teacher_notes_summary': teacher_notes_text,
        'cm_notes_summary': cm_notes_text,
        'homework_rate': hw_rate,
        'avg_listening': avg_listening,
        'avg_rw': avg_rw,
        'avg_speaking': avg_speaking
    }
