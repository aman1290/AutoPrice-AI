from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from mlProject.pipeline.prediction_pipeline import PredictionPipeline
import subprocess
import os
from main import run_full_pipeline

app = FastAPI()

# Setup templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

predictor = PredictionPipeline()

@app.get("/", response_class=HTMLResponse)
async def form_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/train")
def train():
    try:
        result = run_full_pipeline()
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}



@app.post("/predict", response_class=HTMLResponse)
async def predict_price(
    request: Request,
    make: str = Form(...),
    model: str = Form(...),
    kms_driven: int = Form(...),
    ownership: str = Form(...),
    transmission: str = Form(...),
    engine: int = Form(...),
    fuel: str = Form(...),
    city: str = Form(...),
    year: int = Form(...)
):
    input_dict = {
        "make": make,
        "model": model,
        "kms_driven": kms_driven,
        "ownership": ownership,
        "transmission": transmission,
        "engine": engine,
        "fuel": fuel,
        "city": city,
        "year": year
    }

    try:
        predicted_price = predictor.predict(input_dict)
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Prediction failed: {str(e)}"
        })

    lower_range = max(0, predicted_price - 150000)
    upper_range = predicted_price + 150000

    return templates.TemplateResponse("index.html", {
        "request": request,
        "prediction": f"₹{predicted_price:,.2f}",
        "price_range": f"₹{lower_range:,.2f} - ₹{upper_range:,.2f}",
        "car_details": input_dict
    })
