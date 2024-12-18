import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from seabank import SeaBank
import sys
import traceback
from api_response import APIResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
@app.post('/login', tags=["login"])
def login_api(input: LoginDetails):
    try:
        seabank = SeaBank(input.username, input.password, input.account_number)
        session_raw = seabank.do_login()
        return APIResponse.json_format(session_raw)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)  
@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
    try:
        seabank = SeaBank(input.username, input.password, input.account_number)
        balance = seabank.get_balance(input.account_number)
        return APIResponse.json_format(balance)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)  
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    to_date: str
    limit: int
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
    try:
        seabank = SeaBank(input.username, input.password, input.account_number)
        history = seabank.get_transactions(input.from_date,input.to_date,input.account_number,input.limit)
        return APIResponse.json_format(history)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)  

if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)
