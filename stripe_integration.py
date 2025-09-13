# stripe_integration.py - Stripe payment processing

import stripe
import os
from typing import Dict, Optional
from datetime import datetime

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

# Product and price IDs (these will be created in Stripe dashboard)
PRO_PRODUCT_ID = os.environ.get("STRIPE_PRO_PRODUCT_ID", "prod_pro_placeholder")
PRO_PRICE_ID = os.environ.get("STRIPE_PRO_PRICE_ID", "price_pro_placeholder")

class StripeManager:
    def __init__(self):
        self.stripe = stripe
        self.pro_product_id = PRO_PRODUCT_ID
        self.pro_price_id = PRO_PRICE_ID
    
    def create_customer(self, email: str, user_id: str) -> Dict:
        """Create a Stripe customer"""
        try:
            customer = self.stripe.Customer.create(
                email=email,
                metadata={
                    'user_id': user_id,
                    'app': 'fineprint_simplifier'
                }
            )
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_checkout_session(self, customer_id: str, user_id: str, success_url: str, cancel_url: str) -> Dict:
        """Create a Stripe checkout session for Pro subscription"""
        try:
            session = self.stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': self.pro_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': user_id,
                    'subscription_type': 'pro'
                },
                subscription_data={
                    'metadata': {
                        'user_id': user_id,
                        'subscription_type': 'pro'
                    }
                }
            )
            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details"""
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            return {
                'success': True,
                'subscription': subscription
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel a subscription"""
        try:
            subscription = self.stripe.Subscription.delete(subscription_id)
            return {
                'success': True,
                'subscription': subscription
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_customer_portal_session(self, customer_id: str, return_url: str) -> Dict:
        """Create a customer portal session for subscription management"""
        try:
            session = self.stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return {
                'success': True,
                'portal_url': session.url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        try:
            webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
            if not webhook_secret:
                return False
            
            self.stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return True
        except Exception as e:
            print(f"Webhook signature verification failed: {e}")
            return False

# Global instance
stripe_manager = StripeManager()

# Helper functions for the main application
def create_payment_session(user_id: str, email: str, success_url: str, cancel_url: str) -> Dict:
    """Create a payment session for a user"""
    # First create or get customer
    customer_result = stripe_manager.create_customer(email, user_id)
    if not customer_result['success']:
        return customer_result
    
    customer_id = customer_result['customer_id']
    
    # Create checkout session
    session_result = stripe_manager.create_checkout_session(
        customer_id, user_id, success_url, cancel_url
    )
    
    if session_result['success']:
        session_result['customer_id'] = customer_id
    
    return session_result

def handle_successful_payment(subscription_id: str, user_id: str) -> Dict:
    """Handle successful payment - upgrade user to Pro"""
    try:
        # Get subscription details
        subscription_result = stripe_manager.get_subscription(subscription_id)
        if not subscription_result['success']:
            return subscription_result
        
        subscription = subscription_result['subscription']
        
        # Check if subscription is active
        if subscription.status in ['active', 'trialing']:
            # Handle current_period_end safely
            current_period_end = None
            if hasattr(subscription, 'current_period_end') and subscription.current_period_end:
                current_period_end = subscription.current_period_end
            
            return {
                'success': True,
                'subscription_id': subscription_id,
                'customer_id': subscription.customer,
                'status': subscription.status,
                'current_period_end': current_period_end
            }
        else:
            return {
                'success': False,
                'error': f'Subscription status is {subscription.status}, not active'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error processing subscription: {str(e)}'
        }
