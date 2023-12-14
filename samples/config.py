app_id = 'hcfrei1d4ywjhly7hnmdz'
app_secret = 'h5mfAjRkbJV6bNdPYgG2rGuIYzRMM4r8'

redirect_uri_callback = 'http://localhost:5000/callback' #configure in logto admin

post_logout_redirect_uri = 'http://localhost:5000' #configure in logto admin

core_endpoint = 'http://localhost:3001' #do not add a final forward slash '/'

issuer = 'http://localhost:3001/oidc'

jwks_uri = 'http://localhost:3001/oidc/jwks'

# Global variables for JWKS caching
JWKS_CACHE = None
JWKS_LAST_FETCHED = 0
JWKS_REFRESH_INTERVAL = 86400  # Refresh every 24 hours (86400 seconds)
