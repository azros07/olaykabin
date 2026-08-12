import os
import tempfile
import requests
import streamlit as st
from PIL import Image, ImageOps
from gradio_client import Client, handle_file

# Sayfa Tasarımı ve Diva Teması
st.set_page_config(
    page_title="DIVA | VIP OLAYKABIN",
    page_icon="👑",
    layout="wide"
)

# Custom CSS - Diva VIP Görünümü
st.markdown("""
    <style>
    .stButton>button {
        background: linear-gradient(45deg, #111111, #333333);
        color: #D4AF37;
        border: 1px solid #D4AF37;
        border-radius: 10px;
        height: 52px;
        font-weight: bold;
        font-size: 17px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #D4AF37, #FFDF00);
        color: #000000;
        border: 1px solid #000000;
    }
    </style>
""", unsafe_allow_html=True)

st.title("👑 DIVALARA ÖZEL | VIP OLAYKABIN")
st.caption("✨ HD Kalitede Yüz Koruma Teknolojisi & Divalara Özel Mağaza Yönlendirmeli Sanal Kabin")

# Yönlü Resim Düzeltme Fonksiyonu
def fix_image_orientation(img_input):
    """Telefondan çekilen görsellerin yan/ters dönmesini engeller."""
    if isinstance(img_input, str):
        img = Image.open(img_input)
    else:
        img = Image.open(img_input)
    
    img = ImageOps.exif_transpose(img)
    return img

# Yan Menü: Bilgilendirme
with st.sidebar:
    st.header("⚙️ Diva VIP Sistem Ayarları")
    st.info("💋 Diva Tüyosu: Kusursuz sonuç için fotoğrafının düz, net ve ışık altında çekilmiş olması gerekir.")

# Sekme Yapısı: Hazır Katalog vs Kendi Yükleyeceğin
tab1, tab2 = st.tabs(["💅 DIVA MAĞAZA KATALOĞU", "📤 KENDİ KIYAFETİNİ YÜKLE"])

with tab1:
    st.subheader("Favori Tarzını Seç & Üzerinde Dene Diva!")
    
    catalog = [
        {
            "title": "Mavi Gece Elbisesi",
            "img": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=500",
            "zara_link": "https://www.zara.com/tr/tr/search?searchTerm=mavi%20elbise",
            "mavi_link": "https://www.mavi.com/search/?text=mavi+elbise",
            "trendyol_link": "https://www.trendyol.com/sr?q=mavi+elbise"
        },
        {
            "title": "Beyaz Poplin Gömlek",
            "img": "https://images.unsplash.com/photo-1598554747436-c9293d6a588f?w=500",
            "zara_link": "https://www.zara.com/tr/tr/search?searchTerm=beyaz%20gomlek",
            "mavi_link": "https://www.mavi.com/search/?text=beyaz+gomlek",
            "trendyol_link": "https://www.trendyol.com/sr?q=beyaz+gomlek"
        },
        {
            "title": "Siyah Deri Ceket",
            "img": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500",
            "zara_link": "https://www.zara.com/tr/tr/search?searchTerm=deri%20ceket",
            "mavi_link": "https://www.mavi.com/search/?text=deri+ceket",
            "trendyol_link": "https://www.trendyol.com/sr?q=deri+ceket"
        },
        {
            "title": "Kırmızı Çiçekli Elbise",
            "img": "https://images.unsplash.com/photo-1612423284934-2850a4ea6b0f?w=500",
            "zara_link": "https://www.zara.com/tr/tr/search?searchTerm=kırmızı%20elbise",
            "mavi_link": "https://www.mavi.com/search/?text=kirmizi+elbise",
            "trendyol_link": "https://www.trendyol.com/sr?q=kirmizi+elbise"
        }
    ]

    cols = st.columns(4)
    for idx, item in enumerate(catalog):
        with cols[idx % 4]:
            st.image(item["img"])
            st.write(f"*{item['title']}*")
            if st.button(f"Bu Kıyafeti Seç", key=f"btn_{idx}"):
                st.session_state["selected_garment"] = item["img"]
                st.session_state["selected_item"] = item
                st.success(f"{item['title']} Seçildi!")

with tab2:
    uploaded_garment = st.file_uploader("İnternetten indirdiğin kıyafet görselini yükle", type=["jpg", "png", "jpeg"])

st.divider()

# Model Fotoğrafı Yükleme Alanı
col_user, col_preview = st.columns(2)

with col_user:
    st.subheader("1. Kendi Fotoğrafını Yükle")
    human_file = st.file_uploader("Düz duvar önünde çekilmiş boydan/üst beden fotoğrafın", type=["jpg", "png", "jpeg"])
    if human_file:
        st.image(human_file, caption="Model Diva (Sen)", width=250)

with col_preview:
    st.subheader("2. Denenecek Kıyafet Önizleme")
    garment_to_use = None
    
    if uploaded_garment:
        garment_to_use = uploaded_garment
        st.image(uploaded_garment, caption="Yüklediğin Kıyafet", width=250)
    elif "selected_garment" in st.session_state:
        garment_to_use = st.session_state["selected_garment"]
        st.image(garment_to_use, caption="Katalogdan Seçilen Kıyafet", width=250)

# İşlem Butonu
if st.button("✨ KUSURSUZ GİYDİR VE BENZERLERİNİ BUL", use_container_width=True):
    if not human_file or not garment_to_use:
        st.error("Lütfen hem kendi fotoğrafını yükle hem de bir kıyafet seç Diva!")
    else:
        with st.spinner("💋 HD Kalitede işleniyor... Yüzün korunuyor ve kıyafet üzerine oturtuluyor..."):
            human_path = None
            garment_path = None
            try:
                # 1. Kendi fotoğrafını yön düzeltmesiyle kaydet
                user_img_pil = fix_image_orientation(human_file)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f1:
                    user_img_pil.save(f1.name)
                    human_path = f1.name

                # 2. Kıyafet fotoğrafını yön düzeltmesiyle kaydet
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f2:
                    if isinstance(garment_to_use, str):
                        garment_pil = Image.open(requests.get(garment_to_use, stream=True).raw)
                    else:
                        garment_pil = Image.open(garment_to_use)
                    
                    garment_pil = ImageOps.exif_transpose(garment_pil)
                    garment_pil.save(f2.name)
                    garment_path = f2.name

                # 3. Gradio IDM-VTON Modeline İstem Gönderimi (HF Token Desteğiyle)
                hf_token = os.getenv("HF_TOKEN", None)
                client_kwargs = {}
                if hf_token:
                    client_kwargs["token"] = hf_token

                client = Client("yisol/IDM-VTON", **client_kwargs)

                result = client.predict(
                    dict={
                        "background": handle_file(human_path),
                        "layers": [],
                        "composite": handle_file(human_path)
                    },
                    garm_img=handle_file(garment_path),
                    garment_des="clothing",
                    is_checked=True,
                    is_checked_crop=False,
                    denoise_steps=30,
                    seed=42,
                    api_name="/tryon"
                )

                st.success("🎉 Podyum Seni Bekliyor Diva! Harika Görünüyorsun!")
                
                # Çıkan sonucun yönünü de garanti düzelt
                res_img = fix_image_orientation(result[0])
                st.image(res_img, caption="DIVA VIP OLAYKABIN SONUÇ")

                # Mağaza Yönlendirme Alanı
                st.divider()
                st.subheader("🛍️ Bu Tarzı Beğendin mi? Mağazalarda Doğrudan İncele:")
                
                if "selected_item" in st.session_state:
                    item = st.session_state["selected_item"]
                    col_b1, col_b2, col_b3 = st.columns(3)
                    with col_b1:
                        st.link_button("Zara'da Benzerleri Gör ➔", item["zara_link"])
                    with col_b2:
                        st.link_button("Mavi'de Benzerleri Gör ➔", item["mavi_link"])
                    with col_b3:
                        st.link_button("Trendyol'da Benzerleri Gör ➔", item["trendyol_link"])
                else:
                    col_b1, col_b2, col_b3 = st.columns(3)
                    with col_b1:
                        st.link_button("Zara'da Benzer Ürünleri Ara ➔", "https://www.zara.com/tr/")
                    with col_b2:
                        st.link_button("Mavi'de Benzer Ürünleri Ara ➔", "https://www.mavi.com/")
                    with col_b3:
                        st.link_button("Trendyol'da Ara ➔", "https://www.trendyol.com/")

            except Exception as e:
                st.error("Yapay zekâ sunucusu şu an yoğun Diva, lütfen birkaç saniye sonra tekrar dene!")
                st.caption(f"Hata detayı: {e}")
            finally:
                if human_path and os.path.exists(human_path):
                    os.remove(human_path)
                if garment_path and os.path.exists(garment_path):
                    os.remove(garment_path)
