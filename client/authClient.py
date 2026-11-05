import os
import requests # pyright: ignore[reportMissingModuleSource]
from typing import Dict, Any
# Initialize logger at the top so it's available everywhere
# Use absolute imports from the client package root to make it usable as a module
from client.logger.loggerFactory import logger_factory
logger = logger_factory.get_logger('authClient')

VERIFY_TIMEOUT_SECONDS = 10

class AuthServerError(Exception):
    """The Authentication Server could not give an answer about a token (unreachable, TLS failure, unexpected response)"""

class AuthClient:
    """Client for authentication and token verification"""
    def __init__(self):
        authServerHost = ""
        authServerPort = ""
        environment = os.getenv("ENVIRONMENT", "prod")
        if environment == "dev":
            logger.debug("environment is dev !!!")
            authServerHost = "localhost"
            authServerPort = 8443
        elif environment == "prod":
            logger.debug("environment is prod !!!")
            authServerHost = "raspberry01"
            authServerPort = 8444
        # ##### START Allow WINDFIRE_SECURITY_HOST / WINDFIRE_SECURITY_PORT to override the ENVIRONMENT mapping #####
        authServerSource = f"ENVIRONMENT mapping ({environment})"
        overrideHost = os.getenv("WINDFIRE_SECURITY_HOST", "").strip()
        overridePort = os.getenv("WINDFIRE_SECURITY_PORT", "").strip()
        if overrideHost:
            authServerHost = overrideHost
            authServerSource = "WINDFIRE_SECURITY_HOST/WINDFIRE_SECURITY_PORT environment variables"
        if overridePort:
            try:
                authServerPort = int(overridePort)
                authServerSource = "WINDFIRE_SECURITY_HOST/WINDFIRE_SECURITY_PORT environment variables"
            except ValueError:
                logger.error(f"Invalid WINDFIRE_SECURITY_PORT '{overridePort}', keeping port {authServerPort}")
        # ##### END Allow WINDFIRE_SECURITY_HOST / WINDFIRE_SECURITY_PORT to override the ENVIRONMENT mapping #####

        self.auth_server_host = authServerHost
        self.auth_server_port = authServerPort
        self.ca_bundle_path = os.getenv("ROOT_CA_PATH")
        # ##### START Handle ENFORCE_AUTH_SERVER_HTTPS as boolean properly #####
        raw = os.getenv('ENFORCE_AUTH_SERVER_HTTPS', None)
        if raw is None:
            ENFORCE_AUTH_SERVER_HTTPS = True  # or your preferred default
        else:
            ENFORCE_AUTH_SERVER_HTTPS = raw.strip().lower() in ('1', 'true', 'yes', 'on')
        self.enforce_https = ENFORCE_AUTH_SERVER_HTTPS
        # ##### END Handle ENFORCE_AUTH_SERVER_HTTPS as boolean properly #####
        # ***** START Handle VERIFY_SSL_CERTS as boolean properly *****
        raw = os.getenv('VERIFY_SSL_CERTS', None)
        if raw is None:
            VERIFY_SSL_CERTS = False  # or your preferred default
        else:
            VERIFY_SSL_CERTS = raw.strip().lower() in ('1', 'true', 'yes', 'on')
        self.verify_ssl_certs = VERIFY_SSL_CERTS
        # ***** END Handle VERIFY_SSL_CERTS as boolean properly *****
        self.protocol = 'http'
        if self.enforce_https:
            self.protocol = 'https'
        self.url_base = f"{self.protocol}://{self.auth_server_host}:{self.auth_server_port}"
        # Logging initialization details for debug purposes
        logger.debug(f"authClient configuration initialized:")
        logger.debug(f"     Environment: {environment}")
        logger.debug(f"     Protocol: {self.protocol}")
        logger.debug(f"     Authentication Server Host: {self.auth_server_host}")
        logger.debug(f"     Authentication Server Port: {self.auth_server_port}")
        logger.debug(f"     Authentication Server Host/Port source: {authServerSource}")
        logger.debug(f"     Authentication Server URL: {self.url_base}")
        logger.debug(f"     Enforce HTTPS Authentication Server: {self.enforce_https}")
        if self.enforce_https:
            logger.debug("      --> HTTPS enforcement is enabled")
        else:
            logger.debug("      --> HTTPS enforcement is disabled")
        logger.debug(f"     Verify SSL Certificates: {self.verify_ssl_certs}")
        if self.verify_ssl_certs:
            logger.debug("      --> SSL certificate verification is enabled")
        else:
            logger.debug("      --> SSL certificate verification is disabled")
        logger.debug(f"     Certificate Authority bundle path: {self.ca_bundle_path}")
        logger.debug(f"     AuthClient initialized with base URL: {self.url_base}")
    
    ##########################################################
    ##### Function to authenticate user and obtain token #####
    ##########################################################
    def authenticate(self, username: str, password: str, service: str) -> Dict[str, Any]:
        """
        Function to authenticate a user and return access token
        
        Args:
            username: Username
            password: Password
            service: Service name
        
        Returns:
            Access token if authentication is successful, None otherwise
        """
        token = None
        logger.info(f"Authenticating user {username} for {service} service to obtain access token ...")
        url = f"{self.url_base}/v1/security/auth"
        http_headers = {"Content-Type": "application/json"}
        logger.info(f"Calling endpoint {url} on Authentication Server ...")
        try:
            logger.debug(f"VERIFY_SSL_CERTS environment variable is set to {self.verify_ssl_certs} ...")
            if self.verify_ssl_certs:
                logger.debug(f"Verify SSL certificate using CA certificate {self.ca_bundle_path}")
                response = requests.post(url,
                                        json={'username': username, 
                                                'password': password, 
                                                'service': service},
                                        headers=http_headers,
                                        verify=self.ca_bundle_path)
            else:
                logger.debug(f"SSL certificate will not be verified")
                response = requests.post(url,
                                        json={'username': username, 
                                                'password': password, 
                                                'service': service},
                                        headers=http_headers,
                                        verify=self.verify_ssl_certs)
            logger.debug(f"Return Code: {response.status_code}\n")
            if response.status_code == 200:
                token = response.json().get('access_token')
                # ****** START - Uncomment for debug purposes in development ONLY ********
                #logger.debug(f"Response Body: {response.__dict__}\n")
                #logger.debug(f"Access Token: {token}\n")
                # ****** END - Uncomment for debug purposes in development ONLY ********
                if not token is None:
                    logger.info("Authentication successful !!!")
                else:
                    logger.error("Authentication response missing access_token")
            else:
                logger.error(f"Authentication failed with status code {response.status_code}")
                logger.debug(f"Response body: {response.text}\n")
        except Exception as e:
            token = None
            logger.error(f"Authentication failed: {e}")
        return token
    
    #############################################
    ##### Function to verify token validity #####
    #############################################
    def verify(self, token: str, service: str, method: str = 'local') -> bool:
        """
        Function to verify authentication token validity

        A failure to reach the Authentication Server is also reported as False:
        use verify_or_raise() to tell it apart from an invalid token.

        Args:
            token: Access token to verify
            service: Service name
            method: Verification method ('local' or 'remote')

        Returns:
            True if the token is valid, False otherwise
        """
        try:
            return self.verify_or_raise(token, service)
        except AuthServerError as e:
            logger.error(f"Token verification failed: {e}")
            return False

    def verify_or_raise(self, token: str, service: str) -> bool:
        """
        Function to verify authentication token validity, keeping auth server failures distinct

        Args:
            token: Access token to verify
            service: Service name

        Returns:
            True if the Authentication Server accepts the token, False if it rejects it (401/403)

        Raises:
            AuthServerError: If the Authentication Server gives no usable answer
        """
        logger.info(f"Verifying authentication token validity for {service} service ...")
        url = f"{self.url_base}/v1/security/verify"
        http_headers = {"Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"}
        logger.info(f"Calling endpoint {url} on Authentication Server ...")
        logger.debug(f"VERIFY_SSL_CERTS environment variable is set to {self.verify_ssl_certs} ...")
        if self.verify_ssl_certs:
            logger.debug(f"Verify SSL certificate using CA certificate {self.ca_bundle_path}")
        else:
            logger.debug(f"SSL certificate will not be verified")
        try:
            response = requests.post(url,
                                    json={'service': service},
                                    headers=http_headers,
                                    verify=self.ca_bundle_path if self.verify_ssl_certs else False,
                                    timeout=VERIFY_TIMEOUT_SECONDS)
        except Exception as e:
            raise AuthServerError(f"Cannot reach Authentication Server at {url}: {e}") from e
        logger.debug(f"Return Code: {response.status_code}\n")
        # ****** START - Uncomment for debug purposes in development ONLY ********
        #logger.debug(f"Response Body: {response.__dict__}\n")
        # ****** END - Uncomment for debug purposes in development ONLY ********
        if response.status_code in (401, 403):
            logger.warning("Token verification failed !!!")
            return False
        if response.status_code != 200:
            raise AuthServerError(f"Unexpected status code {response.status_code} from {url}: is this the windfire-security server?")
        # A 200 only counts when it carries the JSON body of the verify endpoint
        try:
            body = response.json()
        except ValueError as e:
            raise AuthServerError(f"Response from {url} is not valid JSON: is this the windfire-security server?") from e
        if not body:
            raise AuthServerError(f"Empty response from {url}: is this the windfire-security server?")
        logger.info("Token verification successful !!!")
        return True

####################################################
##### Initialize configuration reader instance #####
####################################################
authClient = AuthClient()