from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pandas as pd
from typing import Optional
from random import sample
import random
import csv
app = FastAPI()
security = HTTPBasic()

# Authentication credentials
users = {
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine",
    "admin": "4dm1N"
}

# Load questions from the Excel file
questions_df = pd.read_csv("questions.csv")

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username in users and credentials.password == users[credentials.username]:
        return credentials.username
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/verify")
def verify(user: str = Depends(get_current_username)):
    return {"message": "API is working!"}

@app.get("/questions/")
def get_questions(test_type: str, category: str, number: int, user: str = Depends(get_current_username)):
    if number not in [5, 10, 20]:
        raise HTTPException(status_code=400, detail="Number of questions must be 5, 10, or 20.")
    filtered_questions = questions_df[(questions_df['use'] == test_type) & (questions_df['subject'] == category)]
    if len(filtered_questions) < number:
        raise HTTPException(status_code=400, detail="Not enough questions available.")
    
    # Replace NaN values with None (or another appropriate value for your context)
    filtered_questions = filtered_questions.fillna('None')  # Or use "" if you prefer empty strings
    # filtered_questions = filtered_questions.sample(n=number)
    filtered_questions = filtered_questions.sample(n=number)['question']
    
    # Sample the questions and convert to dict
    #sampled_questions = filtered_questions.to_dict('records')

    
    return filtered_questions.tolist() #filtered_questions

@app.post("/create_question/")
def create_question(question: dict, user: str = Depends(get_current_username)):
    if user != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You must be an admin to create a question.")
    
    # Open the CSV file in append mode and write the new question
    with open("questions.csv", "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ['question', 'subject', 'use', 'correct', 'responseA', 'responseB', 'responseC', 'responseD', 'remark']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the new question to the CSV file
        writer.writerow(question)  
    
    return {"message": "Question created successfully."}

