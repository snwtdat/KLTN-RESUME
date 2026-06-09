# 🚀 AI Resume Tracker - Hệ thống ATS Lọc CV Thông minh

**Đồ án Tốt nghiệp - Khoa Công nghệ Thông tin, Đại học Thăng Long** **Sinh viên thực hiện:** Đỗ Tiến Đạt

---

## 📖 Giới thiệu Dự án
Hệ thống quản lý và theo dõi ứng viên (ATS - Applicant Tracking System) được tích hợp Trí tuệ Nhân tạo (AI) và cơ sở dữ liệu Đồ thị Tri thức (Knowledge Graph). Thay vì lọc từ khóa một cách máy móc, hệ thống mô phỏng tư duy của một chuyên gia tuyển dụng (HR): đọc hiểu văn cảnh trong CV, nhận diện kỹ năng nền tảng và tự động đề xuất lộ trình đào tạo cho ứng viên.

## ✨ Tính năng Nổi bật
- **🧠 Lai ghép AI & Rule-based (Hybrid Extraction):** Bóc tách kỹ năng từ CV và JD bằng mô hình ngôn ngữ lớn `XLM-RoBERTa` kết hợp với Từ điển IT chuyên ngành, khắc phục hoàn toàn nhược điểm "mù" từ khóa trong bảng biểu.
- **🕸️ Chấm điểm bằng Đồ thị Tri thức (Neo4j):** Không chỉ chấm điểm kỹ năng khớp hoàn toàn (Exact Match), hệ thống còn cộng điểm vớt nếu ứng viên có kỹ năng nền tảng (Partial Match) dựa trên các mối quan hệ (ví dụ: `Linux -> Docker`).
- **🗺️ Đề xuất Lộ trình Học tập:** Tự động vẽ đường dẫn học tập ngắn nhất để bù đắp các kỹ năng IT còn thiếu sót.
- **👁️ Nhận dạng Ký tự Quang học (OCR):** Tích hợp `Tesseract OCR` kết hợp `pdfplumber`, sẵn sàng đọc mọi loại CV từ PDF chuẩn đến ảnh Scan mờ mịt.
- **🐳 Dockerized:** Triển khai toàn bộ hệ thống (Frontend, FastAPI, MongoDB, Neo4j, AI Models) chỉ bằng một câu lệnh duy nhất.

---

## 🛠️ Công nghệ Sử dụng
- **Backend:** Python 3.11, FastAPI, Uvicorn.
- **AI / Machine Learning:** Hugging Face `transformers`, PyTorch (Mô hình XLM-RoBERTa fine-tuned).
- **Database:** MongoDB (Lưu trữ văn bản CV), Neo4j (Graph Database lưu đồ thị kỹ năng).
- **Frontend:** HTML5, CSS3 (Tailwind CSS), JS (SweetAlert2).
- **Công cụ Khác:** Docker & Docker Compose, Tesseract OCR.

---

## ⚙️ Hướng dẫn Cài đặt & Chạy Hệ thống

### Cách 1: Triển khai nhanh bằng Docker (Khuyên dùng)
Yêu cầu máy tính đã cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1. **Clone kho mã nguồn:**
   ```bash
   git clone [https://github.com/TenCuaBan/AI-Resume-Tracker-KLTN.git](https://github.com/TenCuaBan/AI-Resume-Tracker-KLTN.git)
   cd AI-Resume-Tracker-KLTN
