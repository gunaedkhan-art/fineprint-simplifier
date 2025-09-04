# Stripe Payment Integration Setup Guide

## 🚀 Quick Setup for Production

### 1. Create Stripe Account
1. Go to [stripe.com](https://stripe.com) and create an account
2. Complete the account verification process
3. Get your API keys from the Stripe Dashboard

### 2. Get Your Stripe Keys
1. Go to [Stripe Dashboard > Developers > API Keys](https://dashboard.stripe.com/apikeys)
2. Copy your **Publishable Key** and **Secret Key**
3. For production, use the **Live** keys (not Test keys)

### 3. Create Product and Price
1. Go to [Stripe Dashboard > Products](https://dashboard.stripe.com/products)
2. Click "Add Product"
3. Set up your Pro subscription:
   - **Name**: Small Print Checker Pro
   - **Description**: Unlimited document analysis with advanced features
   - **Pricing**: $9.99/month (recurring)
   - **Billing**: Monthly

4. Copy the **Product ID** and **Price ID** from the created product

### 4. Set Up Webhooks
1. Go to [Stripe Dashboard > Developers > Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Set **Endpoint URL** to: `https://your-domain.com/stripe-webhook`
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Webhook Signing Secret**

### 5. Environment Variables
Set these environment variables in your deployment platform:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_PRO_PRODUCT_ID=prod_your_product_id_here
STRIPE_PRO_PRICE_ID=price_your_price_id_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Admin Configuration
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

### 6. Test the Integration
1. Deploy your application with the environment variables
2. Go to your pricing page
3. Click "Upgrade to Pro"
4. Enter a test email
5. Complete the Stripe checkout process
6. Verify the user is upgraded to Pro tier

## 🔧 Development/Testing Setup

For testing, use Stripe's test mode:

1. Use **Test** API keys from the Stripe Dashboard
2. Create a test product with $0.01 price for testing
3. Use test webhook endpoint: `https://your-domain.com/stripe-webhook`
4. Test with Stripe's test card numbers:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`

## 📋 Production Checklist

- [ ] Stripe account verified and activated
- [ ] Live API keys configured
- [ ] Product and price created in Stripe
- [ ] Webhook endpoint configured and tested
- [ ] Environment variables set in production
- [ ] Payment flow tested end-to-end
- [ ] Customer portal access tested
- [ ] Subscription cancellation tested

## 🛡️ Security Notes

- Never commit API keys to version control
- Use environment variables for all sensitive data
- Enable webhook signature verification
- Use HTTPS for all webhook endpoints
- Regularly rotate API keys

## 📞 Support

If you encounter issues:
1. Check Stripe Dashboard for error logs
2. Verify webhook endpoint is accessible
3. Check environment variables are set correctly
4. Test with Stripe's test mode first

## 💰 Pricing Configuration

Current pricing:
- **Free Tier**: $0/month - 3 documents
- **Pro Tier**: $9.99/month - Unlimited documents

To change pricing:
1. Update the price in Stripe Dashboard
2. Update the price display in `templates/pricing.html`
3. Update the price in `pricing_config.py` if needed
