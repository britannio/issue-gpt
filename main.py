from fastapi import FastAPI
from models import *
from faq_generator import generate_faqs

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/faq/{org}/{repo}", response_model=FAQResponse)
async def get_faq(org: str, repo: str):
    pairs = generate_faqs(org, repo)
    return FAQResponse(faq_pairs=pairs)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)