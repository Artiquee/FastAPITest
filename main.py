from fastapi import FastAPI
import uvicorn
from routes.user import router as user_router
from routes.post import router as post_router
from routes.comments import router as comment_router


app = FastAPI()

app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True, log_level="debug")
