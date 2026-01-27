def has_market_changed(latest_market, issue_name, current_price):
    """
    Returns True if any price in new_market differs from latest_market.
    Returns False if all prices match or items are new.
    """
    # Create a lookup map of {name: price} from the database records
    db_prices = {item['issue_name']: item['current_price'] for item in latest_market}

    # We only care about changes to EXISTING items
    if issue_name in db_prices:
        if db_prices[issue_name] != current_price:
            return True 
                
    return False# no change
