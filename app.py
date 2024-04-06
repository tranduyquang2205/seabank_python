import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from seabank import SeaBank


app = FastAPI()




class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
@app.post('/login', tags=["login"])
def login_api(input: LoginDetails):
        seabank = SeaBank(input.username, input.password, input.account_number)
        session_raw = seabank.do_login()
        return json.loads(session_raw)

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
        seabank = SeaBank(input.username, input.password, input.account_number)
        accounts_list = seabank.get_accounts()
        return json.loads(accounts_list)
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    to_date: str
    limit: int
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
        seabank = SeaBank(input.username, input.password, input.account_number)
        history = seabank.get_transactions(input.from_date,input.to_date,input.account_number,input.limit)
        return json.loads(history)


if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)
