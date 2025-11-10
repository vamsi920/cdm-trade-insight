"""
FastAPI application for CDM Trade Insight API
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import trades, narratives
from agent.mcp_client import MCPClientManager
from agent.narrative_agent import set_mcp_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Initializes MCP client connections on startup and cleans up on shutdown
    """
    # Startup: Initialize MCP client
    logger.info("=" * 60)
    logger.info("Starting CDM Trade Insight API with MCP architecture")
    logger.info("=" * 60)
    
    mcp_client = MCPClientManager()
    
    try:
        # Connect to all MCP servers and discover tools
        await mcp_client.start()
        
        # Set the MCP client for narrative agent
        set_mcp_client(mcp_client)
        
        # Log discovered tools
        tools = mcp_client.get_available_tools()
        logger.info(f"✅ MCP client initialized successfully")
        logger.info(f"📦 Connected to {len(mcp_client.processes)} MCP servers")
        logger.info(f"🔧 Discovered {len(tools)} tools:")
        for tool in tools:
            tool_name = tool["function"]["name"]
            logger.info(f"   - {tool_name}")
        
        logger.info("=" * 60)
        logger.info("🚀 API server ready to accept requests")
        logger.info("=" * 60)
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP client: {e}")
        raise
    
    finally:
        # Shutdown: Cleanup MCP connections
        logger.info("Shutting down MCP client connections...")
        await mcp_client.shutdown()
        logger.info("✅ MCP client shutdown complete")


app = FastAPI(
    title="CDM Trade Insight API",
    description="REST API for querying CDM trade states and business events with MCP-powered narrative generation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],  # Vite dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# Include routers
app.include_router(trades.router, prefix="/api", tags=["trades"])
app.include_router(narratives.router, prefix="/api", tags=["narratives"])

