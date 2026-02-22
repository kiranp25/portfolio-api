from fastapi import FastAPI
from app.routers import auth, portfolio, public, users

app = FastAPI(
    title='portfolio_app',
    version="1.0.0",
    root_path="/api"
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(portfolio.router)
app.include_router(public.router)



@app.get("/")
def root():
    print("portfolio app running")
