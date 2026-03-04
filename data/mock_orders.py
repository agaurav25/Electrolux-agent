import json
from datetime import datetime, timedelta
import random

MOCK_ORDERS = [
    {
        "order_id": "ORD-1001",
        "customer_name": "Acme Corp",
        "region": "North America",
        "order_created_time": (datetime.now() - timedelta(hours=2)).isoformat(),
        "payment_status": "Authorized",
        "erp_status": "Confirmed",
        "fulfillment_status": "Shipped",
        "shipment_status": "In Transit",
        "sla_threshold": 4.0,
        "processing_time": 1.8,
        "order_value": 12500.00,
        "priority": "Standard",
        "integration_error_logs": []
    },
    {
        "order_id": "ORD-1002",
        "customer_name": "TechVentures Inc",
        "region": "Europe",
        "order_created_time": (datetime.now() - timedelta(hours=6)).isoformat(),
        "payment_status": "Failed",
        "erp_status": "Pending",
        "fulfillment_status": "Not Started",
        "shipment_status": "Not Initiated",
        "sla_threshold": 4.0,
        "processing_time": 6.2,
        "order_value": 8750.00,
        "priority": "High",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=5, minutes=45)).isoformat(), "system": "Payment Gateway", "error_code": "PG-401", "message": "Payment authorization declined – insufficient funds", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=5, minutes=30)).isoformat(), "system": "Payment Gateway", "error_code": "PG-401", "message": "Retry #1 – authorization declined", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=4)).isoformat(), "system": "OMS", "error_code": "OMS-100", "message": "Order held – payment not cleared", "severity": "Warning"}
        ]
    },
    {
        "order_id": "ORD-1003",
        "customer_name": "Global Supplies Ltd",
        "region": "Asia Pacific",
        "order_created_time": (datetime.now() - timedelta(hours=8)).isoformat(),
        "payment_status": "Authorized",
        "erp_status": "Stuck – Submission Error",
        "fulfillment_status": "Blocked",
        "shipment_status": "Not Initiated",
        "sla_threshold": 4.0,
        "processing_time": 8.1,
        "order_value": 22000.00,
        "priority": "Critical",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=7, minutes=50)).isoformat(), "system": "ERP", "error_code": "ERP-503", "message": "ERP service unavailable – connection timeout after 30s", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=7)).isoformat(), "system": "ERP", "error_code": "ERP-503", "message": "Retry #1 – ERP submission failed, service down", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=6)).isoformat(), "system": "ERP", "error_code": "ERP-504", "message": "Retry #2 – gateway timeout", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=5)).isoformat(), "system": "OMS", "error_code": "OMS-200", "message": "Order flagged for manual ERP intervention", "severity": "Warning"}
        ]
    },
    {
        "order_id": "ORD-1004",
        "customer_name": "FastTrack Logistics",
        "region": "North America",
        "order_created_time": (datetime.now() - timedelta(hours=10)).isoformat(),
        "payment_status": "Authorized",
        "erp_status": "Confirmed",
        "fulfillment_status": "Packed",
        "shipment_status": "Delayed – Carrier Issue",
        "sla_threshold": 6.0,
        "processing_time": 10.3,
        "order_value": 5200.00,
        "priority": "Standard",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=4)).isoformat(), "system": "Logistics", "error_code": "LOG-300", "message": "Carrier pickup delayed – warehouse congestion", "severity": "Warning"},
            {"timestamp": (datetime.now() - timedelta(hours=3)).isoformat(), "system": "Logistics", "error_code": "LOG-301", "message": "Carrier rescheduled pickup – next available slot in 4 hours", "severity": "Warning"},
            {"timestamp": (datetime.now() - timedelta(hours=1)).isoformat(), "system": "Logistics", "error_code": "LOG-302", "message": "Shipment tracking ID not generated", "severity": "Info"}
        ]
    },
    {
        "order_id": "ORD-1005",
        "customer_name": "Premier Electronics",
        "region": "Europe",
        "order_created_time": (datetime.now() - timedelta(hours=14)).isoformat(),
        "payment_status": "Authorized",
        "erp_status": "Confirmed",
        "fulfillment_status": "Processing",
        "shipment_status": "Not Initiated",
        "sla_threshold": 4.0,
        "processing_time": 14.0,
        "order_value": 45000.00,
        "priority": "Critical",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=10)).isoformat(), "system": "Fulfillment", "error_code": "FUL-400", "message": "Warehouse allocation failed – stock discrepancy", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=8)).isoformat(), "system": "Fulfillment", "error_code": "FUL-401", "message": "Manual stock recount requested", "severity": "Warning"},
            {"timestamp": (datetime.now() - timedelta(hours=6)).isoformat(), "system": "ERP", "error_code": "ERP-200", "message": "Inventory sync mismatch – ERP vs WMS delta: 12 units", "severity": "Warning"},
            {"timestamp": (datetime.now() - timedelta(hours=4)).isoformat(), "system": "OMS", "error_code": "OMS-300", "message": "SLA breach alert triggered", "severity": "Critical"}
        ]
    },
    {
        "order_id": "ORD-1006",
        "customer_name": "MedSupply Co",
        "region": "North America",
        "order_created_time": (datetime.now() - timedelta(hours=5)).isoformat(),
        "payment_status": "Authorized",
        "erp_status": "Confirmed",
        "fulfillment_status": "Partially Fulfilled",
        "shipment_status": "Partial Shipment",
        "sla_threshold": 6.0,
        "processing_time": 5.0,
        "order_value": 18500.00,
        "priority": "High",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=3)).isoformat(), "system": "Fulfillment", "error_code": "FUL-402", "message": "2 of 5 line items out of stock – partial fulfillment initiated", "severity": "Warning"},
            {"timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(), "system": "Logistics", "error_code": "LOG-200", "message": "Partial shipment created – 3 of 5 items", "severity": "Info"},
            {"timestamp": (datetime.now() - timedelta(hours=2)).isoformat(), "system": "OMS", "error_code": "OMS-150", "message": "Backorder created for remaining 2 items", "severity": "Info"}
        ]
    },
    {
        "order_id": "ORD-1007",
        "customer_name": "CloudFirst Solutions",
        "region": "Asia Pacific",
        "order_created_time": (datetime.now() - timedelta(hours=3)).isoformat(),
        "payment_status": "Processing",
        "erp_status": "Pending",
        "fulfillment_status": "Not Started",
        "shipment_status": "Not Initiated",
        "sla_threshold": 4.0,
        "processing_time": 3.0,
        "order_value": 9800.00,
        "priority": "Standard",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=2, minutes=50)).isoformat(), "system": "Payment Gateway", "error_code": "PG-504", "message": "API timeout – gateway did not respond within 60s", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(), "system": "Payment Gateway", "error_code": "PG-504", "message": "Retry #1 – API timeout persists", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=2)).isoformat(), "system": "OMS", "error_code": "OMS-100", "message": "Payment confirmation pending – order on hold", "severity": "Warning"}
        ]
    },
    {
        "order_id": "ORD-1008",
        "customer_name": "Retail Giants LLC",
        "region": "Europe",
        "order_created_time": (datetime.now() - timedelta(hours=7)).isoformat(),
        "payment_status": "Failed",
        "erp_status": "Rejected",
        "fulfillment_status": "Cancelled",
        "shipment_status": "Not Initiated",
        "sla_threshold": 4.0,
        "processing_time": 7.0,
        "order_value": 33000.00,
        "priority": "Critical",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=6, minutes=50)).isoformat(), "system": "Payment Gateway", "error_code": "PG-403", "message": "Payment declined – fraud detection triggered", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=6, minutes=30)).isoformat(), "system": "ERP", "error_code": "ERP-600", "message": "Order rejected – payment validation failed", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=6)).isoformat(), "system": "OMS", "error_code": "OMS-400", "message": "Order auto-cancelled due to payment + ERP failure", "severity": "Critical"},
            {"timestamp": (datetime.now() - timedelta(hours=5)).isoformat(), "system": "OMS", "error_code": "OMS-401", "message": "Customer notification sent – order cancelled", "severity": "Info"}
        ]
    },
    {
        "order_id": "ORD-1009",
        "customer_name": "DataBridge Corp",
        "region": "North America",
        "order_created_time": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
        "payment_status": "Authorized",
        "erp_status": "Confirmed",
        "fulfillment_status": "Processing",
        "shipment_status": "Not Initiated",
        "sla_threshold": 4.0,
        "processing_time": 3.5,
        "order_value": 15600.00,
        "priority": "High",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=1)).isoformat(), "system": "Fulfillment", "error_code": "FUL-100", "message": "Warehouse picking in progress – estimated 1h remaining", "severity": "Info"},
            {"timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(), "system": "OMS", "error_code": "OMS-250", "message": "SLA at-risk alert – 87% of threshold consumed", "severity": "Warning"}
        ]
    },
    {
        "order_id": "ORD-1010",
        "customer_name": "QuickShip International",
        "region": "Asia Pacific",
        "order_created_time": (datetime.now() - timedelta(hours=9)).isoformat(),
        "payment_status": "Authorized",
        "erp_status": "Confirmed",
        "fulfillment_status": "Packed",
        "shipment_status": "Delayed – Hub Congestion",
        "sla_threshold": 6.0,
        "processing_time": 9.0,
        "order_value": 7400.00,
        "priority": "Standard",
        "integration_error_logs": [
            {"timestamp": (datetime.now() - timedelta(hours=5)).isoformat(), "system": "Logistics", "error_code": "LOG-310", "message": "Regional hub congestion – estimated 6h delay", "severity": "Warning"},
            {"timestamp": (datetime.now() - timedelta(hours=3)).isoformat(), "system": "Logistics", "error_code": "LOG-311", "message": "Alternative routing being evaluated", "severity": "Info"},
            {"timestamp": (datetime.now() - timedelta(hours=2)).isoformat(), "system": "Logistics", "error_code": "LOG-312", "message": "Rerouted via secondary hub – pickup scheduled", "severity": "Info"}
        ]
    }
]


def get_all_orders():
    return MOCK_ORDERS


def get_order_by_id(order_id):
    for order in MOCK_ORDERS:
        if order["order_id"].upper() == order_id.upper():
            return order
    return None


def get_order_ids():
    return [order["order_id"] for order in MOCK_ORDERS]
