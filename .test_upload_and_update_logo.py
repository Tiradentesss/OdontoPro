import os
import sys
from dotenv import load_dotenv
load_dotenv()
ROOT = os.path.abspath(os.path.dirname(__file__))
SISTEMA_PATH = os.path.join(ROOT, "SistemaDesktop")
if SISTEMA_PATH not in sys.path:
    sys.path.insert(0, SISTEMA_PATH)

from services.cloudinary_service import upload_image_to_cloudinary
from config.database import get_connection
from PIL import Image
import tempfile
import time

try:
    # create a small temp image
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, f"test_logo_{int(time.time())}.png")
    img = Image.new('RGB', (120, 120), color=(73, 109, 137))
    img.save(tmp_path)

    print(f"[TEST] Temp image created at: {tmp_path}")

    public_id = f"clinica_1_test_{int(time.time())}"
    folder = "odontopro/clinicas/1"
    print("[TEST] Uploading to Cloudinary...")
    secure_url = upload_image_to_cloudinary(tmp_path, public_id=public_id, folder=folder)
    print(f"[TEST] Upload returned secure_url: {secure_url}")

    if not (secure_url and secure_url.startswith('https://')):
        print('[TEST] Upload did not return a valid HTTPS URL; aborting DB update.')
        sys.exit(1)

    # Update DB for clinica_id=1
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, logo FROM odontoPro_clinica WHERE id = %s", (1,))
    before = cursor.fetchone()
    print('[TEST] Before update:', before)

    cursor.execute("UPDATE odontoPro_clinica SET logo = %s WHERE id = %s", (secure_url, 1))
    conn.commit()

    cursor.execute("SELECT id, nome, logo FROM odontoPro_clinica WHERE id = %s", (1,))
    after = cursor.fetchone()
    print('[TEST] After update:', after)

    print('[TEST] Cleaning up: removing temp file')
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    print('[TEST] Done')

except Exception as e:
    print('[ERROR]', e)
    sys.exit(1)
