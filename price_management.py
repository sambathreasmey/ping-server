def has_market_changed(latest_market, new_market):
    """
    Returns True if any price in new_market differs from latest_market.
    Returns False if all prices match or items are new.
    """
    # Create a lookup map of {name: price} from the database records
    db_prices = {item['issue_name']: item['current_price'] for item in latest_market}

    # Check if any item's price is different from what we have in the DB
    for item in new_market:
        name = item.get("issueName")
        new_price = item.get("currentPrice")
        
        # We only care about changes to EXISTING items
        if name in db_prices:
            if db_prices[name] != new_price:
                return True 
                
    return False# no change
