import os
import time
import hashlib
import requests
from urllib.parse import urlparse


def get_cloudinary_config():
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not (cloud_name and api_key and api_secret):
        cloudinary_url = os.getenv("CLOUDINARY_URL", "").strip()
        if cloudinary_url.startswith("cloudinary://"):
            parsed = urlparse(cloudinary_url)
            cloud_name = parsed.hostname
            api_key = parsed.username
            api_secret = parsed.password

    if cloud_name and api_key and api_secret:
        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret,
        }
    return None


def upload_image_to_cloudinary(file_path, public_id=None, folder=None):
    config = get_cloudinary_config()
    if config is None:
        raise RuntimeError("Configuração Cloudinary não encontrada. Verifique CLOUDINARY_URL ou as variáveis CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY e CLOUDINARY_API_SECRET.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {file_path}")

    cloud_name = config["cloud_name"]
    api_key = config["api_key"]
    api_secret = config["api_secret"]
    timestamp = int(time.time())

    data = {
        "timestamp": timestamp,
    }
    if folder:
        data["folder"] = folder
    if public_id:
        data["public_id"] = public_id

    signed_items = [(k, data[k]) for k in sorted(data) if data[k] is not None]
    signature_base = "&".join(f"{k}={v}" for k, v in signed_items)
    signature = hashlib.sha1((signature_base + api_secret).encode("utf-8")).hexdigest()

    data["api_key"] = api_key
    data["signature"] = signature
    endpoint = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"

    with open(file_path, "rb") as file_obj:
        files = {"file": file_obj}
        response = requests.post(endpoint, data=data, files=files, timeout=60)

    response.raise_for_status()
    result = response.json()
    if "secure_url" not in result:
        raise RuntimeError(f"Upload Cloudinary falhou: {result}")

    return result["secure_url"]
