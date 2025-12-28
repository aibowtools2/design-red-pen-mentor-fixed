import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from gemini_client import analyze_image_design
import json
import os

WATCHED_DIR = "../watched_videos" # Keeping same dir for simplicity, but user should put images here
DATA_FILE = "data.json"

class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Check for images
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            return

        print(f"New image detected: {filename}")
        self.process_image(filepath)

    def process_image(self, filepath):
        print(f"Processing {filepath}...")
        
        # 1. Analyze Design (Tensaku + Google Data)
        result_json_str = analyze_image_design(filepath)
        
        # Parse JSON to ensure validity
        try:
            data = json.loads(result_json_str)
            # Add timestamp or filename if needed
            data["source_image"] = os.path.basename(filepath)
            
            # Save to history
            timestamp = int(time.time())
            history_file = f"analysis_{timestamp}.json"
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # Update main data.json for Frontend
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"Analysis saved to {DATA_FILE}")
            
        except json.JSONDecodeError:
            print("Failed to decode JSON from Gemini response.")
            print(result_json_str)
        except Exception as e:
            print(f"Error saving data: {e}")

def scan_existing_files(handler):
    print("Scanning for existing images...")
    if not os.path.exists(WATCHED_DIR):
        os.makedirs(WATCHED_DIR)
        return
    
    for filename in os.listdir(WATCHED_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
             filepath = os.path.join(WATCHED_DIR, filename)
             print(f"Found existing: {filepath}")
             # Optional: Process existing?
             # handler.process_image(filepath) 
             pass

def start_watching():
    # Scan first
    event_handler = VideoHandler()
    scan_existing_files(event_handler)
        
    observer = Observer()
    observer.schedule(event_handler, path=WATCHED_DIR, recursive=False)
    observer.start()
    print(f"Monitoring {WATCHED_DIR} for images...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
