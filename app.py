import requests
import pandas as pd
import streamlit as str_web
import plotly.express as px

str_web.set_page_config(page_title="Dashboard Cuaca Global", layout='wide')

def cari_koordinat_kota(nama_kota):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": nama_kota,
        "count": 1,
        "language": "id"
    }
    try: 
        response= requests.get(url, params, timeout=5)
        if response.status_code == 200:
            hasil = response.json()
            if "results" in hasil and len(hasil['results']) > 0:
                data_kota = hasil['results'][0]
                return {
                    "lat": data_kota['latitude'],
                    "lon": data_kota['longitude'],
                    "negara": data_kota.get("country", "tidak diketahui"),
                    "nama_resmi": data_kota['name']
                }
        return None
    except Exception:
        return None

def ambil_data_cuaca(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,rain",
        "timezone": "Asia/Jakarta"
    }

    print('Sedang Mengambil Data')

    try:
        response = requests.get(url, params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print('Data berhasil di ambil')
            return data
        else :
            print('Gagal mengambil data. Error code: {response.status_code}')
            return None
    except Exception:
        return None
    

def proses_ke_dataframe(data_mentah):
    data_jam = data_mentah['hourly']
    df = pd.DataFrame(data_jam)
    df['time'] = pd.to_datetime(df["time"])
    df = df.rename(columns={
        'time': 'Waktu',
        'temperature_2m': 'Suhu_Celcius',
        'relative_humidity_2m': 'Kelembapan_Persen',
        'rain': 'Curah_Hujan_MM'
    })
    df['Hari'] = df['Waktu'].dt.day_name()
    df['Jam'] = df['Waktu'].dt.hour
    return df

str_web.sidebar.title("🔍 Pencarian Lokasi")

input_kota = str_web.sidebar.text_input("Ketik Nama Kota (Global):", value="Surabaya")

if input_kota:
    info_lokasi = cari_koordinat_kota(input_kota)

    if info_lokasi:
        nama_kota_resmi = info_lokasi['nama_resmi']
        negara = info_lokasi['negara']

        str_web.title(f'🌤️ Dashboard Analisis Data Cuaca ({nama_kota_resmi}, {negara})')
        str_web.markdown(f'Koordinat Ditemukan: **Lat: {info_lokasi['lat']}, Long: {info_lokasi['lon']}**')

        data_mentah = ambil_data_cuaca(lat=info_lokasi['lat'], lon=info_lokasi['lon'])

        if data_mentah:
            df_cuaca = proses_ke_dataframe(data_mentah)

            cuaca_sekarang = df_cuaca.iloc[0]

            str_web.subheader("Kondisi saat ini")
            kolom1, kolom2, kolom3 = str_web.columns(3)

            with kolom1: 
                str_web.metric(label="Suhu Udara", value=f"{cuaca_sekarang['Suhu_Celcius']} ℃")
            with kolom2:
                str_web.metric(label="Kelembapan", value=f"{cuaca_sekarang['Kelembapan_Persen']} %")
            with kolom3:
                str_web.metric(label="Curah Hujan", value=f"{cuaca_sekarang['Curah_Hujan_MM']} mm")

            str_web.markdown('---')

            str_web.subheader('📊 Rangkuman Statistik (Prediksi 7 Hari Ke Depan)')

            suhu_max = df_cuaca['Suhu_Celcius'].max()
            suhu_min = df_cuaca['Suhu_Celcius'].min()
            total_hujan = df_cuaca['Curah_Hujan_MM'].sum()

            stat1, stat2, stat3 = str_web.columns(3)
            with stat1:
                str_web.info(f"🌡️ **Suhu Tertinggi:** {suhu_max} °C")
            with stat2:
                str_web.info(f"❄️ **Suhu Terendah:** {suhu_min} °C")
            with stat3:
                jam_hujan = len(df_cuaca[df_cuaca['Curah_Hujan_MM'] > 0])
                str_web.info(f"🌧️ **Total Estimasi Hujan:** {total_hujan:.1f} mm (terjadi selama {jam_hujan} jam)")

            str_web.markdown('---')

            str_web.subheader('"📈 Analisis Grafik Tren"')

            ctrl1, ctrl2 = str_web.columns(2)
            with ctrl1:
                pilihan_metrik = str_web.selectbox(
                    "Pilih Variable Cuaca Untuk Dilihat Trennya:",
                    ["Suhu_Celcius", "Kelembapan_Persen", "Curah_Hujan_MM"]
                )
            with ctrl2:
                daftar_hari = ["Semua Hari"] + list(df_cuaca['Hari'].unique())
                pilihan_hari = str_web.selectbox("Filter Berdasarkan Hari:", daftar_hari)

            if pilihan_hari != "Semua Hari" :
                df_tampil = df_cuaca[df_cuaca['Hari'] == pilihan_hari]
            else :
                df_tampil = df_cuaca

            fig = px.line(
                df_tampil,
                x="Waktu",
                y=pilihan_metrik,
                title=f"Grafik Perubahan {pilihan_metrik} Per Jam",
                labels={pilihan_metrik: pilihan_metrik, "Waktu": "Waktu Analisis"},
                markers=True
            )

            str_web.plotly_chart(fig, use_container_width=True)

            with str_web.expander("Lihat Data Tabel Mentah (Pandas DataFrame)"):
                str_web.dataframe(df_cuaca)

        else:
            str_web.error("Gagal terhubung ke API cuaca. Periksa koneksi internet anda.")
    else:
        str_web.sidebar.error("❌ Nama kota tidak ditemukan di database global. Coba periksa ejaannya.")
else:
    str_web.error('Mohon isi nama kota untuk melihat Cuaca')