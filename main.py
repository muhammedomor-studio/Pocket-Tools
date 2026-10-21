import io
import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import qrcode
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pypdf
from pdf2image import convert_from_bytes

app = FastAPI(
    title="Pocket Tools API",
    description="A high-performance premium Swiss-Army knife utility API & Web Tool",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Pocket Tools", "version": "1.0.0"}


# --- TOOL 1: QR CODE GENERATOR ---
@app.get("/api/v1/generate-qr")
async def generate_qr(
    text: str,
    fill_color: str = "#000000",
    back_color: str = "#ffffff",
    box_size: int = 10
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=min(max(box_size, 1), 50),
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png", headers={"Content-Disposition": "inline; filename=qrcode.png"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate QR Code: {str(e)}")


# --- TOOL 2: PDF TO TEXT EXTRACTOR ---
@app.post("/api/v1/pdf-to-text")
async def pdf_to_text(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    
    try:
        contents = await file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(contents))
        
        num_pages = len(pdf_reader.pages)
        pages_data = []
        full_text = ""

        for idx, page in enumerate(pdf_reader.pages):
            text = page.extract_text() or ""
            pages_data.append({"page": idx + 1, "text": text})
            full_text += f"--- Page {idx + 1} ---\n{text}\n\n"

        return JSONResponse(content={
            "filename": file.filename,
            "total_pages": num_pages,
            "full_text": full_text.strip(),
            "pages": pages_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


# --- TOOL 3: IMAGE COMPRESSOR & CONVERTER ---
@app.post("/api/v1/process-image")
async def process_image(
    file: UploadFile = File(...),
    output_format: str = Form("JPEG"),
    quality: int = Form(80),
    max_width: Optional[int] = Form(None)
):
    valid_formats = ["JPEG", "PNG", "WEBP"]
    out_fmt = output_format.upper()
    if out_fmt not in valid_formats:
        raise HTTPException(status_code=400, detail="Unsupported output format. Choose JPEG, PNG, or WEBP.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Convert palette/RGBA modes appropriately for JPEG
        if out_fmt == "JPEG" and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Optional resize preserving aspect ratio
        if max_width and max_width > 0 and image.width > max_width:
            aspect_ratio = image.height / image.width
            new_height = int(max_width * aspect_ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        save_params = {}
        if out_fmt in ["JPEG", "WEBP"]:
            save_params["quality"] = min(max(quality, 10), 100)
        
        image.save(buf, format=out_fmt, **save_params)
        buf.seek(0)

        ext = out_fmt.lower()
        media_type = f"image/{ext}"
        return StreamingResponse(
            buf, 
            media_type=media_type, 
            headers={"Content-Disposition": f'attachment; filename="processed_image.{ext}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")


# --- TOOL 4: PDF TO IMAGES CONVERTER ---
@app.post("/api/v1/pdf-to-images")
async def pdf_to_images(
    file: UploadFile = File(...),
    page_number: int = Form(1)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file. Please upload a PDF.")

    try:
        contents = await file.read()
        # Convert specific page
        images = convert_from_bytes(contents, first_page=page_number, last_page=page_number)
        if not images:
            raise HTTPException(status_code=400, detail="Specified page out of bounds.")
        
        img = images[0]
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": f'inline; filename="pdf_page_{page_number}.png"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to Image conversion failed: {str(e)}")


# --- TOOL 5: TEXT UTILITIES (Formatter / Word Counter / JSON Inspector) ---
@app.post("/api/v1/text-utility")
async def text_utility(
    text: str = Form(...),
    action: str = Form("analyze")
):
    if not text:
        raise HTTPException(status_code=400, detail="No text provided.")

    if action == "analyze":
        words = text.split()
        chars = len(text)
        lines = text.splitlines()
        return {
            "word_count": len(words),
            "character_count": chars,
            "character_count_no_spaces": len(text.replace(" ", "")),
            "line_count": len(lines),
            "estimated_read_time_minutes": round(len(words) / 200, 2)
        }
    elif action == "uppercase":
        return {"result": text.upper()}
    elif action == "lowercase":
        return {"result": text.lower()}
    elif action == "clean":
        clean_text = " ".join(text.split())
        return {"result": clean_text}
    else:
        raise HTTPException(status_code=400, detail="Unknown action requested.")
