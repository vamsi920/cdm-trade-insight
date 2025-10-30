"""
Trade state diff utilities for CDM MCP Provider
"""
from typing import Any, List, Dict, Optional

def notional(trade_state: Dict[str, Any]) -> Optional[float]:
    """Extract notional amount from trade state payload"""
    try:
        # Navigate through CDM JSON structure
        trade = trade_state.get('trade', {})
        tradable_product = trade.get('tradableProduct', {})
        product = tradable_product.get('product', {})
        economic_terms = product.get('economicTerms', {})
        payout = economic_terms.get('payout', {})
        
        # Look for notional in various payout types
        for payout_type in ['interestRatePayout', 'equityPayout', 'creditDefaultSwapPayout']:
            if payout_type in payout:
                payouts = payout[payout_type]
                if isinstance(payouts, list) and payouts:
                    quantity = payouts[0].get('quantity', {})
                    return quantity.get('value')
        return None
    except (KeyError, TypeError, IndexError):
        return None

def fixed_rate(trade_state: Dict[str, Any]) -> Optional[float]:
    """Extract fixed rate from trade state payload"""
    try:
        # Navigate through CDM JSON structure for interest rate products
        trade = trade_state.get('trade', {})
        tradable_product = trade.get('tradableProduct', {})
        product = tradable_product.get('product', {})
        economic_terms = product.get('economicTerms', {})
        payout = economic_terms.get('payout', {})
        
        # Look for fixed rate in interest rate payout
        if 'interestRatePayout' in payout:
            payouts = payout['interestRatePayout']
            if isinstance(payouts, list) and payouts:
                rate_schedule = payouts[0].get('rateSpecification', {}).get('rateSchedule', {})
                if rate_schedule:
                    rate = rate_schedule.get('rate', {})
                    return rate.get('value')
        return None
    except (KeyError, TypeError, IndexError):
        return None

def changed(old_val: Any, new_val: Any) -> Dict[str, Any]:
    """Return dict with from, to, and changed flag"""
    return {
        "from": old_val,
        "to": new_val,
        "changed": old_val != new_val
    }

def appended(old_list: List[Any], new_list: List[Any]) -> List[Any]:
    """Return newly added items"""
    if not old_list:
        return new_list
    if not new_list:
        return []
    
    # Simple approach: return items in new_list not in old_list
    # For more complex CDM objects, this might need custom comparison logic
    return [item for item in new_list if item not in old_list]




