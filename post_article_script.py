import asyncio
import argparse
import os
import sys
from playwright.async_api import async_playwright

# Add backend to path to import archive_manager
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
try:
    from archive_manager import archive_article
except ImportError:
    print("Warning: Could not import archive_manager. Archiving will be disabled.")
    archive_article = None

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
IMAGES_DIR = os.path.join(ARTICLES_DIR, "images") # Assumed structure

async def post_to_note(article_path, title, body, header_image_path=None, headless=False):
    """
    Automates the posting process to Note.com
    """
    async with async_playwright() as p:
        # Launch browser (non-headless by default for login visibility)
        browser = await p.chromium.launch(channel="chrome", headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("Accessing Note.com login page...")
            await page.goto("https://note.com/login")
            
            # Check if already logged in or needs login
            if "login" in page.url:
                print("【Action Required】 Please log in to Note.com in the opened browser.")
                print("After logging in, press Enter here to continue...")
                input()
            
            print("Navigating to new note page...")
            await page.goto("https://note.com/notes/new")
            
            # Rate limit / Page load wait
            await page.wait_for_timeout(2000)

            print(f"Drafting: {title}")
            
            # Title
            await page.fill('textarea[placeholder="記事タイトル"]', title)
            
            # Body
            await page.click('.editor-content')
            await page.keyboard.type(body)
            
            # Header Image (if provided and implemented in Note content)
            # Note: Header image upload selector might vary. 
            # For now, we'll just log it as a manual step if automation is complex/unstable
            if header_image_path and os.path.exists(header_image_path):
                 print(f"Header image found at {header_image_path}. Please upload it manually for now (Automation WIP).")
                 # await page.set_input_files('input[type="file"]', header_image_path) # Example
            
            print("Draft created successfully!")
            print("Please review the draft in the browser.")
            print("Press Enter to close the browser (or Ctrl+C to keep it open if you want to publish manually now).")
            input()

        except Exception as e:
            print(f"Error during browser automation: {e}")
        finally:
            await browser.close()

def main():
    parser = argparse.ArgumentParser(description="Post article to Note.com and optionally archive assets.")
    parser.add_argument("--id", required=True, help="Article ID (e.g., 10_portfolio)")
    parser.add_argument("--archive", action="store_true", help="Archive assets before posting")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--image-dir", default=IMAGES_DIR, help="Directory containing images")
    parser.add_argument("--dry-run", action="store_true", help="Simulate process without browser automation")
    
    args = parser.parse_args()
    
    # 1. Resolve Paths
    # Try exact match first, then formatted
    article_filename = args.id if args.id.endswith(".md") else f"{args.id}.md"
    article_path = os.path.join(ARTICLES_DIR, article_filename)
    
    if not os.path.exists(article_path):
        print(f"Error: Article file not found at {article_path}")
        return

    # Image Paths (Best guess based on conventions)
    # Assuming images are named like the article ID or standard names in a subfolder
    # User can adjust this logic or move files to match
    original_path = os.path.join(args.image_dir, f"{args.id}_original.png")
    eval_path = os.path.join(args.image_dir, f"{args.id}_evaluation.png")
    thumb_path = os.path.join(args.image_dir, f"{args.id}_thumbnail.png")
    
    # Fallback to generic names if specific ID names don't exist? 
    # Or just warn. For now, let's warn.
    
    # 2. Archiving
    if args.archive:
        if archive_article:
            print("Starting archive process...")
            # We pass what we found. If files are missing, archive_manager warns but proceeds.
            archive_article(
                article_id=args.id.replace(".md", ""),
                article_path=article_path,
                original_path=original_path,
                evaluation_path=eval_path,
                thumbnail_path=thumb_path
            )
        else:
            print("Archive manager not loaded. Skipping archive.")
            
    # 3. Read Content
    print(f"Reading article: {article_path}")
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")
        # Extract title (first line usually)
        title = lines[0].replace("# ", "").replace("*", "").strip()
        # Body is the rest
        body = "\n".join(lines[1:])

    # 4. Post
    # Determine header image (Thumbnail is usually the header)
    header_image = thumb_path if os.path.exists(thumb_path) else None
    
    if args.dry_run:
        print("[Dry Run] Skipping browser automation.")
        print(f"[Dry Run] Would post article: '{title}'")
        print(f"[Dry Run] Body length: {len(body)} chars")
        if header_image:
            print(f"[Dry Run] With header image: {header_image}")
        return

    asyncio.run(post_to_note(article_path, title, body, header_image, args.headless))

if __name__ == "__main__":
    main()
