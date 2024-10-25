from typing import Optional
from fastapi import APIRouter, Request, Depends


from .models import User
from .auth import current_active_user

from templates_config import templates


router = APIRouter(tags=["pages"])

@router.get("/register")
async def register_page(request: Request, errors: Optional[str] = None):
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "errors": errors
        }
    )

@router.get("/login")
async def login_page(request: Request, errors: Optional[str] = None):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "errors": errors
        }
    )

@router.get("/logout")
async def logout_page(
        request: Request,
        errors: Optional[str] = None,
        user: User = Depends(current_active_user)
):
    return templates.TemplateResponse(
        "auth/logout.html",
        {
            "request": request,
            "user": user,
            "errors": errors
        }
    )


@router.get('/profile')
async def profile_page(
        request: Request,
        errors: Optional[str] = None,
        user: User = Depends(current_active_user)
):
    return templates.TemplateResponse(
        "auth/profile.html",
        {
            "request": request,
            "user": user,
            "errors": errors
        }
    )