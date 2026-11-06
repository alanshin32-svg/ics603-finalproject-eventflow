from fastapi import FastAPI

app = FastAPI(title="EventFlow")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to EventFlow"}
