
import os

file_path = "backend/.env"
if not os.path.exists(file_path):
    file_path = ".env"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace placeholder with actual password
    new_content = content.replace("[YOUR-PASSWORD]", "Boxllc12313f9lfxlz")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Successfully updated password in .env")
    
except Exception as e:
    print(f"Error updating .env: {e}")
