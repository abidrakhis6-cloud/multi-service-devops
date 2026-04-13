"""
Stripe Connect views for MultiServe
Handles payments and payouts with Stripe Connect
"""
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Order, Payment, UserBankAccount, Invoice
from .invoice_generator import create_invoice

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else 'sk_test_your_key'


@csrf_exempt
@require_http_methods(["POST"])
def create_payment_intent(request):
    """Create a payment intent for an order"""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        amount = data.get('amount')  # Amount in cents
        
        # Get order
        order = Order.objects.get(id=order_id)
        
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='eur',
            metadata={
                'order_id': order_id,
                'user_id': request.user.id,
                'store_id': order.store.id if order.store else None
            },
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            method='card',
            status='pending',
            transaction_id=intent.id
        )
        
        return JsonResponse({
            'success': True,
            'client_secret': intent.client_secret,
            'payment_id': payment.id
        })
        
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def confirm_payment(request):
    """Confirm payment and create invoice"""
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        
        # Retrieve payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Update payment status
            payment = Payment.objects.get(transaction_id=payment_intent_id)
            payment.status = 'completed'
            payment.save()
            
            # Update order status
            order = payment.order
            order.status = 'confirmed'
            order.save()
            
            # Create invoice
            invoice = create_invoice(order, payment)
            
            return JsonResponse({
                'success': True,
                'message': 'Payment confirmed',
                'invoice_number': invoice.invoice_number,
                'invoice_url': f'/invoice/{invoice.id}/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Payment status: {intent.status}'
            })
            
    except Payment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Payment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_connected_account(request):
    """Create a Stripe Connect account for receiving payments"""
    try:
        data = json.loads(request.body)
        
        # Create Connected Account
        account = stripe.Account.create(
            type='express',
            country='FR',
            email=request.user.email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
            business_type='individual',
            business_profile={
                'name': data.get('business_name', 'MultiServe Partner'),
                'url': data.get('website', ''),
            }
        )
        
        # Save account ID to user profile
        bank_account, created = UserBankAccount.objects.get_or_create(
            user=request.user,
            defaults={
                'stripe_account_id': account.id,
                'account_holder_name': data.get('account_holder_name', ''),
            }
        )
        
        if not created:
            bank_account.stripe_account_id = account.id
            bank_account.save()
        
        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=f"{request.build_absolute_uri('/')}/stripe/reconnect",
            return_url=f"{request.build_absolute_uri('/')}/dashboard/",
            type='account_onboarding',
        )
        
        return JsonResponse({
            'success': True,
            'account_id': account.id,
            'onboarding_url': account_link.url
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_bank_account(request):
    """Add bank account (IBAN) for payouts"""
    try:
        data = json.loads(request.body)
        
        # Get user's Stripe account
        bank_account = UserBankAccount.objects.get(user=request.user)
        
        if not bank_account.stripe_account_id:
            return JsonResponse({
                'success': False,
                'error': 'No Stripe account found. Create account first.'
            }, status=400)
        
        # Create bank account token
        token = stripe.Token.create(
            bank_account={
                'country': 'FR',
                'currency': 'eur',
                'account_holder_name': data.get('account_holder_name'),
                'account_holder_type': 'individual',
                'iban': data.get('iban'),
            }
        )
        
        # Attach bank account to connected account
        external_account = stripe.Account.create_external_account(
            bank_account.stripe_account_id,
            external_account=token.id
        )
        
        # Save to database
        bank_account.iban = data.get('iban')
        bank_account.bic_swift = data.get('bic', '')
        bank_account.bank_name = data.get('bank_name', '')
        bank_account.stripe_bank_account_id = external_account.id
        bank_account.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Bank account added successfully',
            'bank_account_id': external_account.id
        })
        
    except UserBankAccount.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bank account record not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def transfer_to_account(request):
    """Transfer funds to user's connected account (payout)"""
    try:
        data = json.loads(request.body)
        amount = data.get('amount')  # Amount in cents
        
        # Get user's bank account
        bank_account = UserBankAccount.objects.get(user=request.user)
        
        if not bank_account.stripe_account_id:
            return JsonResponse({
                'success': False,
                'error': 'No Stripe account found'
            }, status=400)
        
        # Create transfer
        transfer = stripe.Transfer.create(
            amount=int(amount * 100),
            currency='eur',
            destination=bank_account.stripe_account_id,
            description=f'Payout for {request.user.username}'
        )
        
        return JsonResponse({
            'success': True,
            'transfer_id': transfer.id,
            'amount': amount,
            'status': transfer.status
        })
        
    except UserBankAccount.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bank account not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_invoice_pdf(request, invoice_id):
    """Generate and return invoice PDF"""
    from django.shortcuts import render
    
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        # Check if user owns this invoice
        if invoice.order.user != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        # Return HTML for now - in production, convert to PDF
        return render(request, 'invoice_template.html', {
            'invoice': invoice,
            'order': invoice.order,
            'items': invoice.order.cart.items.all()
        })
        
    except Invoice.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invoice not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """Stripe webhook handler"""
    payload = request.body
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle events
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Update payment status
            try:
                payment = Payment.objects.get(transaction_id=payment_intent['id'])
                payment.status = 'completed'
                payment.save()
                
                # Update order
                order = payment.order
                order.status = 'confirmed'
                order.save()
                
                # Create invoice
                create_invoice(order, payment)
                
            except Payment.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'success'})
        
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
