import requests, base64, datetime

def stk_push(phone, amount, reference):
    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret = "YOUR_CONSUMER_SECRET"
    shortcode = "YOUR_SHORTCODE"
    passkey = "YOUR_PASSKEY"

    # Get access token
    auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    token_res = requests.get(
        "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {auth}"}
    )
    token = token_res.json()["access_token"]

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": "https://yourdomain.com/payments/callback/",
        "AccountReference": reference,
        "TransactionDesc": "Featured Listing Payment"
    }

    requests.post(
        "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
"""
import requests
import base64
import datetime

def stk_push(phone, amount, reference):
    # ✅ YOUR SANDBOX CREDENTIALS - REPLACE THESE WITH YOUR ACTUAL VALUES
    consumer_key = "BDfkPsoS1gMcsTNyEGJMAvBDqFnP51PBW0L2bkZxgAbp6jFT"      # Get from developer.safaricom.co.ke
    consumer_secret = "H6FSvZuMTioIXaoUnQeJDHKLu55hRmdibT3wDRtN7lH36ayaIiF6hSvgxoAbdC3Z" # Get from developer.safaricom.co.ke
    shortcode = "174379"                              # Standard sandbox test shortcode
    passkey = "YOUR_SANDBOX_PASSKEY"                  # Get from test credentials page
    
    # ✅ SANDBOX URLS
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    # Get access token
    auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    
    try:
        token_res = requests.get(
            auth_url,
            headers={"Authorization": f"Basic {auth}"}
        )
        token_res.raise_for_status()
        token = token_res.json()["access_token"]
        
        # Generate timestamp and password
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = shortcode + passkey + timestamp
        password = base64.b64encode(password_str.encode()).decode()

        # Prepare STK Push payload
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",  # Use "CustomerBuyGoodsOnline" for Till
            "Amount": amount,
            "PartyA": str(phone),  # Ensure phone is string
            "PartyB": shortcode,
            "PhoneNumber": str(phone),
            "CallBackURL": "https://yourdomain.com/payments/callback/",  # Use ngrok for local testing
            "AccountReference": reference[:12],  # Max 12 chars
            "TransactionDesc": "Listing Fee"  # Max 13 chars
        }

        # Send STK Push
        response = requests.post(
            stk_url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return response.json()  # Return the response
        
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

# Example usage:
# result = stk_push("254708374149", 1, "TEST001")
# print(result)
"""