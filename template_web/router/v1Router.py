"""
Router v1 - Rutas de la aplicación web
"""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from controller.v1Controller import v1Controller
from dependencies.auth import get_current_user_cookie, create_session_cookie

router = APIRouter()

def get_templates(request: Request):
    return request.app.state.templates

def get_controller() -> v1Controller:
    return v1Controller()


# Páginas públicas

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, templates=Depends(get_templates)):
    """Página de inicio"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, templates=Depends(get_templates)):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    controller: v1Controller = Depends(get_controller)
):
    """Procesar login"""
    result = await controller.login(username, password)

    if result.get("success"):
        response = RedirectResponse("/dashboard", status_code=303)
        # Crear cookie de sesión
        response.set_cookie(
            key="session_token",
            value=result["access_token"],
            httponly=True,
            secure=False,  # True en producción con HTTPS
            samesite="lax"
        )
        return response
    else:
        # Volver a login con error
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": result.get("error")}
        )


@router.get("/logout")
async def logout():
    """Cerrar sesión"""
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session_token")
    return response


# Páginas protegidas (requieren autenticación)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: dict = Depends(get_current_user_cookie),
    templates=Depends(get_templates)
):
    """Dashboard principal (requiere autenticación)"""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )


# TODO: Agregar más rutas según necesidad
