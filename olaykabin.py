import os
import gradio as gr
from gradio_client import Client, handle_file
from PIL import Image, ImageOps

# Hugging Face Token (Varsa ortam değişkeninden alır, yoksa None geçer)
HF_TOKEN = os.getenv("HF_TOKEN", None)

def fotograﬁ_duzelt(image_path):
    """Telefondan yüklenen görsellerin yan/ters dönmesini engeller."""
    if not image_path:
        return None
    try:
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)  # Kamera EXIF yön bilgisini düzeltir
        duzeltilmis_yol = "fixed_input.png"
        img.save(duzeltilmis_yol)
        return duzeltilmis_yol
    except Exception as e:
        print(f"Görsel düzeltme uyarısı: {e}")
        return image_path

def olaykabin_giydir(kullanici_fotosu, kiyafet_fotosu):
    if not kullanici_fotosu or not kiyafet_fotosu:
        return None, "Aşkım lütfen hem kendi fotoğrafını hem de giymek istediğin kıyafeti yükle! ✨"
    
    try:
        # 1. Görsellerin yönünü otomatik düzelt
        islenmis_user_img = fotograﬁ_duzelt(kullanici_fotosu)
        islenmis_garm_img = fotograﬁ_duzelt(kiyafet_fotosu)

        # 2. Sanal Kabin AI İstemcisi (Güncel token parametresi ile)
        client_kwargs = {}
        if HF_TOKEN:
            client_kwargs["token"] = HF_TOKEN

        client = Client("yisol/IDM-VTON", **client_kwargs)

        # 3. Model Tahmin İsteği
        result = client.predict(
            dict={"background": handle_file(islenmis_user_img), "layers": [], "composite": None},
            garm_img=handle_file(islenmis_garm_img),
            garment_des="Stylish outfit",
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=30,
            seed=42,
            api_name="/tryon"
        )

        # 4. Çıkan sonuç görselinin yönünü düzelt ve döndür
        if result and len(result) > 0:
            sonuc_yolu = result[0]
            sonuc_duzeltilmis = fotograﬁ_duzelt(sonuc_yolu)
            return sonuc_duzeltilmis, None
        else:
            return None, "Görsel oluşturulamadı, lütfen tekrar dene Diva!"

    except Exception as e:
        print(f"Sistem Detay Hatası: {str(e)}")
        error_msg = "Yapay zekâ sunucusu şu an yoğun Diva, lütfen birkaç saniye sonra tekrar dene!"
        return None, error_msg

# Custom CSS - Ekran görüntüsündeki tasarımla birebir uyumlu
custom_css = """
.yellow-btn {
    background-color: #FFD500 !important;
    color: #000000 !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
    font-size: 16px !important;
    border: none !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
}
.yellow-btn:hover {
    background-color: #E6C000 !important;
}
.error-box {
    background-color: #FFEBEB !important;
    color: #D32F2F !important;
    padding: 14px !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border: 1px solid #FFCDD2 !important;
}
"""

with gr.Blocks(css=custom_css, title="Diva VIP Olaykabin") as demo:
    
    gr.Markdown("## ✨ Diva VIP Olaykabin")
    
    with gr.Row():
        user_img = gr.Image(type="filepath", label="Kendi Fotoğrafın")
        garment_img = gr.Image(type="filepath", label="Yüklediğin Kıyafet")
    
    btn = gr.Button("✨ KUSURSUZ GİYDİR VE BENZERLERİNİ BUL", elem_classes=["yellow-btn"])
    
    error_output = gr.Markdown(visible=False, elem_classes=["error-box"])
    
    result_img = gr.Image(label="DIVA VIP OLAYKABIN SONUÇ", type="filepath")
    
    gr.Markdown("🛍️ *Bu Tarzı Beğendin mi? Mağazalarda Doğrudan İncele:*")

    def process_ui(user_i, garm_i):
        res, err = olaykabin_giydir(user_i, garm_i)
        if err:
            return gr.update(value=None), gr.update(value=err, visible=True)
        return gr.update(value=res), gr.update(visible=False)

    btn.click(
        fn=process_ui,
        inputs=[user_img, garment_img],
        outputs=[result_img, error_output]
    )

if _name_ == "_main_":
    demo.launch()
