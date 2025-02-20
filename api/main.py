from fastapi import FastAPI, Request, Depends
from api.routers import router
from api.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from api.auth import get_api_key
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(dependencies=[Depends(get_api_key)])

origins = [
    "https://benceluzsinszky.com",
    "https://www.benceluzsinszky.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.include_router(router)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Server online"}
