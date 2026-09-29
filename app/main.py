from fastapi import FastAPI

from app.api.research import router as research_router


app = FastAPI(
    title="Interview Intelligence Engine",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(research_router)
