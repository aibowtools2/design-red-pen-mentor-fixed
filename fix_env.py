
import os

file_path = "backend/.env"
if not os.path.exists(file_path):
    file_path = ".env"

try:
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Remove null bytes (common artifact of UTF-16 vs UTF-8 mixup in PowerShell)
    fixed_content = content.replace(b'\x00', b'')
    
    # Try to decode to ensure it's text
    try:
        text_content = fixed_content.decode('utf-8')
    except UnicodeDecodeError:
        text_content = fixed_content.decode('utf-16', errors='ignore')
        
    print(f"Original Text Length: {len(content)}")
    print(f"Fixed Text Length: {len(text_content)}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
        
    print("Successfully fixed .env encoding.")
    
except Exception as e:
    print(f"Error fixing .env: {e}")
