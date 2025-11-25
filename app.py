import streamlit as st
from PIL import Image, ImageEnhance, ImageDraw, ImageOps, ImageFilter, ImageFont
from rembg import remove
import io

# --- Helper Functions ---
def convert_image(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

def make_rounded_icon(image, size=(512, 512), radius=0):
    image = image.resize(size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    if radius == 0: return image
    elif radius >= size[0] // 2: draw.ellipse((0, 0) + size, fill=255)
    else: draw.rounded_rectangle((0, 0) + size, radius=radius, fill=255)
    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

# --- Sidebar Menu ---
st.sidebar.title("🎨 Studio Foto AI (Web Version)")
menu = st.sidebar.radio("Pilih Fitur:", ("Hapus Background", "Restorasi Foto", "Gabung Foto", "Icon Maker", "Watermark", "Filter"))

# --- LOGIKA APLIKASI ---

if menu == "Hapus Background":
    st.header("✂️ Hapus Background")
    u = st.file_uploader("Upload Foto", type=["jpg", "png", "jpeg"])
    if u:
        image = Image.open(u)
        st.image(image, caption="Asli", width=300)
        if st.button("Proses Hapus Background"):
            with st.spinner('Proses AI berjalan... (Mungkin 1-2 menit untuk unduh model pertama kali)'):
                try:
                    res = remove(image)
                    st.image(res, caption="Hasil")
                    st.download_button("Download", convert_image(res), "no_bg.png", "image/png")
                except Exception as e: 
                    st.error(f"Gagal memproses. Error: {e}")

elif menu == "Restorasi Foto":
    st.header("✨ Restorasi Simpel")
    u = st.file_uploader("Upload", type=["jpg","png"])
    if u:
        img = Image.open(u)
        st.image(img, width=300)
        s = st.slider("Tajam", 1.0, 3.0, 1.5)
        c = st.slider("Kontras", 1.0, 2.0, 1.2)
        res = ImageEnhance.Sharpness(img).enhance(s)
        res = ImageEnhance.Contrast(res).enhance(c)
        st.image(res)
        st.download_button("Download", convert_image(res), "restorasi.png", "image/png")

elif menu == "Gabung Foto":
    st.header("🖼️ Gabung Foto")
    us = st.file_uploader("Upload Banyak Foto", accept_multiple_files=True)
    if us and st.button("Gabung"):
        imgs = [Image.open(x) for x in us]
        if imgs:
            min_h = min(i.height for i in imgs)
            rz = [i.resize((int(i.width*min_h/i.height), min_h)) for i in imgs]
            w = sum(i.width for i in rz)
            new = Image.new('RGB', (w, min_h))
            x=0
            for i in rz: new.paste(i, (x,0)); x+=i.width
            st.image(new); st.download_button("Download", convert_image(new), "gabung.png")

elif menu == "Icon Maker":
    st.header("📱 Icon Maker")
    u = st.file_uploader("Upload")
    if u:
        im = Image.open(u)
        s = st.radio("Style", ["Kotak", "Bulat", "Rounded"])
        r=0
        if s=="Bulat": r=256
        elif s=="Rounded": r=80
        res = make_rounded_icon(im, radius=r)
        st.image(res); st.download_button("Download", convert_image(res), "icon.png")

elif menu == "Watermark":
    st.header("🔤 Watermark")
    u = st.file_uploader("Upload")
    if u:
        im = Image.open(u).convert("RGBA")
        txt = st.text_input("Teks", "Watermark")
        op = st.slider("Transparansi", 0, 255, 128)
        
        txt_lyr = Image.new("RGBA", im.size, (255,255,255,0))
        d = ImageDraw.Draw(txt_lyr)
        
        # PERBAIKAN: Memuat font default secara eksplisit
        try:
            # Gunakan ImageFont.load_default() yang aman
            font = ImageFont.load_default()
        except Exception:
            # Fallback jika ImageFont.load_default() gagal
            font = None
            
        d.text((20,20), txt, font=font, fill=(255,255,255,op))
        res = Image.alpha_composite(im, txt_lyr)
        st.image(res); st.download_button("Download", convert_image(res), "watermark.png")
        
elif menu == "Filter":
    st.header("Filter")
    u = st.file_uploader("Upload")
    if u:
        im = Image.open(u)
        f = st.selectbox("Pilih", ["Grayscale", "Blur"])
        if f=="Grayscale": im=im.convert("L")
        elif f=="Blur": im=im.filter(ImageFilter.GaussianBlur(2))

        st.image(im); st.download_button("Download", convert_image(im), "edit.png")
