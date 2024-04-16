import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(routes.app, prefix='/contacts')
app.include_router(routes.router, prefix='/auth')



@app.get("/")
def read_root():
    """
        Root endpoint returning a simple greeting message.

        Returns:
            dict: A simple greeting message.
        """
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
