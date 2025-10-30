"""
Data transformation utilities to convert database/CDM format to frontend TypeScript types
"""
from typing import Dict, Any, List, Optional
from common.diff import notional

# Event type mapping from backend event_type to frontend EventType
EVENT_TYPE_MAP = {
    "Execution": "Execution",
    "Confirmation": "Confirmation",
    "Amendment": "Amendment",
    "Termination": "Termination",
    "Settlement": "Settlement",
    "Reset": "Amendment",  # Map Reset to Amendment for now
    "Transfer": "Novation"  # Map Transfer to Novation
}

# Position state to Trade status mapping
POSITION_STATE_TO_STATUS = {
    "EXECUTED": "Pending",
    "CONFIRMED": "Active",
    "CLEARED": "Active",
    "TERMINATED": "Terminated",
    "AMENDED": "Active"
}


def map_event_type(backend_event_type: str) -> str:
    """Map backend event_type to frontend EventType enum"""
    return EVENT_TYPE_MAP.get(backend_event_type, "Execution")


def extract_product_type(trade_state_payload: Dict[str, Any]) -> str:
    """Extract product type from TradeState CDM payload"""
    try:
        trade = trade_state_payload.get('trade', {})
        tradable_product = trade.get('tradableProduct', {})
        product = tradable_product.get('product', {})
        product_type_obj = product.get('productType', {})
        if isinstance(product_type_obj, dict):
            return product_type_obj.get('value', 'Unknown')
        return str(product_type_obj) if product_type_obj else 'Unknown'
    except (KeyError, TypeError, AttributeError):
        return 'Unknown'


def extract_parties(trade_state_payload: Dict[str, Any]) -> Dict[str, str]:
    """Extract bank and counterparty names from TradeState CDM payload
    
    Returns: {'bank': 'Bank Name', 'counterparty': 'Counterparty Name'}
    """
    result = {'bank': 'Unknown', 'counterparty': 'Unknown'}
    try:
        trade = trade_state_payload.get('trade', {})
        party_roles = trade.get('partyRole', [])
        
        for role in party_roles:
            role_type = role.get('role', {})
            role_name = role_type.get('value', '').upper() if isinstance(role_type, dict) else str(role_type).upper()
            party = role.get('party', {})
            party_ids = party.get('partyId', [])
            
            if party_ids:
                identifier = party_ids[0].get('identifier', {})
                party_name = identifier.get('value', '') if isinstance(identifier, dict) else str(identifier)
                
                # Map role to bank/counterparty
                if 'BANK' in role_name or 'PARTY' in role_name or 'SELLER' in role_name:
                    if result['bank'] == 'Unknown':
                        result['bank'] = party_name
                else:
                    if result['counterparty'] == 'Unknown':
                        result['counterparty'] = party_name
                
                # If we have two parties but bank is still Unknown, use first as bank
                if len([p for p in party_roles if p.get('party', {}).get('partyId')]) >= 2:
                    if result['counterparty'] != 'Unknown' and result['bank'] == 'Unknown':
                        result['bank'] = result['counterparty']
    except (KeyError, TypeError, AttributeError, IndexError):
        pass
    
    return result


def extract_dates(trade_state_payload: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Extract start date and maturity date from TradeState CDM payload
    
    Returns: {'startDate': 'YYYY-MM-DD', 'maturityDate': 'YYYY-MM-DD'}
    """
    result = {'startDate': None, 'maturityDate': None}
    try:
        trade = trade_state_payload.get('trade', {})
        tradable_product = trade.get('tradableProduct', {})
        product = tradable_product.get('product', {})
        economic_terms = product.get('economicTerms', {})
        contract_terms = economic_terms.get('contractTerms', {})
        
        # Extract dates from contractTerms
        dated = contract_terms.get('dated', {})
        if isinstance(dated, dict):
            result['startDate'] = dated.get('value', '').split('T')[0] if dated.get('value') else None
        
        # Extract maturity/termination date
        termination_events = contract_terms.get('terminationEvent', [])
        if termination_events and isinstance(termination_events, list):
            for event in termination_events:
                event_date = event.get('dated', {})
                if isinstance(event_date, dict):
                    date_val = event_date.get('value', '').split('T')[0] if event_date.get('value') else None
                    if date_val:
                        result['maturityDate'] = date_val
                        break
        
        # Fallback: try to get from schedule
        if not result['maturityDate']:
            schedule = contract_terms.get('schedule', {})
            if schedule:
                schedule_period = schedule.get('period', [])
                if schedule_period and isinstance(schedule_period, list):
                    last_period = schedule_period[-1]
                    end_date = last_period.get('endDate', {})
                    if isinstance(end_date, dict):
                        result['maturityDate'] = end_date.get('value', '').split('T')[0] if end_date.get('value') else None
    except (KeyError, TypeError, AttributeError, IndexError):
        pass
    
    return result


def extract_currency(trade_state_payload: Dict[str, Any]) -> str:
    """Extract currency from TradeState CDM payload"""
    try:
        notional_val = notional(trade_state_payload)
        if notional_val is None:
            # Try to get from quantity
            trade = trade_state_payload.get('trade', {})
            tradable_product = trade.get('tradableProduct', {})
            product = tradable_product.get('product', {})
            economic_terms = product.get('economicTerms', {})
            payout = economic_terms.get('payout', {})
            
            for payout_type in ['interestRatePayout', 'equityPayout', 'creditDefaultSwapPayout']:
                if payout_type in payout:
                    payouts = payout[payout_type]
                    if isinstance(payouts, list) and payouts:
                        quantity = payouts[0].get('quantity', {})
                        if isinstance(quantity, dict):
                            unit = quantity.get('unit', {})
                            if isinstance(unit, dict):
                                return unit.get('value', 'USD')
        else:
            # Try to get currency from notional context
            trade = trade_state_payload.get('trade', {})
            tradable_product = trade.get('tradableProduct', {})
            product = tradable_product.get('product', {})
            economic_terms = product.get('economicTerms', {})
            payout = economic_terms.get('payout', {})
            
            for payout_type in ['interestRatePayout', 'equityPayout', 'creditDefaultSwapPayout']:
                if payout_type in payout:
                    payouts = payout[payout_type]
                    if isinstance(payouts, list) and payouts:
                        quantity = payouts[0].get('quantity', {})
                        if isinstance(quantity, dict):
                            unit = quantity.get('unit', {})
                            if isinstance(unit, dict):
                                return unit.get('value', 'USD')
    except (KeyError, TypeError, AttributeError, IndexError):
        pass
    
    return 'USD'  # Default currency


def generate_event_description(event_type: str, intent: str, position_state: str) -> str:
    """Generate a human-readable description for an event"""
    if event_type == "Execution":
        return "Initial trade execution"
    elif event_type == "Confirmation":
        return "Trade confirmation received"
    elif event_type == "Amendment":
        return f"Trade amendment - {intent if intent != 'UNKNOWN' else 'terms modified'}"
    elif event_type == "Settlement":
        return "Trade settlement completed"
    elif event_type == "Termination":
        return "Trade terminated"
    elif event_type == "Novation":
        return "Trade novation completed"
    else:
        return f"{event_type} event"


def transform_timeline_to_events(timeline_data: Dict[str, Any], trade_state_payloads: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert timeline from get_trade_lineage() to frontend TradeEvent[] format
    
    Args:
        timeline_data: Result from get_trade_lineage()
        trade_state_payloads: Dict mapping trade_state_id -> TradeState payload
    
    Returns:
        List of TradeEvent dictionaries
    """
    events = []
    timeline = timeline_data.get('timeline', [])
    
    for entry in timeline:
        trade_state_id = entry.get('trade_state_id')
        payload = trade_state_payloads.get(trade_state_id, {})
        
        # Extract notional and currency from payload
        notional_val = notional(payload)
        currency = extract_currency(payload)
        
        # Extract party (simplified - use first party found)
        parties = extract_parties(payload)
        party = parties.get('bank', parties.get('counterparty', 'Unknown'))
        
        # Generate description
        description = generate_event_description(
            entry.get('event_type', ''),
            entry.get('intent', ''),
            entry.get('position_state', '')
        )
        
        event = {
            "id": entry.get('event_id', ''),
            "type": map_event_type(entry.get('event_type', 'Execution')),
            "date": entry.get('date', '') or entry.get('as_of', ''),
            "description": description,
            "party": party,
            "notionalValue": notional_val,
            "currency": currency,
            "narrative": None,  # Will be generated later via LLM
            "metadata": {
                "trade_state_id": trade_state_id,
                "version": entry.get('version'),
                "intent": entry.get('intent'),
                "position_state": entry.get('position_state')
            }
        }
        events.append(event)
    
    return events


def transform_to_trade(
    trade_id: str,
    timeline_data: Dict[str, Any],
    latest_trade_state_payload: Dict[str, Any],
    trade_state_payloads: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert timeline and trade state data to frontend Trade format
    
    Args:
        trade_id: Trade identifier
        timeline_data: Result from get_trade_lineage()
        latest_trade_state_payload: Latest TradeState payload
        trade_state_payloads: Dict mapping trade_state_id -> TradeState payload
    
    Returns:
        Trade dictionary matching frontend Trade interface
    """
    # Extract basic info from latest state
    product_type = extract_product_type(latest_trade_state_payload)
    parties = extract_parties(latest_trade_state_payload)
    notional_val = notional(latest_trade_state_payload) or 0.0
    currency = extract_currency(latest_trade_state_payload)
    dates = extract_dates(latest_trade_state_payload)
    
    # Map position state to status
    latest_state = timeline_data.get('timeline', [{}])[-1] if timeline_data.get('timeline') else {}
    position_state = latest_state.get('position_state', '')
    status = POSITION_STATE_TO_STATUS.get(position_state, 'Active')
    
    # Transform events
    events = transform_timeline_to_events(timeline_data, trade_state_payloads)
    
    return {
        "id": trade_id,
        "productType": product_type,
        "counterparty": parties.get('counterparty', 'Unknown'),
        "bank": parties.get('bank', 'Unknown'),
        "currentNotional": notional_val,
        "currency": currency,
        "startDate": dates.get('startDate', ''),
        "maturityDate": dates.get('maturityDate', ''),
        "status": status,
        "events": events,
        "narrative": None  # Will be generated later via LLM
    }

