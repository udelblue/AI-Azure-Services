from fastapi import FastAPI, Form, Request, status,  File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import re   

from services.language import Language
from services.storage import Storage

from dotenv import load_dotenv

from services.vision import Vision
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})

@app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})

def split_paragraph_into_sentences(paragraph):
    # Use regular expression to split by sentence-ending punctuation followed by a space or end of string
    sentences = re.split(r'(?<=[.!?]) +', paragraph)
    return sentences


# image_analysis
@app.get("/image_analysis", response_class=HTMLResponse)
async def image_analysis_get(request: Request):
    print('Request for image_analysis page received')

    context = {"request": request, "original_post":  "", "summerization": "" }
    return templates.TemplateResponse('image_analysis.html', context)

@app.post("/image_analysis", response_class=HTMLResponse)
async def image_analysis( request: Request, name: UploadFile = File(...)):

    storage = Storage()
    storage_values = storage.upload_file(name) 
    # sas_token = storage.generate_sas_token(name.filename)
    public_url = storage.get_public_url(name.filename)

    image_url = public_url
    vision = Vision()
    summary = vision.image_analysis_from_url(image_url)
    context = {"request": request, "original_post": image_url, "summerization": summary }
    return templates.TemplateResponse('image_analysis.html', context)

# image_analysis OCR
@app.get("/image_analysis_OCR", response_class=HTMLResponse)
async def image_analysis_OCR_get(request: Request):
    print('Request for image_analysis page received')

    context = {"request": request, "original_post":  "", "summerization": "" }
    return templates.TemplateResponse('image_analysis_ocr.html', context)

@app.post("/image_analysis_OCR", response_class=HTMLResponse)
async def image_analysis_OCR( request: Request, name: UploadFile = File(...)):

    storage = Storage()
    storage_values = storage.upload_file(name) 
    # sas_token = storage.generate_sas_token(name.filename)
    public_url = storage.get_public_url(name.filename)

    image_url = public_url
    vision = Vision()
    summary = vision.image_analysis_OCR_from_url(image_url)
    context = {"request": request, "original_post": image_url, "summerization": summary }
    return templates.TemplateResponse('image_analysis_ocr.html', context)

#summerization
@app.get("/summerization", response_class=HTMLResponse)
async def summerization_get(request: Request):
    print('Request for summerization page received')
    context = {"request": request}
    return templates.TemplateResponse('summerization.html', context)

@app.post("/summerization", response_class=HTMLResponse)
async def summerization(request: Request, name: str = Form(...)): 
    if name:
        block = []
        block.append(name)
        lang = Language()
        summary = lang.extractive_summarization(block)
        context = {"request": request, "original_post": name, "summerization": summary }
        return templates.TemplateResponse('summerization.html', context)
    else:
        print('Request for summerization page received with no value submitted  -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

# sentiment_analyze
@app.get("/sentiment_analyze", response_class=HTMLResponse)
async def sentiment_analyze_get(request: Request):
    print('Request for sentiment_analyze page received')
    context = {"request": request}
    return templates.TemplateResponse('sentiment_analyze.html', context)


@app.post("/sentiment_analyze", response_class=HTMLResponse)
async def sentiment_analyze(request: Request, name: str = Form(...)):
    if name:
        split = split_paragraph_into_sentences(name)
        lang = Language()
        summary = lang.sentiment_analysis_with_opinion_mining(split)
        context = {"request": request, "original_post": name, "summerization": summary }
        return templates.TemplateResponse('sentiment_analyze.html', context)
    else:
        print('Request for sentiment_analyze page received with no value submitted -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

#entity_recognition
@app.get("/entity_recognition", response_class=HTMLResponse)
async def entity_recognition_get(request: Request):
    print('Request for entity_recognition page received')
    context = {"request": request}
    return templates.TemplateResponse('entity_recognition.html', context)


@app.post("/entity_recognition", response_class=HTMLResponse)
async def entity_recognition(request: Request, name: str = Form(...)):
    summary = ""
    if name:
        split = split_paragraph_into_sentences(name)
        langage = Language()
        results = langage.entity_recognition(split)
        context = {"request": request, "original_post": name, "summerization": results }
        return templates.TemplateResponse('entity_recognition.html', context)
    else:
        print('Request for entity_recognition page received with no value submitted -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)


#entity linking
@app.get("/extract_key_phrases", response_class=HTMLResponse)
async def extract_key_phrases_get(request: Request):
    print('Request for extract_key_phrases page received')
    context = {"request": request}
    return templates.TemplateResponse('extract_key_phrases.html', context)


@app.post("/extract_key_phrases", response_class=HTMLResponse)
async def extract_key_phrases(request: Request, name: str = Form(...)):
    summary = ""
    if name:
        split = split_paragraph_into_sentences(name)
        langage = Language()
        results = langage.extract_key_phrases(split)
        context = {"request": request, "original_post": name, "summerization": results }
        return templates.TemplateResponse('extract_key_phrases.html', context)
    else:
        print('Request for extract_key_phrases page received with no value submitted -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)



if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)

