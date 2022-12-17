import os
import secrets
import requests

from fastapi import Depends, FastAPI, HTTPException, Request, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from redis import Redis

app = FastAPI()

class Message(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/message")
def receive_message(request: Request):
    # Parse the message text
    data = request.json()
    print(data)
    # Send a reply
    send_message(data["text"])

    return {"status" : "success"}

def parse_message(text):
    # Parse the message text here
    return text + "hi"

def send_message(text):
    # Set the API access token and group ID
    api_key = "{{ groupme.access_token }}"
    group_id = "{{ groupme.group_id }}"
    
    # Send the message to the group
    data = {
        "message": {
            "source_guid": "95be04807de7dc001351743dde",
            "text": text
        }
    }
    headers = {
        "Authorization": f"Bearer {{ groupme.access_token }}"
    }
    response = requests.post(f"https://api.groupme.com/v3/groups/{group_id}/messages", json=data, headers=headers)
    
    # Check for errors
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)



"""""
conn = Redis.from_url(os.getenv("REDIS_URL", "redis://redis/0"))
templates = Jinja2Templates(directory="/templates")

security = HTTPBasic()
auth_user = os.getenv("ADMIN_USERNAME", "aang")
auth_password = os.getenv("ADMIN_PASSWORD", "all4elements")


def get_admin_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if auth_user is None or auth_password is None:
        return "guestuser"
    correct_username = secrets.compare_digest(credentials.username, auth_user)
    correct_password = secrets.compare_digest(credentials.password, auth_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/hello")
def hello_view(name: str = "Toph"):
    return {"message": f"Hello there, {name}!"}


class Bender(BaseModel):
    name: str
    element: str


@app.post("/bender")
def add_bender(bender: Bender, username: str = Depends(get_admin_username)):
    conn.set(bender.name, bender.element)
    return {"message": f"Set element for {bender.name}!"}


@app.get("/bender")
def get_bender(name: str, username: str = Depends(get_admin_username)):
    if len(name) == 0:
        raise HTTPException(status_code=400, detail="Bender must have a name.")
    value = conn.get(name)
    if value is None:
        raise HTTPException(status_code=404, detail="bender not found.")

    return {"name": name, "element": value}


@app.get("/info", response_class=HTMLResponse)
def get_info(request: Request, username: str = Depends(get_admin_username)):
    bender_names = conn.keys()
    bender_dict = dict(
        [
            (name.decode("utf-8"), conn.get(name).decode("utf-8"))
            for name in bender_names
        ]
    )
    return templates.TemplateResponse(
        "info.html.j2", {"request": request, "benders": bender_dict}
    )
"""
