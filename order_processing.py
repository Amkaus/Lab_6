# Константы
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
DISCOUNT_RATES = {
    "SAVE10": 0.10,
    "SAVE20_LARGE": 0.20,
    "SAVE20_SMALL": 0.05
}
DISCOUNT_THRESHOLD_SAVE20 = 200
DISCOUNT_THRESHOLD_VIP = 100
VIP_DISCOUNT = 50
SMALL_ORDER_VIP_DISCOUNT = 10
MIN_PRICE = 0
MIN_QTY = 0

def parse_request(request: dict):
    return (
        request.get("user_id"),
        request.get("items"),
        request.get("coupon"),
        request.get("currency")
    )

def validate_request(user_id, items, currency):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if currency is None:
        currency = DEFAULT_CURRENCY

    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    return currency

def validate_items(items):
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= MIN_PRICE:
            raise ValueError("price must be positive")
        if item["qty"] <= MIN_QTY:
            raise ValueError("qty must be positive")

def calculate_subtotal(items):
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_discount(coupon, subtotal):
    if not coupon or coupon == "":
        return 0

    if coupon == "SAVE10":
        return int(subtotal * DISCOUNT_RATES["SAVE10"])
    if coupon == "SAVE20":
        if subtotal >= DISCOUNT_THRESHOLD_SAVE20:
            return int(subtotal * DISCOUNT_RATES["SAVE20_LARGE"])
        else:
            return int(subtotal * DISCOUNT_RATES["SAVE20_SMALL"])
    if coupon == "VIP":
        if subtotal >= DISCOUNT_THRESHOLD_VIP:
            return VIP_DISCOUNT
        else:
            return SMALL_ORDER_VIP_DISCOUNT
    raise ValueError("unknown coupon")


def calculate_tax(amount):
    return int(amount * TAX_RATE)

def generate_order_id(user_id, items_count):
    return f"{user_id}-{items_count}-X"


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)
    currency = validate_request(user_id, items, currency)
    validate_items(items)
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(coupon, subtotal)
    total_after_discount = subtotal - discount

    if total_after_discount < 0:
        total_after_discount = 0

    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax
    order_id = generate_order_id(user_id, len(items))

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }