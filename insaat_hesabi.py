import streamlit as st
import pandas as pd
import os
import io

# Sayfa ayarları 
st.set_page_config(page_title="İnşaat Maliyet Analizi", page_icon="🏗️", layout="wide")

# Değişkenleri sıfırlayalım (Hata almamak için)
p_kereste = p_demir_beton = p_bims = toplam_kaba_iscilik = 0
p_celik_kapi = p_oluk = p_fayans = p_parke = p_ic_kapi = p_su_isitma = p_elektrik = p_mantolama = p_mutfak = 0
iscilik_tipi = "Metrekare (m²) Üzerinden"
m2 = 100 # Varsayılan değer

# ==========================================
# KURUMSAL VE ŞIK SOL YAN MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    # Akıllı Logo (Yeni Streamlit güncellemesine göre ayarlandı)
    if os.path.exists("logo.png"):
        st.image("logo.png", width="stretch")
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", width="stretch")
    else:
        st.info("📌 Kendi logonuzu eklemek için bu klasöre 'logo.png' adında bir resim dosyası koyun.")
    
    st.markdown("---")
    
    # Kurumsal, sade başlık
    st.markdown("<h3 style='text-align: center; color: #2C3E50; font-weight: 800;'>⚙️ PROJE AYARLARI</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================
    # YENİ, ŞIK VE SADE M2 ALANI
    # ==========================================
    st.markdown("""
    <div style="background-color: #2C3E50; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <span style="color: #FFFFFF; font-size: 16px; font-weight: bold; letter-spacing: 0.5px;">📐 YAPILACAK İNŞAATIN M²'Sİ</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Kutu tasarımı
    m2 = st.number_input("Alan", min_value=1, max_value=2000, value=100, step=5, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 5px;'>🎯 Hesaplama Kapsamı</h4>", unsafe_allow_html=True)
    
    # Toggle düğmeleri
    kaba_dahil = st.toggle("🧱 Kaba İnşaat Dahil", value=True)
    ince_dahil = st.toggle("🏠 İnce İnşaat Dahil", value=True)
    
    st.markdown("---")
    st.info("🏢 **Geliştirici:** Deha Grup Yapı / Aksaray")

# ==========================================
# ANA EKRAN VE SEKMELER
# ==========================================
st.title("🏗️ İnşaat Maliyet Analizi")
st.markdown("Güncel birim fiyatları değiştirerek anlık maliyet raporu oluşturabilirsiniz. İstemediğiniz kalemlere **0** yazabilirsiniz.")

# Rapor sekmesini ilk sıraya koyduk
tab_rapor, tab_kaba, tab_ince = st.tabs(["📊 Rapor ve Özet", "🧱 Kaba İnşaat Fiyatları", "🏠 İnce İnşaat Fiyatları"])

with tab_kaba:
    if kaba_dahil:
        st.subheader("Kaba İnşaat Birim Fiyatları (TL/m²)")
        col1, col2 = st.columns(2)
        with col1:
            p_kereste = st.number_input("Kereste", value=1000, step=50)
            p_demir_beton = st.number_input("Demir Beton Malzemesi", value=4200, step=100)
        with col2:
            p_bims = st.number_input("Bims, Çimento, Kum, Kiremit", value=3000, step=100)
            
        st.markdown("#### İşçilik Giderleri")
        iscilik_tipi = st.radio("İşçilik Fiyatlandırma Yöntemi:", ["Metrekare (m²) Üzerinden", "Götürü (Sabit Fiyat)"], horizontal=True)
        if iscilik_tipi == "Metrekare (m²) Üzerinden":
            p_kaba_iscilik_m2 = st.number_input("Kaba İnşaat İşçiliği (TL/m²)", value=4000, step=100)
            toplam_kaba_iscilik = m2 * p_kaba_iscilik_m2
        else:
            toplam_kaba_iscilik = st.number_input("Götürü İşçilik Toplam Fiyatı (TL)", value=400000, step=5000)
    else:
        st.warning("Kaba inşaat hesaplamaya dahil edilmedi. Sol menüden aktif edebilirsiniz.")

with tab_ince:
    if ince_dahil:
        st.subheader("İnce İnşaat Birim Fiyatları (TL/m²)")
        col3, col4 = st.columns(2)
        with col3:
            p_celik_kapi = st.number_input("Çelik Kapı ve Pencere", value=1000, step=50)
            p_oluk = st.number_input("Oluk, Şap, Küpeşte", value=1000, step=50)
            p_fayans = st.number_input("Fayans (İşçilikli)", value=1200, step=50)
            p_parke = st.number_input("Parke", value=500, step=50)
            p_ic_kapi = st.number_input("İç Kapılar", value=750, step=50)
        with col4:
            p_su_isitma = st.number_input("Su ve Isıtma Tesisatı (Malzemeli)", value=1400, step=50)
            p_elektrik = st.number_input("Elektrik Tesisatı (İşçilikli)", value=1400, step=50)
            p_mantolama = st.number_input("Mantolama / Dış Cephe", value=1400, step=50)
            p_mutfak = st.number_input("Mutfak Dolabı", value=1000, step=50)
    else:
        st.warning("İnce inşaat hesaplamaya dahil edilmedi. Sol menüden aktif edebilirsiniz.")

# ==========================================
# HESAPLAMALAR 
# ==========================================
kalemler = []

if kaba_dahil:
    kalemler.extend([
        {"Kategori": "Kaba İnşaat", "Kalem": "Kereste", "Tutar": m2 * p_kereste},
        {"Kategori": "Kaba İnşaat", "Kalem": "Demir Beton Malzemesi", "Tutar": m2 * p_demir_beton},
        {"Kategori": "Kaba İnşaat", "Kalem": "Bims, Çimento, Kum, Kiremit", "Tutar": m2 * p_bims},
        {"Kategori": "Kaba İnşaat", "Kalem": f"İşçilik ({iscilik_tipi})", "Tutar": toplam_kaba_iscilik},
    ])

if ince_dahil:
    kalemler.extend([
        {"Kategori": "İnce İnşaat", "Kalem": "Çelik Kapı ve Pencere", "Tutar": m2 * p_celik_kapi},
        {"Kategori": "İnce İnşaat", "Kalem": "Oluk, Şap, Küpeşte", "Tutar": m2 * p_oluk},
        {"Kategori": "İnce İnşaat", "Kalem": "Fayans (İşçilikli)", "Tutar": m2 * p_fayans},
        {"Kategori": "İnce İnşaat", "Kalem": "Parke", "Tutar": m2 * p_parke},
        {"Kategori": "İnce İnşaat", "Kalem": "Su ve Isıtma Tesisatı", "Tutar": m2 * p_su_isitma},
        {"Kategori": "İnce İnşaat", "Kalem": "Elektrik Tesisatı", "Tutar": m2 * p_elektrik},
        {"Kategori": "İnce İnşaat", "Kalem": "Mantolama / Dış Cephe", "Tutar": m2 * p_mantolama},
        {"Kategori": "İnce İnşaat", "Kalem": "İç Kapılar", "Tutar": m2 * p_ic_kapi},
        {"Kategori": "İnce İnşaat", "Kalem": "Mutfak Dolabı", "Tutar": m2 * p_mutfak},
    ])

aktif_kalemler = [k for k in kalemler if k["Tutar"] > 0]
kaba_toplam = sum(k["Tutar"] for k in aktif_kalemler if k["Kategori"] == "Kaba İnşaat")
ince_toplam = sum(k["Tutar"] for k in aktif_kalemler if k["Kategori"] == "İnce İnşaat")
genel_toplam = kaba_toplam + ince_toplam
yanilma_payli_toplam = genel_toplam * 1.10

# ==========================================
# RAPOR SEKMESİNİN İÇERİĞİ
# ==========================================
with tab_rapor:
    st.subheader("💰 Finansal Özet")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🧱 Kaba İnşaat", f"{kaba_toplam:,.0f} TL")
    m2.metric("🏠 İnce İnşaat", f"{ince_toplam:,.0f} TL")
    m3.metric("💵 Toplam Maliyet", f"{genel_toplam:,.0f} TL")
    m4.metric("📈 Toplam (+ %10 Opsiyon)", f"{yanilma_payli_toplam:,.0f} TL")
    
    st.markdown("---")
    
    if aktif_kalemler:
        st.markdown("#### 📊 Detaylı Maliyet Tablosu")
        df_ozet = pd.DataFrame(aktif_kalemler)
        
        df_gorsel = df_ozet.copy()
        df_gorsel["Tutar (TL)"] = df_gorsel["Tutar"].apply(lambda x: f"{x:,.0f} TL")
        df_gorsel = df_gorsel.drop(columns=["Tutar"])
        
        # Tablo çizimi de yeni güncellemeye göre ayarlandı
        st.dataframe(df_gorsel, width="stretch")
        
        ozet_satirlari = [
            {"Kategori": "", "Kalem": "", "Tutar": None},
            {"Kategori": "ÖZET", "Kalem": "KABA İNŞAAT TOPLAMI", "Tutar": kaba_toplam},
            {"Kategori": "ÖZET", "Kalem": "İNCE İNŞAAT TOPLAMI", "Tutar": ince_toplam},
            {"Kategori": "ÖZET", "Kalem": "GENEL TOPLAM MALİYET", "Tutar": genel_toplam},
            {"Kategori": "ÖZET", "Kalem": "%10 YANILMA PAYLI TOPLAM", "Tutar": yanilma_payli_toplam},
        ]
        
        df_excel = pd.concat([df_ozet, pd.DataFrame(ozet_satirlari)], ignore_index=True)
        
        try:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_excel.to_excel(writer, index=False, sheet_name='Maliyetler')
            
            st.download_button(
                label="📥 Raporu Excel Olarak İndir (.xlsx)",
                data=excel_buffer.getvalue(),
                file_name="Deha_Grup_Maliyet_Raporu.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.error("⚠️ Excel formatında indirebilmek için sisteminizde 'openpyxl' eksik. Lütfen terminale `pip install openpyxl` yazıp yükleyin.")
            
    else:
        st.info("Hesaplamaya dahil edilmiş hiçbir kalem bulunmamaktadır.")
