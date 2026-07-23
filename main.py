from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API Scraper GitHub Aktif! Gunakan endpoint /api/github?username=NAMA_USER"}

@app.get("/api/github")
def get_github_repositories(username: str = "Grimpascal"):
    url = f"https://github.com/{username}?tab=repositories"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    
    try:
        respon = requests.get(url, headers=headers, timeout=10)
        if respon.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Username '{username}' tidak ditemukan.")
        elif respon.status_code != 200:
            raise HTTPException(status_code=respon.status_code, detail="Gagal mengambil halaman GitHub.")
            
        soup = BeautifulSoup(respon.text, 'html.parser')
        mentah = soup.find_all('li', itemprop='owns')
        
        hasil = []
        for block in mentah:
            nama_repo = "N/A"
            link_repo = "N/A"
            status_repo = "Public"
            bahasa_repo = "Not Specified"
            
            h3_element = block.find('h3', class_='wb-break-all')
            if h3_element:
                a_tag = h3_element.find('a')
                if a_tag:
                    nama_repo = a_tag.get_text(strip=True)
                    href_data = a_tag.get('href') 
                    if href_data:
                        link_repo = f"https://github.com{href_data}"
                
            status_element = block.find('span', class_='Label')
            if status_element:
                status_repo = status_element.get_text(strip=True)
                
            bahasa_element = block.find('span', itemprop='programmingLanguage')
            if bahasa_element:
                bahasa_repo = bahasa_element.get_text(strip=True)
                
            hasil.append({
                "nama_repository": nama_repo,
                "link_repository": link_repo,
                "status": status_repo,
                "bahasa": bahasa_repo
            })
            
        if not hasil:
            raise HTTPException(status_code=500, detail="Gagal ekstraksi. Struktur halaman berubah.")
            
        return {
            "status": "success",
            "username": username,
            "total_repositories": len(hasil),
            "data": hasil
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
