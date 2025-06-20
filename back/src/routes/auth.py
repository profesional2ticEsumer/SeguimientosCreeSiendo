# auth.py
from fastapi import APIRouter, Form, Response, Request, HTTPException
from fastapi.responses import RedirectResponse
from typing import Dict, List

router = APIRouter()

# Estructura de usuarios
AUTHORIZED_USERS = {
    "administrador": {
        "password": "Esumer2025**",
        "role": "superadmin",
        "name": "Eduardo Duque"
    },
    "administrador2": {
        "password": "Esumer2025**",
        "role": "superadmin",
        "name": "Maria Jose Castaño"
    },
    "1040744789": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Juliana Jaramillo Mazo"
    },
    "1039701366": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Jheniffer Marcela Pérez"
    },
    "1036928529": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Lina Marcela Botero Escobar"
    },
    "39452804": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Paola Andrea Mejía"
    },
    "15437492": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Duvian Sanchez Gallego"
    },
    "1036397698": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Gloria María Ospina Cardona"
    },
    "1152209099": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Valentina Suarique Agudelo"
    },
    "1026148543": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Juliana Jaramillo Mazo"
    },
    "1036928529": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Lina Marcela Botero Escobar"
    },
    "1026148543": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Melissa Soto Velez"
    },
    "1036951860": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Maria Alejandra Franco Jimenez"
    },
    "71291859": {
        "password": "Esumer2025**",
        "role": "admin",
        "name": "Edisson Andres Perez"
    },
}

@router.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user_data = AUTHORIZED_USERS.get(username)
    if not user_data or password != user_data["password"]:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    response = RedirectResponse(url="/seguimientos/dashboard", status_code=302)
    response.set_cookie(key="auth", value="true", max_age=3600, httponly=False)
    response.set_cookie(key="user", value=username, max_age=3600, httponly=False)
    response.set_cookie(key="role", value=user_data["role"], max_age=3600, httponly=False)
    response.set_cookie(key="name", value=user_data["name"], max_age=3600, httponly=False)  # <- ESTA LÍNEA ES NUEVA

    return response

@router.post("/logout")
async def logout(request: Request, response: Response):
    response = RedirectResponse(url="/seguimientos", status_code=302)
    response.delete_cookie("auth")
    response.delete_cookie("user")
    response.delete_cookie("role")
    response.delete_cookie("name")
    return response
