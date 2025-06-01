import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat_routes
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("<<<~~~~~~~~~~~~>>>"*50)


app.include_router(chat_routes.router)








if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=900, reload=True)