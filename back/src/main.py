# import os
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.templating import Jinja2Templates

# from routes import auth, dashboard, documents, files

# app = FastAPI(title="Sistema de Gestión de Documentos")

# # Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # Obtener la ruta absoluta de la carpeta src
# app.mount("/static", StaticFiles(directory="../../front/static"), name="static")
# app.mount("/documents", StaticFiles(directory="documents"), name="documents")

# # Routers
# app.include_router(auth.router)
# app.include_router(dashboard.router)
# app.include_router(documents.router)
# app.include_router(files.router)

import os
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from routes import auth, dashboard, documents, files

app = FastAPI(title="Sistema de Gestión de Documentos")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Crear router principal con prefijo
main_router = APIRouter(prefix="/seguimientos")

# Incluir todos los routers bajo el prefijo /seguimientos
main_router.include_router(auth.router)
main_router.include_router(dashboard.router)
main_router.include_router(documents.router)
main_router.include_router(files.router)

# Montar la aplicación principal
app.include_router(main_router)

# Montar archivos estáticos (también bajo /seguimientos)
app.mount("/seguimientos/static", StaticFiles(directory="../../front/static"), name="static")
app.mount("/seguimientos/documents", StaticFiles(directory="documents"), name="documents")