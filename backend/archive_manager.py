import os
import shutil
import datetime
import argparse

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Desktop/なるほどデザイン
ARCHIVE_ROOT = os.path.join(BASE_DIR, "archives")

def archive_article(article_id, article_path, original_path, evaluation_path, thumbnail_path, social_posts=None):
    """
    Archives article assets into a date-stamped folder.
    """
    today = datetime.datetime.now().strftime("%Y%m%d")
    folder_name = f"{today}_{article_id}"
    target_dir = os.path.join(ARCHIVE_ROOT, folder_name)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created archive directory: {target_dir}")
    else:
        print(f"Directory exists, updating files: {target_dir}")

    # Copy files
    files_map = {
        "article.md": article_path,
        "original.png": original_path,
        "evaluation.png": evaluation_path,
        "thumbnail.png": thumbnail_path
    }

    for target_name, source_path in files_map.items():
        if source_path and os.path.exists(source_path):
            dest = os.path.join(target_dir, target_name)
            shutil.copy2(source_path, dest)
            print(f"Copied {os.path.basename(source_path)} -> {target_name}")
        else:
            print(f"Warning: Source file not found: {source_path}")

    if social_posts and os.path.exists(social_posts):
        shutil.copy2(social_posts, os.path.join(target_dir, "social_posts.md"))
        print(f"Copied {os.path.basename(social_posts)} -> social_posts.md")

    print(f"Archiving complete! Location: {target_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive Design Red Pen articles.")
    parser.add_argument("id", help="Article ID (e.g. portrait_02)")
    parser.add_argument("--article", help="Path to markdown article", required=True)
    parser.add_argument("--original", help="Path to original image", required=True)
    parser.add_argument("--eval", help="Path to evaluation OGP image", required=True)
    parser.add_argument("--thumb", help="Path to thumbnail image", required=True)
    parser.add_argument("--social", help="Path to social posts markdown", required=False) # Added

    args = parser.parse_args()
    
    archive_article(
        args.id,
        args.article,
        args.original,
        args.eval,
        args.thumb,
        social_posts=args.social # Added
    )
