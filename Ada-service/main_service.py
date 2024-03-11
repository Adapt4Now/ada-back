import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"I think that should be logged"}


@app.get("/simple")
def read_root():
    return {"Hello": "World"}


@app.get("/input/{message}")
def read_item(message: str):
    return {"Input received:": message}


def run():
    uvicorn.run(app, host="ada-back.vercel.app", port=443, log_level="info")


if __name__ == "__main__":
    run()
