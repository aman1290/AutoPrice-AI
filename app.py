from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from mlProject.pipeline.prediction_pipeline import PredictionPipeline
import subprocess
import sys
import os

app = FastAPI()
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
predictor = PredictionPipeline()

        

@app.get("/", response_class=HTMLResponse)
async def form_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

    predicted_price = predictor.predict(input_dict)

    lower_range = max(0, predicted_price - 150000)  # Ensure not negative
    upper_range = predicted_price + 150000
    
    # Format with commas for Indian numbering
    formatted_predicted = f"₹{predicted_price:,.2f}"
    formatted_lower = f"₹{lower_range:,.2f}"
    formatted_upper = f"₹{upper_range:,.2f}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "prediction": formatted_predicted,
        "price_range": f"{formatted_lower} - {formatted_upper}",
        "car_details": input_dict  # Pass all car details to template
    })

