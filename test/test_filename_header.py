import urllib.parse

def clean_filename(text):
    import re
    import unicodedata
    # Convert Vietnamese accented string to ASCII / unaccented for filename
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = text.replace('đ', 'd').replace('Đ', 'D')
    text = re.sub(r'[^a-zA-Z0-9_\-]', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text

print("EVI056 name clean:", clean_filename("Nguyễn Ngọc Huyền"))
