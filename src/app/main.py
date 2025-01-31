from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.route import router as auth_router

app = FastAPI()

# Add CORS middleware with expanded configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 10 minutes
)

# Add authentication middleware AFTER CORS middleware
# public_paths = [
#     "/auth/login",
#     "/auth/create-account",
#     "/",
#     "/docs",
#     "/openapi.json",
#     "/redoc",
# ]
# app.add_middleware(AuthMiddleware, public_paths=public_paths)

# Add routes
app.include_router(router=auth_router)


# app.add_event_handler(
#     "startup",
#     execute_backend_server_event_handler(backend_app=app),
# )
# app.add_event_handler(
#     "shutdown",
#     terminate_backend_server_event_handler(backend_app=app),
# )


@app.get("/")
async def root():
    return {"message": "Welcome to yet-another-fastapi-template"}
