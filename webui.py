from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from config import settings
from web.routers import front_router, api_router



app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), "static")


def main():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=front_router)
    app.include_router(router=api_router)

    import uvicorn
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)


if __name__ == '__main__':
    main()
