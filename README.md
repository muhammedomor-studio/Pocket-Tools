# 🧰 Pocket Tools - Utility API & Web Application

A premium, modern, all-in-one utility application built with **FastAPI**, **TailwindCSS**, and **Python**. Designed for seamless free deployment on **Render** via **GitHub**.

---

## ✨ Features Included

1. 📱 **QR Code Generator**: Fully customizable colors, box sizing, and high-res PNG download.
2. 📄 **PDF Text Extractor**: Upload PDFs and extract structured text per page instantly.
3. 🖼️ **Image Compressor & Converter**: Convert images between `JPEG`, `WEBP`, and `PNG` with target quality settings.
4. 📝 **Text Analyzer & Utilities**: Word count, character analysis, case formatting, and space cleanup.
5. ⚡ **Interactive API Docs**: Built-in Swagger UI provided automatically by FastAPI at `/docs`.
6. 🌙 **Dark/Light Mode**: Premium glassmorphism UI styled with Tailwind CSS.

---

## 🚀 How to Run Locally

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/pocket-tools.git
   cd pocket-tools
   ```

2. Create a virtual environment & install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

4. Open your browser and go to `http://127.0.0.1:8000`.

---

## 🌐 How to Deploy to Render (100% Free)

1. Push this entire project code to a **GitHub** repository.
2. Go to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Configure the build parameters:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click **Create Web Service**. Your app will be live in 1-2 minutes!
