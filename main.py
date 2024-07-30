from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class FAQPair(BaseModel):
    question: str
    answer: str

class FAQResponse(BaseModel):
    faq_pairs: List[FAQPair]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/faq/{org}/{repo}", response_model=FAQResponse)
async def get_faq(org: str, repo: str):
    # Dummy data - replace this with actual implementation later
    dummy_faq_pairs = [
        FAQPair(question="What is this repo about?", answer="This is a sample answer about the repo."),
        FAQPair(question="How do I contribute?", answer="Here are some guidelines for contributing..."),
        FAQPair(question="Where can I find documentation?", answer="Documentation can be found in the /docs folder."),
    ]
    
    return FAQResponse(faq_pairs=dummy_faq_pairs)