"""
Main API v1 router - aggregates all endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import auth, dividends, fiis, permissions, roles, transactions, users

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(fiis.router, prefix="/fiis", tags=["FIIs"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(dividends.router, prefix="/dividends", tags=["Dividends"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
