# InstaPDF

Instagram'daki çok görselli (carousel) postları tek bir PDF'e çevirir — her görsel bir sayfa, tam çözünürlükte. Ders notu paylaşılan postları kaydetmek için yapıldı.

## Kurulum

Python 3.10+ gerekir.

```bash
pip install -r requirements.txt
```

## Kullanım

**Arayüz:** `InstaPDF.bat` dosyasına çift tıkla (veya `pythonw instapdf_gui.pyw`).
Post linkini kopyala, uygulama açılınca otomatik yapıştırır; **PDF Yap**'a bas. PDF'ler `pdfs/` klasörüne kaydedilir.

**Komut satırı:**

```bash
python instapdf.py "https://www.instagram.com/p/XXXXXXX/"
python instapdf.py "<link>" -o notlar.pdf
```

## Instagram giriş isterse

Public postlar genelde girişsiz iner. Engellenirse bir kez oturum aç:

```bash
instaloader --login KULLANICI_ADIN
```

Sonra arayüzde "Oturum" kutusuna kullanıcı adını yaz (komut satırında `--login KULLANICI_ADIN`).

## Not

Sadece kişisel kullanım için. İndirdiğin içeriklerin hakları paylaşan hesaba aittir.
