import os
import sys

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from routes.api import _format_comment_html

def test_format_comment():
    sample_text = "**Đánh giá chung:**\nCon học rất ngoan.\n- Nắm vững từ vựng\n- Phản xạ nhanh\n*Cần phát huy thêm!*"
    formatted = _format_comment_html(sample_text)
    print("--- FORMATTED HTML OUTPUT ---")
    print(formatted)
    assert "<strong>Đánh giá chung:</strong>" in formatted
    assert "•" in formatted
    assert "<em>Cần phát huy thêm!</em>" in formatted
    assert "<br>" in formatted
    print("\n✅ All format assertions PASSED successfully!")

if __name__ == '__main__':
    test_format_comment()
