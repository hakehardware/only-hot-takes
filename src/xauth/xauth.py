import os
import time
import base64
import hashlib
import re
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from flask import Flask, request, redirect, session
from src.db.db import DB
from logger import logger


X_REDIRECT_URI = "http://localhost:5000/oauth/callback"
X_AUTH_URL = "https://twitter.com/i/oauth2/authorize"
X_TOKEN_URL = "https://api.x.com/2/oauth2/token"
X_SCOPES = ["tweet.read", "users.read", "tweet.write", "offline.access"]


class XAuth:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.access_token = os.getenv("X_ACCESS_TOKEN")
        self.secret = os.getenv("X_SECRET")
        self.redirect_uri = X_REDIRECT_URI

        # X API endpoints and scopes
        self.auth_url = X_AUTH_URL
        self.token_url = X_TOKEN_URL
        self.scopes = X_SCOPES

        # Initialize the database
        self.db = DB()

        # Flask app for initial auth callback
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(50)
        self._setup_routes()

    def _make_oauth_session(self):
        """Create an OAuth2Session instance."""
        return OAuth2Session(
            client_id=self.access_token,
            redirect_uri=self.redirect_uri,
            scope=self.scopes
        )

    def _generate_pkce(self):
        """Generate PKCE code verifier and challenge."""
        code_verifier = base64.urlsafe_b64encode(os.urandom(30))\
            .decode("utf-8")
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge)\
            .decode("utf-8").replace("=", "")
        return code_verifier, code_challenge

    def _setup_routes(self):
        """Set up Flask routes for authentication."""
        @self.app.route("/")
        def auth_start():
            oauth = self._make_oauth_session()
            code_verifier, code_challenge = self._generate_pkce()
            authorization_url, state = oauth.authorization_url(
                self.auth_url,
                code_challenge=code_challenge,
                code_challenge_method="S256"
            )
            session["oauth_state"] = state
            session["code_verifier"] = code_verifier
            return redirect(authorization_url)

        @self.app.route("/oauth/callback")
        def auth_callback():
            code = request.args.get("code")
            if not code:
                return "Error: No code provided", 400

            oauth = self._make_oauth_session()
            token = oauth.fetch_token(
                self.token_url,
                client_secret=self.secret,
                code_verifier=session["code_verifier"],
                code=code
            )

            # Add expiration timestamp
            token["expires_at"] = time.time() + token["expires_in"]

            # Store token in database
            self.db.store_token(token)

            return "Authentication successful! Token stored in the database.",
        200

    def start_auth_server(self):
        """Start the Flask server for authentication."""
        print("Visit http://localhost:5000 to authorize your app.")
        self.app.run(host="0.0.0.0", port=5000)

    def _refresh_token(self):
        """Refresh the token using the stored refresh token."""
        refresh_token = self.db.get_refresh_token()
        if not refresh_token:
            logger.info("No refresh token found. User needs to \
                        re-authenticate.")
            return None

        oauth = self._make_oauth_session()
        oauth.auth = HTTPBasicAuth(self.access_token, self.secret)
        token = oauth.refresh_token(
            token_url=self.token_url,
            refresh_token=refresh_token
        )

        # Add expiration timestamp
        token["expires_at"] = time.time() + token["expires_in"]

        # Store updated token
        self.db.store_token(token)
        return token

    def get_access_token(self):
        """Get a valid access token, refreshing if expired or initializing \
            if missing."""
        token = self.db.get_token()

        if not token:
            logger.info("No token found in the database. \
                        Starting authentication...")
            self.start_auth_server()
            return None  # User must complete authentication in the browser

        if time.time() >= token.get("expires_at", 0):
            logger.info("Token expired. Refreshing...")
            token = self._refresh_token()

        return token["access_token"] if token else None

    def is_token_valid(self):
        """Check if the current token is valid."""
        return self.db.is_token_valid()
