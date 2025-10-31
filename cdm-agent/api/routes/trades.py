"""
Trade-related API routes
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from providers.cdm_db.provider import (
    get_trade_lineage,
    get_trade_states,
    get_tradestate_payload,
    get_business_event
)
from common.db import conn, q, one
from common.transform import (
    transform_to_trade,
    extract_product_type,
    extract_currency,
    extract_parties,
    extract_dates,
    apply_default_trade_metadata,
)
from common.diff import notional as extract_notional

logger = logging.getLogger(__name__)
router = APIRouter()
cnx = conn()


@router.get("/trades")
async def list_trades():
    """List all trades with summary information"""
    try:
        # Get all unique trade IDs
        trade_ids = q(cnx, "SELECT DISTINCT trade_id FROM trade_state ORDER BY trade_id")
        
        logger.info(f"Found {len(trade_ids)} unique trade IDs in database")
        
        if not trade_ids:
            logger.warning("No trade IDs found in database")
            return []
        
        summaries = []
        errors = []
        for row in trade_ids:
            trade_id = row["trade_id"]
            try:
                # Get timeline to get latest state
                timeline = await get_trade_lineage(trade_id)
                
                if not timeline.get("timeline"):
                    logger.warning(f"Trade {trade_id} has no timeline entries")
                    continue
                
                # Get latest trade state payload
                latest_state_id = timeline["timeline"][-1]["trade_state_id"]
                latest_payload = await get_tradestate_payload(latest_state_id)
                
                # Extract summary fields
                product_type = extract_product_type(latest_payload)
                notional_val = extract_notional(latest_payload) or 0.0
                currency = extract_currency(latest_payload)
                parties = extract_parties(latest_payload)
                dates = extract_dates(latest_payload)

                # Determine status from latest position_state
                latest_entry = timeline["timeline"][-1]
                position_state = latest_entry.get("position_state", "")
                status_map = {
                    "EXECUTED": "Pending",
                    "CONFIRMED": "Active",
                    "CLEARED": "Active",
                    "TERMINATED": "Terminated",
                    "AMENDED": "Active"
                }
                status = status_map.get(position_state, "Active")

                enriched = apply_default_trade_metadata(
                    trade_id,
                    {
                        "productType": product_type,
                        "currentNotional": notional_val,
                        "currency": currency,
                        "counterparty": parties.get("counterparty"),
                        "bank": parties.get("bank"),
                        "startDate": dates.get("startDate"),
                        "maturityDate": dates.get("maturityDate"),
                    },
                )

                summaries.append({
                    "id": trade_id,
                    "productType": enriched["productType"],
                    "status": status,
                    "currentNotional": enriched["currentNotional"],
                    "currency": enriched["currency"],
                    "counterparty": enriched.get("counterparty", "Unknown"),
                    "bank": enriched.get("bank", "Unknown")
                })
            except Exception as e:
                # Log errors but continue processing other trades
                error_msg = f"Error processing trade {trade_id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                continue
        
        logger.info(f"Successfully processed {len(summaries)} trades, {len(errors)} errors")
        
        if errors:
            logger.warning(f"Errors encountered: {errors}")
        
        return summaries
    except Exception as e:
        logger.error(f"Error listing trades: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing trades: {str(e)}")


@router.get("/trades/search")
async def search_trades(
    query: str = Query(..., alias="q", description="Search query for trade ID")
):
    """Search trades by trade ID (case-insensitive)"""
    try:
        # Search in database
        results = q(
            cnx,
            "SELECT DISTINCT trade_id FROM trade_state WHERE LOWER(trade_id) LIKE LOWER(%s) ORDER BY trade_id LIMIT 20",
            (f"%{query}%",)
        )
        
        if not results:
            return []
        
        summaries = []
        for row in results:
            trade_id = row["trade_id"]
            try:
                # Get basic info for summary
                timeline = await get_trade_lineage(trade_id)
                
                if not timeline.get("timeline"):
                    continue
                
                latest_state_id = timeline["timeline"][-1]["trade_state_id"]
                latest_payload = await get_tradestate_payload(latest_state_id)
                
                product_type = extract_product_type(latest_payload)
                notional_val = extract_notional(latest_payload) or 0.0
                currency = extract_currency(latest_payload)
                parties = extract_parties(latest_payload)
                dates = extract_dates(latest_payload)

                latest_entry = timeline["timeline"][-1]
                position_state = latest_entry.get("position_state", "")
                status_map = {
                    "EXECUTED": "Pending",
                    "CONFIRMED": "Active",
                    "CLEARED": "Active",
                    "TERMINATED": "Terminated",
                    "AMENDED": "Active"
                }
                status = status_map.get(position_state, "Active")

                enriched = apply_default_trade_metadata(
                    trade_id,
                    {
                        "productType": product_type,
                        "currentNotional": notional_val,
                        "currency": currency,
                        "counterparty": parties.get("counterparty"),
                        "bank": parties.get("bank"),
                        "startDate": dates.get("startDate"),
                        "maturityDate": dates.get("maturityDate"),
                    },
                )

                summaries.append({
                    "id": trade_id,
                    "productType": enriched["productType"],
                    "status": status,
                    "currentNotional": enriched["currentNotional"],
                    "currency": enriched["currency"],
                    "counterparty": enriched.get("counterparty", "Unknown"),
                    "bank": enriched.get("bank", "Unknown")
                })
            except Exception:
                continue
        
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching trades: {str(e)}")


@router.get("/trades/{trade_id}")
async def get_trade(trade_id: str):
    """Get full trade details with events"""
    try:
        # Get timeline data
        timeline_data = await get_trade_lineage(trade_id)
        
        if not timeline_data.get("timeline"):
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
        
        # Get all trade state payloads for transformation
        trade_state_payloads = {}
        for entry in timeline_data["timeline"]:
            trade_state_id = entry.get("trade_state_id")
            try:
                payload = await get_tradestate_payload(trade_state_id)
                trade_state_payloads[trade_state_id] = payload
            except Exception:
                continue
        
        # Get latest trade state payload
        latest_state_id = timeline_data["timeline"][-1]["trade_state_id"]
        latest_payload = await get_tradestate_payload(latest_state_id)
        
        # Transform to Trade format
        trade = transform_to_trade(
            trade_id,
            timeline_data,
            latest_payload,
            trade_state_payloads
        )
        
        return trade
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trade: {str(e)}")


@router.get("/trades/{trade_id}/timeline")
async def get_trade_timeline(trade_id: str):
    """Get trade timeline/events only"""
    try:
        timeline_data = await get_trade_lineage(trade_id)
        
        if not timeline_data.get("timeline"):
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
        
        # Get trade state payloads for transformation
        trade_state_payloads = {}
        for entry in timeline_data["timeline"]:
            trade_state_id = entry.get("trade_state_id")
            try:
                payload = await get_tradestate_payload(trade_state_id)
                trade_state_payloads[trade_state_id] = payload
            except Exception:
                continue
        
        events = transform_timeline_to_events(timeline_data, trade_state_payloads)
        
        return {"events": events}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching timeline: {str(e)}")


@router.get("/trades/{trade_id}/state/{trade_state_id}")
async def get_trade_state(trade_id: str, trade_state_id: str):
    """Get specific trade state payload (for CDM Output tab)"""
    try:
        payload = await get_tradestate_payload(trade_state_id)
        return {"payload": payload}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trade state: {str(e)}")


@router.get("/debug/trades")
async def debug_trades():
    """Debug endpoint to check database connection and data"""
    try:
        # Check database connection
        test_query = q(cnx, "SELECT COUNT(*) as count FROM trade_state")
        total_states = test_query[0]["count"] if test_query else 0
        
        # Get trade IDs
        trade_ids_query = q(cnx, "SELECT DISTINCT trade_id FROM trade_state ORDER BY trade_id LIMIT 10")
        trade_ids_list = [row["trade_id"] for row in trade_ids_query]
        
        # Check if we have CDM outputs
        cdm_outputs_query = q(cnx, "SELECT COUNT(*) as count FROM cdm_outputs WHERE object_type='TradeState'")
        cdm_outputs_count = cdm_outputs_query[0]["count"] if cdm_outputs_query else 0
        
        return {
            "database_connected": True,
            "total_trade_states": total_states,
            "unique_trade_ids": len(trade_ids_list),
            "trade_ids_sample": trade_ids_list,
            "cdm_outputs_count": cdm_outputs_count
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}", exc_info=True)
        return {
            "database_connected": False,
            "error": str(e)
        }


@router.get("/debug/trade/{trade_id}")
async def debug_trade_detail(trade_id: str):
    """Debug endpoint to inspect a single trade's processing"""
    debug_info = {
        "trade_id": trade_id,
        "steps": []
    }
    
    try:
        # Step 1: Get trade states
        debug_info["steps"].append("Step 1: Getting trade states")
        states_result = await get_trade_states(trade_id)
        debug_info["states_count"] = len(states_result.get("states", []))
        debug_info["states"] = states_result.get("states", [])
        
        if not states_result.get("states"):
            debug_info["error"] = "No states found for trade"
            return debug_info
        
        # Step 2: Get timeline
        debug_info["steps"].append("Step 2: Getting timeline")
        timeline = await get_trade_lineage(trade_id)
        debug_info["timeline_count"] = len(timeline.get("timeline", []))
        debug_info["timeline"] = timeline.get("timeline", [])
        
        if not timeline.get("timeline"):
            debug_info["error"] = "Timeline is empty"
            return debug_info
        
        # Step 3: Get latest state payload
        debug_info["steps"].append("Step 3: Getting latest state payload")
        latest_state_id = timeline["timeline"][-1]["trade_state_id"]
        debug_info["latest_state_id"] = latest_state_id
        
        try:
            latest_payload = await get_tradestate_payload(latest_state_id)
            debug_info["payload_keys"] = list(latest_payload.keys()) if isinstance(latest_payload, dict) else "Not a dict"
            debug_info["payload_sample"] = str(latest_payload)[:500] if latest_payload else None
            
            # Step 4: Try extraction
            debug_info["steps"].append("Step 4: Extracting fields")
            product_type = extract_product_type(latest_payload)
            notional_val = extract_notional(latest_payload)
            currency = extract_currency(latest_payload)
            
            debug_info["extracted"] = {
                "product_type": product_type,
                "notional": notional_val,
                "currency": currency
            }
            
            debug_info["success"] = True
            
        except Exception as e:
            debug_info["payload_error"] = str(e)
            debug_info["payload_error_type"] = type(e).__name__
            
            # Try to get raw payload from database
            try:
                raw_rec = one(cnx, """SELECT payload_json FROM cdm_outputs
                                     WHERE object_type='TradeState' AND trade_state_id=%s
                                     ORDER BY created_at DESC LIMIT 1""", (latest_state_id,))
                if raw_rec:
                    debug_info["raw_payload_keys"] = list(raw_rec["payload_json"].keys()) if isinstance(raw_rec["payload_json"], dict) else "Not a dict"
                    debug_info["raw_payload_structure"] = str(raw_rec["payload_json"])[:500]
            except Exception as e2:
                debug_info["raw_payload_error"] = str(e2)
        
    except Exception as e:
        debug_info["error"] = str(e)
        debug_info["error_type"] = type(e).__name__
        import traceback
        debug_info["traceback"] = traceback.format_exc()
    
    return debug_info
