# back/src/utils/dependencies.py
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="../../front/templates")
