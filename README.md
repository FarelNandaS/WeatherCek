Ini adalah project berbasis python pertama saya, di mana ini adalah sebuah website analisis cuaca global dengan filter kota dan filter pengecekan lain nya. Ada dua data API yang saya ambil yaitu open-mateo untuk data cuaca nya dan open-mateo geocoding API untuk menemukan koodinasi kota yang di cari.

Requierment:
- Python 3.14.5

Tech Steck:
- requests 2.34.2
- pandas 3.0.3
- streamlit 1.57.0
- ploty 6.7.0

Setup Project:
```bash
# buat virtual environment baru
python -m venv env

# masuk ke virtual environment
.\env\Script\Activate.ps1 # (Powershell)
.\env\Script\Activate.bat # (Windows CMD)
source env/bin/activate # (mac & linux)

# install semua library di requierments.txt
pip install -r requirements.text

# Jalan kan Website melalui streamlit
sreamlit run app.py
