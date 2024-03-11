import uvicorn
from fastapi import FastAPI
from logger_config import setup_logger

logger = setup_logger()

app = FastAPI()


@app.get("/")
def read_root():
    logger.info("Root endpoint was called")
    return {"I think that should be logged"}


@app.get("/simple")
def read_root():
    logger.info(f"The Simple endpoint was called")
    return {"Hello": "World"}


@app.get("/input/{message}")
def read_item(message: str):
    logger.info(f"Item endpoint was called with message: {message}")
    return {"Input received:": message}


def run():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    run()
