from typing import Dict, Any
from decimal import Decimal
from repository.transaction_repo import TransactionRepository
from schemas.schemas import TransactionCreate


class TransactionService:
    def __init__(self, repo: TransactionRepository):
        self.repo = repo

    async def create_transaction(self, data: dict) -> dict:
        # process product details
        product_detail = self._process_product_details(data)

        # prepare transaction data
        transaction_dict = self._build_transaction_data(data, product_detail)

        # validate and save
        transaction_data = TransactionCreate(**transaction_dict)
        transaction_id = await self.repo.save_transaction(transaction_data)

        return {"status": "success", "transaction_id": transaction_id}

    def _process_product_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        products = data.get("detail", [])
        product_detail = {}

        if products:
            if len(products) > 1:
                for idx, product in enumerate(products, 1):
                    key = f"{data['trans_id']}_{idx}"
                    product_detail[key] = product

            else:
                product_detail[data["trans_id"]] = product[0]
            return product_detail

    def _build_transaction_data(self, data: Dict[str, Any], product_detail: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data["trans_id"],
            "ts": data.get("ts", 0),
            "status": data.get("transaction_status", "pending"),
            "amount": data.get("transaction_amount", 0),
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
                    "mdr_qris": float(Decimal("0.0007") * Decimal(data.get("transaction_amount", 0))),
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
