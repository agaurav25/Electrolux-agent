import os
from utils.logger import log_investigation


def generate_customer_response(investigation_result, sla_result, diagnostic_result, resolution_result):
    if not investigation_result:
        return None

    order = investigation_result["order"]
    order_id = order["order_id"]
    log_investigation(order_id, "CustomerCommAgent", "Generating customer response")

    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        response = _generate_with_groq(groq_key, order, diagnostic_result, resolution_result)
    else:
        response = _generate_simulated(order, diagnostic_result, resolution_result)

    log_investigation(order_id, "CustomerCommAgent", "Customer response generated")
    return response


def _generate_with_groq(api_key, order, diagnostic_result, resolution_result):
    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        has_issues = diagnostic_result and diagnostic_result.get("has_issues", False)
        category = diagnostic_result.get("failure_category", "None") if has_issues else "None"
        est_resolution = resolution_result.get("estimated_resolution", "under investigation") if resolution_result else "under investigation"

        prompt = f"""You are a customer service AI assistant for an enterprise order management company.
Generate a professional, empathetic customer response for the following order issue.

Order ID: {order['order_id']}
Customer: {order['customer_name']}
Current Status: {order['fulfillment_status']}
Shipment Status: {order['shipment_status']}
Issue Category: {category}
Estimated Resolution: {est_resolution}

Guidelines:
- Be professional and empathetic
- Do NOT use technical jargon (no error codes, system names, or API references)
- Explain what happened in simple terms
- Provide the estimated resolution timeline
- Assure the customer their order is being prioritized
- Keep it concise (3-4 paragraphs)
- Do NOT make up specific tracking numbers or agent names
- Sign off as "Electrolux Order Support Team"
"""

        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        return {
            "message": completion.choices[0].message.content,
            "estimated_resolution": est_resolution,
            "generated_by": "AI (Groq LLM)"
        }
    except Exception as e:
        return _generate_simulated(order, diagnostic_result, resolution_result)


def _generate_simulated(order, diagnostic_result, resolution_result):
    has_issues = diagnostic_result and diagnostic_result.get("has_issues", False)
    category = diagnostic_result.get("failure_category", "None") if has_issues else "None"
    est_resolution = resolution_result.get("estimated_resolution", "under investigation") if resolution_result else "under investigation"

    templates = {
        "Payment Authorization Failure": (
            f"Dear {order['customer_name']},\n\n"
            f"Thank you for reaching out regarding your order {order['order_id']}. "
            f"We have identified that there was an issue processing your payment. "
            f"The payment could not be authorized with the details on file.\n\n"
            f"To resolve this, we kindly ask you to verify your payment information "
            f"or provide an alternative payment method. Once updated, we will "
            f"immediately resume processing your order.\n\n"
            f"Estimated resolution: {est_resolution}.\n\n"
            f"We apologize for the inconvenience and appreciate your patience.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "Payment Gateway Timeout": (
            f"Dear {order['customer_name']},\n\n"
            f"Thank you for contacting us about order {order['order_id']}. "
            f"We experienced a temporary technical issue while processing your payment. "
            f"Our team has already initiated a retry and is actively monitoring the situation.\n\n"
            f"No action is needed from your side at this time. "
            f"We expect this to be resolved within {est_resolution}.\n\n"
            f"We sincerely apologize for the delay and will notify you once your order is confirmed.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "Fraud Detection Block": (
            f"Dear {order['customer_name']},\n\n"
            f"Thank you for your patience regarding order {order['order_id']}. "
            f"As part of our standard security procedures, your order requires "
            f"additional verification before it can be processed.\n\n"
            f"Our security team will reach out to you shortly to verify some details. "
            f"This is a standard procedure to protect your account.\n\n"
            f"Estimated timeline: {est_resolution}.\n\n"
            f"We appreciate your understanding.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "ERP Service Outage": (
            f"Dear {order['customer_name']},\n\n"
            f"We are writing to update you on order {order['order_id']}. "
            f"We are currently experiencing a temporary system issue that has "
            f"delayed the processing of your order.\n\n"
            f"Our technical team is working to resolve this as quickly as possible. "
            f"Your order details are saved and will be processed automatically "
            f"once the issue is resolved.\n\n"
            f"Expected resolution: {est_resolution}.\n\n"
            f"We apologize for any inconvenience.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "ERP Submission Error": (
            f"Dear {order['customer_name']},\n\n"
            f"Thank you for your order {order['order_id']}. "
            f"We encountered a processing delay while confirming your order "
            f"in our system. Our team has been notified and is working on resolving this.\n\n"
            f"Expected resolution: {est_resolution}. "
            f"You will receive a confirmation once processing is complete.\n\n"
            f"We appreciate your patience.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "Logistics/Carrier Delay": (
            f"Dear {order['customer_name']},\n\n"
            f"We wanted to provide an update on your order {order['order_id']}. "
            f"Your order has been packed and is ready for shipment. However, "
            f"our shipping partner is currently experiencing delays in your region.\n\n"
            f"We are working with our logistics team to expedite the pickup. "
            f"Updated estimated delivery: {est_resolution}.\n\n"
            f"We apologize for the delay and will send you tracking information "
            f"as soon as your shipment is picked up.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "Logistics Hub Congestion": (
            f"Dear {order['customer_name']},\n\n"
            f"We are providing an update regarding your order {order['order_id']}. "
            f"Your shipment is currently in transit but experiencing a slight delay "
            f"due to high volume at the distribution center.\n\n"
            f"We have arranged alternative routing to get your order to you faster. "
            f"Updated timeline: {est_resolution}.\n\n"
            f"Thank you for your patience.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "Inventory/Stock Issue": (
            f"Dear {order['customer_name']},\n\n"
            f"Thank you for your order {order['order_id']}. We wanted to let you know "
            f"that some items in your order are temporarily out of stock.\n\n"
            f"We have shipped the available items and created a backorder for the "
            f"remaining products. These will be shipped to you as soon as they "
            f"are available, at no additional shipping cost.\n\n"
            f"Estimated timeline for remaining items: {est_resolution}.\n\n"
            f"We appreciate your understanding.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        ),
        "Payment + ERP Combined Failure": (
            f"Dear {order['customer_name']},\n\n"
            f"We regret to inform you that there was an issue processing your "
            f"order {order['order_id']}. Unfortunately, we were unable to complete "
            f"the payment authorization, which prevented us from confirming your order.\n\n"
            f"Our team is investigating the issue and will contact you with next steps. "
            f"If you would like to place the order again with updated payment details, "
            f"we are happy to assist.\n\n"
            f"We sincerely apologize for the inconvenience.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        )
    }

    if not has_issues:
        message = (
            f"Dear {order['customer_name']},\n\n"
            f"Thank you for reaching out regarding your order {order['order_id']}. "
            f"We are pleased to confirm that your order is progressing normally.\n\n"
            f"Current status: {order['fulfillment_status']}\n"
            f"Shipment status: {order['shipment_status']}\n\n"
            f"No issues have been detected with your order. "
            f"If you have any further questions, please do not hesitate to contact us.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        )
    else:
        message = templates.get(category,
            f"Dear {order['customer_name']},\n\n"
            f"Thank you for contacting us about order {order['order_id']}. "
            f"We are aware of a processing issue and our team is actively working on it.\n\n"
            f"Expected resolution: {est_resolution}.\n\n"
            f"We will keep you updated on the progress.\n\n"
            f"Best regards,\nElectrolux Order Support Team"
        )

    return {
        "message": message,
        "estimated_resolution": est_resolution,
        "generated_by": "AI (Simulated Template)"
    }
