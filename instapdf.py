"""Instagram postundaki tüm görselleri tek bir PDF'e çevirir (her görsel = 1 sayfa).

Kullanım:
    python instapdf.py <post_linki> [-o cikti.pdf] [--login kullanici_adi]
Arayüz için: instapdf_gui.pyw (veya InstaPDF.bat)

--login: Instagram login istiyorsa, önce kendi terminalinde
    instaloader --login kullanici_adi
çalıştırıp oturumu kaydet; sonra script'e --login kullanici_adi ver.
"""
import argparse
import io
import re
import sys
import urllib.request
from pathlib import Path

import img2pdf
import instaloader
from PIL import Image

OUT_DIR = Path(__file__).parent / "pdfs"


class InstaPdfError(Exception):
    pass


def shortcode_from_url(url: str) -> str:
    m = re.search(r"instagram\.com/(?:[^/]+/)?(?:p|reel|tv)/([A-Za-z0-9_-]+)", url)
    if not m:
        raise InstaPdfError(f"Geçersiz Instagram post linki: {url}")
    return m.group(1)


def image_urls(post: instaloader.Post) -> list[str]:
    if post.typename == "GraphSidecar":
        return [n.display_url for n in post.get_sidecar_nodes() if not n.is_video]
    if post.is_video:
        return []
    return [post.url]


def fetch_jpeg(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    img = Image.open(io.BytesIO(data))
    if img.format == "JPEG" and img.mode == "RGB":
        return data
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=95)
    return buf.getvalue()


def make_pdf(url: str, output: str | None = None, login: str | None = None, progress=print) -> Path:
    """Postu indirip PDF yapar. progress(mesaj) ile ilerleme bildirir; PDF yolunu döner."""
    shortcode = shortcode_from_url(url)
    L = instaloader.Instaloader(quiet=True)
    if login:
        try:
            L.load_session_from_file(login)
        except FileNotFoundError:
            raise InstaPdfError(f"Oturum bulunamadı. Önce terminalde çalıştır: instaloader --login {login}")

    progress("Post bilgisi alınıyor...")
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        urls = image_urls(post)
    except instaloader.exceptions.InstaloaderException as e:
        raise InstaPdfError(
            f"Post alınamadı: {e}\n"
            "Post gizli olabilir ya da Instagram login istiyor. "
            "'instaloader --login KULLANICI' ile oturum açıp tekrar dene."
        )
    if not urls:
        raise InstaPdfError("Bu postta görsel bulunamadı (sadece video olabilir).")

    progress(f"{post.owner_username} / {shortcode}: {len(urls)} görsel indiriliyor...")
    pages = []
    for i, u in enumerate(urls, 1):
        pages.append(fetch_jpeg(u))
        progress(f"  {i}/{len(urls)}")

    out = Path(output) if output else OUT_DIR / f"{post.owner_username}_{shortcode}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img2pdf.convert(pages))
    progress(f"PDF hazır ({len(pages)} sayfa): {out.resolve()}")
    return out.resolve()


def main() -> None:
    ap = argparse.ArgumentParser(description="Instagram postu -> PDF")
    ap.add_argument("url")
    ap.add_argument("-o", "--output")
    ap.add_argument("--login", help="instaloader ile kaydedilmiş oturumun kullanıcı adı")
    args = ap.parse_args()
    try:
        make_pdf(args.url, args.output, args.login)
    except InstaPdfError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
