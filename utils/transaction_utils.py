from decimal import Decimal


def build_transaction_dict(data: dict) -> dict:
    product_detail = {}

     # Coba ambil langsung kalau user ngirim "product_detail" langsung
    if "product_detail" in data:
        product_detail = data["product_detail"]

    # Kalau tidak ada, dan ada "detail" (list of products), olah jadi product_detail
    elif "detail" in data:
        products = data["detail"]
        if isinstance(products, list) and products:
            if len(products) > 1:
                for idx, product in enumerate(products, 1):
                    key = f"{data['id']}_{idx}"
                    product_detail[key] = product
            else:
                product_detail[data["id"]] = products[0]

    return {
        "id": data["id"],
        "ts": data.get("ts", 0),
        "status": data.get("transaction_status", data.get("status", "pending")),
        "amount": data.get("transaction_amount", data.get("amount", 0)),
        "payment_method": data.get("payment_method", "unknown"),
        "device_id": data.get("device_id", ""),
        "device_tags": data.get("device_tags", []),
        "dispense_code": data.get("dispense_code", 0),
        "payment_detail": {
            "detail": {
                "issuer": data.get("issuer"),
                "order_id": data.get("order_id"),
                "transaction_id": data.get("transaction_id"),
                "transaction_time": data.get("transaction_time"),
            },
            "fee": {
                "mdr_qris": float(Decimal("0.0007") * Decimal(data.get("transaction_amount", data.get("amount", 0)))),
                "landlord_sharing_revenue": 0.0,
                "platform_sharing_revenue": 0.0
            },
            "net": data.get("net")
        },
        "device_detail": {
            "device_name": data.get("device_name", "")
        },
        "dispense_detail": {
            "dispense_status": data.get("dispense_status", "unknown"),
            "dispense_ts": data.get("time", data.get("ts", 0))
        },
        "product_detail": product_detail,
        "refund_detail": data.get("refund_detail", {}),
        "extras": data.get("extras", {})
    }
    
