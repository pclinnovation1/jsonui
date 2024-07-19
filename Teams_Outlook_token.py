import requests

def get_access_token(client_id, client_secret, tenant_id):
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',  # This specifies the type of OAuth2 flow
        'client_id': client_id,              # Application (client) ID from Azure AD
        'client_secret': client_secret,      # Client secret from Azure AD
        'scope': 'https://graph.microsoft.com/.default'  # The scope for Microsoft Graph API
    }
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        raise Exception(f"Failed to obtain access token: {response_data}")

# Example usage
client_id = '605ca15b-8466-40c1-92f0-681179d37409'
client_secret = 'PYT8Q~BKJqtmAfG1AB7G8JHITkvPyH21S.Y1PakW'
tenant_id = '3025d089-487f-4cbc-964c-64da1758fec7'
access_token = get_access_token(client_id, client_secret, tenant_id)
print(f"Access Token: {access_token}")
