from fastapi import FastAPI, Request
from api.routers import router
from api.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler


app = FastAPI()

app.state.limiter = limiter
app.include_router(router)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Server online"}
