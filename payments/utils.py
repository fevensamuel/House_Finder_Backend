def calculate_commission(amount):
    if amount <= 100000:
        return amount * 0.05
    elif amount <= 500000:
        return amount * 0.07
    else:
        return amount * 0.10

def calculate_commission(amount):
    if amount <= 100000:
        return amount * 0.05
    elif amount <= 500000:
        return amount * 0.04
    elif amount <= 1000000:
        return amount * 0.03
    else:
        return amount * 0.025

def get_featured_price(plan, quantity):
    base_monthly = 500  # ETB per listing per month
    if plan == 'yearly':
        base_price_per_listing = base_monthly * 12 * 0.8
    else:
        base_price_per_listing = base_monthly
    total = base_price_per_listing * quantity
    if quantity == 2:
        total *= 0.9
    elif quantity >= 3:
        total *= 0.8
    return round(total, 2)