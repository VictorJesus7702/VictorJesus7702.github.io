import os
import random
import shutil
from datetime import datetime
import subprocess

# CONFIG
source_root = r'D:\YTC\YTC_Daily_Final\Shorts'
media_dir = 'media'
index_file = 'index.html'
backup_file = 'index_backup.html'

# Ensure media directory exists
os.makedirs(media_dir, exist_ok=True)

# 0️⃣ Git identity check
def ensure_git_identity():
    try:
        name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
        email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
    except subprocess.CalledProcessError:
        name, email = "", ""

    if not name:
        subprocess.run(["git", "config", "--global", "user.name", "VictorJesus7702"])
    if not email:
        subprocess.run(["git", "config", "--global", "user.email", "unveiljesus5170@gmail.com "])  # ← Change to your email

ensure_git_identity()

# 1️⃣ Git add & commit current changes before pulling
subprocess.run(["git", "add", "."])
try:
    subprocess.run(["git", "commit", "-m", "Auto-save before update"], check=True)
except subprocess.CalledProcessError:
    print("ℹ️ No changes to commit before pull.")

# 2️⃣ Pull latest with rebase
subprocess.run(["git", "pull", "origin", "main", "--rebase"])

# Today's date formats
today_dt = datetime.now()
folder_name = today_dt.strftime('%b_%d_%Y')   # e.g. Aug_07_2025
today_folder = os.path.join(source_root, folder_name)
today_str = today_dt.strftime('%Y-%m-%d')

video1_name = f'video1_{today_str}.mp4'
video2_name = f'video2_{today_str}.mp4'
video1_path = os.path.join(media_dir, video1_name)
video2_path = os.path.join(media_dir, video2_name)

# 3️⃣ Find today's 2 random .mp4 files
video_files = []
if os.path.exists(today_folder):
    video_files = [f for f in os.listdir(today_folder) if f.lower().endswith('.mp4')]
    random.shuffle(video_files)
    video_files = video_files[:2]

# 4️⃣ Use today's videos or reuse last available ones
if len(video_files) == 2:
    print("✅ Found today's 2 videos. Copying to media/ and using them.")
    shutil.copy(os.path.join(today_folder, video_files[0]), video1_path)
    shutil.copy(os.path.join(today_folder, video_files[1]), video2_path)
    use_video1 = video1_path
    use_video2 = video2_path
else:
    print("⚠️ Today's videos not found. Reusing last available videos in media/.")
    media_videos = sorted(
        [os.path.join(media_dir, f) for f in os.listdir(media_dir)
         if f.startswith('video') and f.endswith('.mp4')],
        key=os.path.getmtime,
        reverse=True
    )
    if len(media_videos) >= 2:
        use_video1 = media_videos[0]
        use_video2 = media_videos[1]
    else:
        raise FileNotFoundError("❌ No videos found in media/ to reuse!")

# 5️⃣ Backup original index.html
shutil.copy(index_file, backup_file)

# 6️⃣ Update index.html video tags
with open(backup_file, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace(
    '<img src="Psalms23-3.png" alt="Psalm 23:3">',
    f'<video src="{use_video1}" autoplay muted loop playsinline width="100%" style="border-radius:10px;"></video>'
)

html = html.replace(
    '<img src="Psalms24-1.png" alt="Psalm 24:1">',
    f'<video src="{use_video2}" autoplay muted loop playsinline width="100%" style="border-radius:10px;"></video>'
)

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ index.html updated.")

# 7️⃣ Delete old dated videos
for file in os.listdir(media_dir):
    full_path = os.path.join(media_dir, file)
    if (
        file.startswith('video') and file.endswith('.mp4') and
        today_str not in file and
        full_path not in (use_video1, use_video2)
    ):
        print(f"🗑️ Deleting old video: {file}")
        os.remove(full_path)

# 8️⃣ Final commit & push
subprocess.run(["git", "add", "index.html", "media/"])
try:
    subprocess.run(["git", "commit", "-m", f"Auto-update video content for {today_str}"], check=True)
except subprocess.CalledProcessError:
    print("ℹ️ No new changes to commit after update.")

subprocess.run(["git", "push", "origin", "main"])

print("✅ All done.")
