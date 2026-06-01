def calculate_commission(amount):
    if amount <= 100000:
        return amount * 0.05
    elif amount <= 500000:
        return amount * 0.07
    else:
        return amount * 0.10