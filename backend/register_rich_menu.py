import os
import requests
import json

def get_token_manually():
    path = ".env"
    if not os.path.exists(path):
        path = "backend/.env"
    if not os.path.exists(path):
        return None
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "LINE_CHANNEL_ACCESS_TOKEN" in line and "=" in line:
                val = line.split("=", 1)[1].strip().strip("'\"")
                return val
    return None

ACCESS_TOKEN = get_token_manually()
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def cleanup_old_menus():
    res = requests.get("https://api.line.me/v2/bot/richmenu/list", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    menus = res.json().get("richmenus", [])
    for m in menus:
        mid = m.get("richMenuId")
        requests.delete(f"https://api.line.me/v2/bot/richmenu/{mid}", headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    print(f"Cleaned up {len(menus)} old menus.")

def create_rich_menu():
    if not ACCESS_TOKEN:
        print("Error: LINE_CHANNEL_ACCESS_TOKEN not set.")
        return

    cleanup_old_menus()

    # 1. Define Rich Menu Structure
    # Compact Size: 2500x843
    rich_menu_data = {
        "size": {"width": 2500, "height": 843},
        "selected": True,
        "name": "NaruhodoDesign_2Button_Menu",
        "chatBarText": "メニューを開く",
        "areas": [
            {
                "bounds": {"x": 0, "y": 0, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "使い方を見る"}
            },
            {
                "bounds": {"x": 1250, "y": 0, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "無制限プランに参加"}
            }
        ]
    }

    # Create Menu
    res = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers=HEADERS,
        data=json.dumps(rich_menu_data)
    )
    result = res.json()
    rich_menu_id = result.get("richMenuId")
    if not rich_menu_id:
        print(f"Failed to create rich menu: {result}")
        return

    print(f"Rich Menu Created: {rich_menu_id}")
    
    # 2. Upload Image (Compress to JPEG to meet 1MB limit)
    image_path = "rich_menu.png"
    jpg_path = "rich_menu.jpg"
    try:
        from PIL import Image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(jpg_path, "JPEG", quality=85, optimize=True)
        print(f"Image compressed to JPEG: {os.path.getsize(jpg_path)} bytes")
    except Exception as e:
        print(f"Compression failed: {e}")
        return

    with open(jpg_path, "rb") as f:
        res_img = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "image/jpeg"},
            data=f
        )
        print(f"Image Upload Status: {res_img.status_code}")

    # 3. Set as Default
    res_default = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=HEADERS
    )
    print(f"Set Default Status: {res_default.status_code}")
    print("Rich Menu registration completed successfully!")

if __name__ == "__main__":
    create_rich_menu()
