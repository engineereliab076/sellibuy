"""FastAPI application entrypoint."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="SelliBuy Backend",
        version="0.1.0",
    )

    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {
            "status": "ok",
            "service": "sellibuy-backend",
        }

    return app


app = create_app()
