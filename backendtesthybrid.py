import os
import io
import re
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson.objectid import ObjectId
import uvicorn
from datetime import datetime
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from neo4j import GraphDatabase

# ==========================================
# 1. KHỞI TẠO CÁC KẾT NỐI & MÔ HÌNH AI
# ==========================================
app = FastAPI(title="Hệ thống Lọc CV AI & Knowledge Graph")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối MongoDB (Hỗ trợ cả chạy Local và chạy trong Docker)
MONGO_URI = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["kltn_cv_database"]
cv_collection = db["cv_candidates"]

# Kết nối Neo4j
NEO4J_URI = os.getenv("NEO4J_URL", "neo4j://127.0.0.1:7687")
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=("neo4j", "12345678"))

print("⏳ Đang nạp Mô hình AI XLM-RoBERTa vào bộ nhớ...")
MODEL_PATH = "./Model"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
ner_model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=tokenizer, aggregation_strategy="simple")
print("✅ Nạp AI thành công!")

# ==========================================
# 2. CÁC HÀM XỬ LÝ LÕI
# ==========================================
def doc_text_tu_pdf(file_bytes):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
    except Exception as e:
        print(f"Lỗi đọc text thường: {e}")

    if len(text.strip()) < 20:
        print("🚨 Phát hiện CV dạng Scan/Ảnh! Đang kích hoạt Tesseract OCR...")
        text = "" 
        try:
            images = convert_from_bytes(file_bytes)
            for i, img in enumerate(images):
                print(f"   -> Đang quét ảnh trang {i+1}...")
                text += pytesseract.image_to_string(img, lang='vie+eng') + "\n"
        except Exception as e:
            print(f"❌ Lỗi khi quét OCR: {e}")
    return text

def boc_tach_ky_nang(van_ban):
    skills_set = set()
    tu_dien_it = [
        "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "Go", "PHP", "Ruby", "Swift", "Kotlin",
        "ReactJS", "React Native", "NextJS", "NestJS", "Angular", "VueJS", "NodeJS", "Express", "Spring Boot", "Django", "Flask", "FastAPI", "Tailwind", "TailwindCSS",
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "Prisma",
        "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Ubuntu", "CI/CD", "Jenkins",
        "Machine Learning", "Deep Learning", "NLP", "Zustand", "Redux", "HTML5", "CSS3"
    ]
    van_ban_lower = van_ban.lower()
    for skill in tu_dien_it:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', van_ban_lower):
            skills_set.add(skill)

    kich_thuoc_chunk = 800
    chunks = [van_ban[i:i + kich_thuoc_chunk] for i in range(0, len(van_ban), kich_thuoc_chunk)]
    for chunk in chunks:
        if len(chunk.strip()) > 10:
            ner_results = ner_pipeline(chunk)
            for r in ner_results:
                if r['entity_group'] == 'SKILL':
                    tu_khoa = r['word'].replace(' ', ' ').strip()
                    if len(tu_khoa) > 1:
                        skills_set.add(tu_khoa.title() if len(tu_khoa) > 3 else tu_khoa.upper())
    return list(skills_set)

def cham_diem_neo4j(cv_skills, jd_skills):
    tong_diem = 0
    diem_toi_da = len(jd_skills) if len(jd_skills) > 0 else 1
    ket_qua = {"khop_hoan_toan": [], "khop_nen_tang": [], "thieu_hoan_toan": []}
    lo_trinh = {}

    with neo4j_driver.session() as session:
        for skill in jd_skills:
            cv_skills_lower = [s.lower() for s in cv_skills]
            if skill.lower() in cv_skills_lower:
                tong_diem += 1
                ket_qua["khop_hoan_toan"].append(skill)
            else:
                query_partial = """
                MATCH (s:Skill)-[:IS_PREREQUISITE_OF*1..3]->(target:Skill)
                WHERE toLower(target.name) = toLower($jd_skill)
                AND toLower(s.name) IN $cv_skills_lower
                RETURN s.name AS ky_nang_goc LIMIT 1
                """
                result = session.run(query_partial, jd_skill=skill, cv_skills_lower=cv_skills_lower).single()
                
                if result:
                    tong_diem += 0.5
                    ket_qua["khop_nen_tang"].append({"yeu_cau": skill, "da_co_nen_tang": result["ky_nang_goc"]})
                else:
                    ket_qua["thieu_hoan_toan"].append(skill)
                    query_path = """
                    MATCH p = (start:Skill)-[:IS_PREREQUISITE_OF*1..4]->(target:Skill)
                    WHERE toLower(target.name) = toLower($target_skill)
                    AND NOT ()-[:IS_PREREQUISITE_OF]->(start)
                    RETURN [n in nodes(p) | n.name] AS duong_di LIMIT 1
                    """
                    path_result = session.run(query_path, target_skill=skill).single()
                    lo_trinh[skill] = " ➔ ".join(path_result["duong_di"]) if path_result else f"Học chuyên sâu {skill}"

    return (tong_diem / diem_toi_da) * 100, ket_qua, lo_trinh

# ==========================================
# 3. API ENDPOINTS
# ==========================================
@app.post("/api/upload_cv")
async def xu_ly_cv_upload(file: UploadFile = File(...), jd_skills_string: str = Form(...)):
    jd_skills = boc_tach_ky_nang(jd_skills_string)
    if not jd_skills: jd_skills = ["Python"] 

    file_bytes = await file.read()
    if file.filename.endswith(".pdf"):
        cv_text = doc_text_tu_pdf(file_bytes)
    else:
        cv_text = file_bytes.decode("utf-8")

    # TẠO TÓM TẮT CV (Lấy 50 từ đầu tiên)
    mang_tu_vung = cv_text.split()
    tom_tat_cv = " ".join(mang_tu_vung[:50]) + ("..." if len(mang_tu_vung) > 50 else "")

    cv_skills = boc_tach_ky_nang(cv_text)
    diem_so, chi_tiet_khop, lo_trinh = cham_diem_neo4j(cv_skills, jd_skills)

    if diem_so >= 70: trang_thai = "PASS"
    elif diem_so >= 60: trang_thai = "MAYBE"
    else: trang_thai = "FAIL"

    cv_data = {
        "ten_file": file.filename,
        "ngay_nop": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tom_tat_cv": tom_tat_cv, # Thêm trường tóm tắt vào CSDL
        "ky_nang_jd_yeu_cau": jd_skills,
        "ky_nang_ai_tim_thay": cv_skills,
        "diem_so": round(diem_so, 2),
        "trang_thai": trang_thai,
        "chi_tiet_danh_gia": chi_tiet_khop,
        "lo_trinh_hoc": lo_trinh
    }
    
    result = cv_collection.insert_one(cv_data)
    del cv_data["_id"]
    cv_data["id_ung_vien"] = str(result.inserted_id)

    return {"message": "Thành công!", "data": cv_data}

@app.get("/api/bang_xep_hang")
def lay_bang_xep_hang():
    danh_sach_cv = list(cv_collection.find().sort("diem_so", -1))
    for cv in danh_sach_cv:
        cv["id_ung_vien"] = str(cv["_id"])
        del cv["_id"]
    return {"tong_so": len(danh_sach_cv), "danh_sach": danh_sach_cv}

@app.delete("/api/xoa_cv/{cv_id}")
def xoa_cv(cv_id: str):
    try:
        result = cv_collection.delete_one({"_id": ObjectId(cv_id)})
        if result.deleted_count == 1: return {"message": "Đã xóa CV thành công!"}
        else: return {"message": "Không tìm thấy CV này."}, 404
    except Exception as e:
        return {"message": f"Lỗi định dạng ID: {str(e)}"}, 400

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)