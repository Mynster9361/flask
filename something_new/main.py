from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from functions import RandomPassword, OulookSignature
import subprocess

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/password", response_class=HTMLResponse)
async def read_item(request: Request, length: int = 10, Symbols: bool = True, Numbers: bool = True, Letters: bool = True, Upper: bool = False, Lower: bool = False, noambiguous: bool = True, nosimilar: bool = True):

    return templates.TemplateResponse("passwordgenerator.html", {"request": request, "pass": RandomPassword(length, Symbols, Numbers, Letters, Upper, Lower, noambiguous, nosimilar)})

#uvicorn main:app --reload

@app.get("/email/{email}}")
async def read_item(email):
    #print(OulookSignature(email))
    #return OulookSignature(email)
    process=subprocess.Popen(["powershell","Get-Childitem C:\\Windows\\*.log"],stdout=subprocess.PIPE);
    result=process.communicate()[0]
    print (result)
    return email
