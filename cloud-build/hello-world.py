from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
def read_root(message: str = None):
    if message:
        return message
    else:
        return 'Hello World!'

@app.post("/")
def read_root_post(request_data: dict):
    message = request_data.get('message', None)
    if message:
        return message
    else:
        return 'Hello World!'