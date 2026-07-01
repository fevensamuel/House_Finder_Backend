from decimal import Decimal

def calculate_commission(amount):
    """Return commission as a Decimal."""
    if amount <= Decimal('100000'):
        return amount * Decimal('0.05')
    elif amount <= Decimal('500000'):
        return amount * Decimal('0.04')
    elif amount <= Decimal('1000000'):
        return amount * Decimal('0.03')
    else:
        return amount * Decimal('0.025')

def get_featured_price(quantity):
    if quantity == 1:
        return Decimal('300')
    elif quantity == 2:
        return Decimal('500')
    elif quantity == 3:
        return Decimal('675')
    elif quantity == 4:
        return Decimal('800')
    else:
        return Decimal('800') + (quantity - 4) * Decimal('180')