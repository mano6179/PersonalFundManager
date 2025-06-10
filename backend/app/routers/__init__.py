from .nav_router import router as nav_router
from .auth_router import router as auth_router
from .zerodha_router import router as zerodha_router
from .market_router import router as market_router
from .logs_router import router as logs_router

__all__ = ['nav_router', 'auth_router', 'zerodha_router', 'market_router', 'logs_router']
