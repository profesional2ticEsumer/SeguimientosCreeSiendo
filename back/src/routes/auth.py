from fastapi import APIRouter, Form, Response, Request, HTTPException
from fastapi.responses import RedirectResponse
from utils.helpers import is_authenticated

router = APIRouter()

ADMIN_USERNAME = "administrador"
ADMIN_PASSWORD = "Esumer2025**"

@router.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="auth", value="true", max_age=3600, httponly=True)
    response.set_cookie(key="user", value=username, max_age=3600, httponly=True)
    return response

@router.post("/logout")
async def logout(request: Request, response: Response):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("auth")
    response.delete_cookie("user")
    return response
