import json
import stripe
import logging
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .serializers import CapOrderSerializer
from .models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
def create_order(request):
    data = request.data
    cart = data.get("cart", [])
    shipping = data.get("shippingInfo", {})

    if not cart:
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    full_name = shipping.get("fullName", "")
    email = shipping.get("email", "")
    address = shipping.get("address", "")
    city = shipping.get("city", "")
    zip_code = shipping.get("zip", "")

    contact_info = f"{full_name} <{email}>"
    shipping_address = f"{address}, {city}, {zip_code}"

    group = CapOrderGroup.objects.create(
        confirmation_code=str(uuid.uuid4()).split("-")[0].upper(),
        full_name=full_name,  # ✅ Save it here
        contact_info=email,   # ✅ Or keep `contact_info` string if preferred
        shipping_address=shipping_address  # ✅ Save address properly
    )

    for item in cart:
        CapOrder.objects.create(
            group=group,
            cat_name=item.get("cat_name", ""),
            team=item.get("team", ""),
            color=item.get("color", ""),
            pope_leo=(item.get("bust_type") == "pope"),
            le_bubu=(item.get("bust_type") == "bubu"),
            bust_color=item.get("bust_color", None),
            font=item.get("font", ""),
            font_color=item.get("font_color", ""),
            contact_info=email,
            shipping_address=shipping_address,
            price=item.get("price", "0.00")
        )

    return Response({
        "message": "Order group created!",
        "confirmation_code": group.confirmation_code
    }, status=status.HTTP_201_CREATED)



@csrf_exempt
def list_orders(request):
    if request.method == "GET":
        groups = CapOrderGroup.objects.prefetch_related("orders").order_by("-created_at")
        data = []
        for group in groups:
            data.append({
                "confirmation_code": group.confirmation_code,
                "full_name": group.full_name,  # <-- Add this line
                "contact_info": group.contact_info,
                "shipping_address": group.shipping_address or "",
                "created_at": group.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "items": [
                    {
                        "cat_name": order.cat_name,
                        "team": order.team,
                        "color": order.color,
                        "bust_type": (
                            "pope" if order.pope_leo else 
                            "bubu" if order.le_bubu else 
                            "none"
                        ),
                        "bust_color": order.bust_color,
                        "font": order.font,
                        "font_color": order.font_color,
                        "price": str(order.price),
                    }
                    for order in group.orders.all()
                ]
            })
        return JsonResponse(data, safe=False)


@csrf_exempt
def submit_pink_interest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            interested = data.get('interested')
            email = data.get('email', None)

            if interested is None:
                return JsonResponse({'error': 'Missing interest flag'}, status=400)

            interest = PinkEditionInterest.objects.create(
                interested=interested,
                email=email if email else None
            )

            logger.info(f"Pink interest saved: {interest}")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.exception("Error saving pink interest")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cart = data.get("cart", [])
            shipping = data.get("shippingInfo", {})

            logger.info("Received cart: %s", cart)
            logger.info("Received shipping: %s", shipping)

            if not cart:
                return JsonResponse({"error": "Cart is empty"}, status=400)

            line_items = []

            for item in cart:
                if "catName" not in item or "teamLogo" not in item:
                    return JsonResponse({"error": "Missing cart item info"}, status=400)

                base_price = 2499
                if item.get("bustType") in ["pope", "bubu"]:
                    base_price += 499

                name = f"{item['catName'].strip()} Cap - {item['teamLogo'].capitalize()}"
                if item["bustType"] != "none":
                    name += f" + {item['bustType'].capitalize()}"

                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": name,
                        },
                        "unit_amount": base_price,
                    },
                    "quantity": 1,
                })

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=settings.SITE_URL + "/success",
                cancel_url=settings.SITE_URL + "/order",
                customer_email=shipping.get("email", ""),
                shipping_address_collection={"allowed_countries": ["US"]},
                metadata={
                    "customer_name": shipping.get("fullName", ""),
                    "email": shipping.get("email", ""),
                    "address": shipping.get("address", ""),
                    "city": shipping.get("city", ""),
                    "zip": shipping.get("zip", "")
                }
            )

            return JsonResponse({"url": checkout_session.url})
        except Exception as e:
            logger.exception("Stripe Checkout error")
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
