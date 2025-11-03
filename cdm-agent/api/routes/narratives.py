"""
Narrative generation API routes with SSE streaming support
"""
import logging
import json
import asyncio
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from agent.narrative_agent import generate_event_narrative, generate_trade_narrative
from agent.cache_manager import (
    get_trade_narrative,
    get_event_narrative,
    save_trade_narrative,
    save_event_narrative,
    generate_version_hash
)
from providers.cdm_db.provider import get_trade_lineage

logger = logging.getLogger(__name__)
router = APIRouter()

def sse_message(event: str, data: dict) -> str:
    """Format SSE message"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

@router.get("/trades/{trade_id}/narrative/generate")
async def generate_trade_narrative_stream(trade_id: str):
    """
    Generate trade-level narrative with SSE progress streaming
    
    Returns Server-Sent Events stream showing:
    - Tool discovery
    - Each MCP tool call with full arguments
    - Tool responses with results
    - LLM generation progress
    - Final narrative and metadata
    """
    async def event_generator():
        try:
            # Check if already cached
            yield sse_message("progress", {
                "type": "cache_check",
                "message": f"🔍 Checking if we already have a narrative for trade {trade_id}..."
            })
            
            cached = get_trade_narrative(trade_id)
            if cached:
                logger.info(f"Returning cached trade narrative for {trade_id}")
                yield sse_message("progress", {
                    "type": "cache_hit",
                    "message": f"✨ Great news! Found existing narrative from {cached['created_at'].strftime('%b %d, %Y at %I:%M %p')}",
                    "timestamp": str(cached['created_at'])
                })
                yield sse_message("complete", {
                    "narrative": cached['narrative_text'],
                    "metadata": {
                        **cached['generation_metadata'],
                        "from_storage": True,
                        "cached_at": str(cached['created_at'])
                    }
                })
                return
            
            yield sse_message("progress", {
                "type": "cache_miss",
                "message": f"📝 No existing narrative found. Let's create a fresh one!"
            })
            
            # Get timeline for version hash
            yield sse_message("progress", {
                "type": "fetching_data",
                "message": f"📊 Fetching complete trade timeline from database..."
            })
            timeline_data = await get_trade_lineage(trade_id)
            version_hash = generate_version_hash(timeline_data)
            yield sse_message("progress", {
                "type": "data_ready",
                "message": f"✅ Got timeline with {len(timeline_data.get('timeline', []))} events. Ready to generate!"
            })
            
            # Generate narrative
            logger.info(f"Generating trade narrative for {trade_id}")
            
            # Collect progress events
            progress_events = []
            
            def sync_callback(event_data):
                progress_events.append(event_data)
            
            result = await generate_trade_narrative(
                trade_id=trade_id,
                progress_callback=sync_callback
            )
            
            # Stream all progress events
            for event in progress_events:
                yield sse_message("progress", event)
                await asyncio.sleep(0.01)  # Small delay for smooth streaming
            
            # Save to permanent storage
            yield sse_message("progress", {
                "type": "saving",
                "message": "💾 Saving narrative to database so you won't need to wait next time..."
            })
            
            save_trade_narrative(
                trade_id=trade_id,
                narrative_text=result['narrative'],
                generation_metadata=result['metadata'],
                version_hash=version_hash
            )
            
            yield sse_message("progress", {
                "type": "saved",
                "message": "✅ Successfully saved! Future requests will be instant."
            })
            
            logger.info(f"Saved trade narrative for {trade_id}")
            
            # Send final result
            yield sse_message("complete", {
                "narrative": result['narrative'],
                "metadata": result['metadata']
            })
            
        except Exception as e:
            logger.error(f"Error generating trade narrative: {str(e)}", exc_info=True)
            yield sse_message("error", {"error": str(e)})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )

@router.get("/trades/{trade_id}/events/{event_id}/narrative/generate")
async def generate_event_narrative_stream(
    trade_id: str,
    event_id: str,
    trade_state_id: str = Query(..., description="Trade state ID for this event")
):
    """
    Generate event-level narrative with SSE progress streaming
    
    Returns Server-Sent Events stream showing:
    - Tool calls and responses
    - LLM generation
    - Final narrative
    """
    async def event_generator():
        try:
            # Check if already cached
            yield sse_message("progress", {
                "type": "cache_check",
                "message": f"🔍 Checking if we already have a narrative for event {event_id}..."
            })
            
            cached = get_event_narrative(trade_id, event_id)
            if cached:
                logger.info(f"Returning cached event narrative for {trade_id}/{event_id}")
                yield sse_message("progress", {
                    "type": "cache_hit",
                    "message": f"✨ Great news! Found existing narrative from {cached['created_at'].strftime('%b %d, %Y at %I:%M %p')}",
                    "timestamp": str(cached['created_at'])
                })
                yield sse_message("complete", {
                    "narrative": cached['narrative_text'],
                    "metadata": {
                        **cached['generation_metadata'],
                        "from_storage": True,
                        "cached_at": str(cached['created_at'])
                    }
                })
                return
            
            yield sse_message("progress", {
                "type": "cache_miss",
                "message": f"📝 No existing narrative found. Let's create a fresh one!"
            })
            
            # Get event context for version hash
            yield sse_message("progress", {
                "type": "fetching_data",
                "message": f"📊 Fetching event context from database (state: {trade_state_id})..."
            })
            from providers.cdm_db.provider import get_lineage
            event_context = await get_lineage(trade_state_id)
            version_hash = generate_version_hash(event_context)
            yield sse_message("progress", {
                "type": "data_ready",
                "message": f"✅ Event context loaded. Ready to generate!"
            })
            
            # Generate narrative
            logger.info(f"Generating event narrative for {trade_id}/{event_id}")
            
            progress_events = []
            
            def sync_callback(event_data):
                progress_events.append(event_data)
            
            result = await generate_event_narrative(
                trade_id=trade_id,
                event_id=event_id,
                trade_state_id=trade_state_id,
                progress_callback=sync_callback
            )
            
            # Stream progress events
            for event in progress_events:
                yield sse_message("progress", event)
                await asyncio.sleep(0.01)
            
            # Save to storage
            yield sse_message("progress", {
                "type": "saving",
                "message": "💾 Saving event narrative to database so you won't need to wait next time..."
            })
            
            save_event_narrative(
                trade_id=trade_id,
                event_id=event_id,
                narrative_text=result['narrative'],
                generation_metadata=result['metadata'],
                version_hash=version_hash
            )
            
            yield sse_message("progress", {
                "type": "saved",
                "message": "✅ Successfully saved! Future requests will be instant."
            })
            
            logger.info(f"Saved event narrative for {trade_id}/{event_id}")
            
            # Send final result
            yield sse_message("complete", {
                "narrative": result['narrative'],
                "metadata": result['metadata']
            })
            
        except Exception as e:
            logger.error(f"Error generating event narrative: {str(e)}", exc_info=True)
            yield sse_message("error", {"error": str(e)})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )

@router.get("/trades/{trade_id}/narrative")
async def get_trade_narrative_cached(trade_id: str):
    """
    Get trade narrative from storage (does not generate if missing)
    
    Returns:
        Stored narrative or null if not generated yet
    """
    try:
        cached = get_trade_narrative(trade_id)
        
        if cached:
            return {
                "narrative": cached['narrative_text'],
                "metadata": {
                    **cached['generation_metadata'],
                    "from_storage": True,
                    "cached_at": str(cached['created_at'])
                }
            }
        else:
            return {"narrative": None, "metadata": None}
            
    except Exception as e:
        logger.error(f"Error fetching trade narrative: {str(e)}", exc_info=True)
        # Return null instead of 500 error to let frontend show generate button
        return {"narrative": None, "metadata": None, "error": str(e)}

@router.get("/trades/{trade_id}/events/{event_id}/narrative")
async def get_event_narrative_cached(trade_id: str, event_id: str):
    """
    Get event narrative from storage (does not generate if missing)
    
    Returns:
        Stored narrative or null if not generated yet
    """
    try:
        cached = get_event_narrative(trade_id, event_id)
        
        if cached:
            return {
                "narrative": cached['narrative_text'],
                "metadata": {
                    **cached['generation_metadata'],
                    "from_storage": True,
                    "cached_at": str(cached['created_at'])
                }
            }
        else:
            return {"narrative": None, "metadata": None}
            
    except Exception as e:
        logger.error(f"Error fetching event narrative: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/trades/{trade_id}/narrative")
async def invalidate_trade_narratives(trade_id: str):
    """
    Invalidate/delete all narratives for a trade
    Useful when trade data changes or regeneration is needed
    """
    try:
        from agent.cache_manager import invalidate_trade_narratives as invalidate
        deleted_count = invalidate(trade_id)
        logger.info(f"Invalidated {deleted_count} narratives for trade {trade_id}")
        return {"deleted": deleted_count, "trade_id": trade_id}
    except Exception as e:
        logger.error(f"Error invalidating narratives: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

