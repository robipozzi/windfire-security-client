import os
import requests # pyright: ignore[reportMissingModuleSource]
from typing import Dict, Any
# Initialize logger at the top so it's available everywhere
# Use absolute imports from the client package root to make it usable as a module
from client.logger.loggerFactory import logger_factory
logger = logger_factory.get_logger('authClient')

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
        # ##### START Allow KEYCLOAK_SERVER_HOST / KEYCLOAK_SERVER_PORT to override the ENVIRONMENT mapping #####
        authServerSource = f"ENVIRONMENT mapping ({environment})"
        overrideHost = os.getenv("KEYCLOAK_SERVER_HOST", "").strip()
        overridePort = os.getenv("KEYCLOAK_SERVER_PORT", "").strip()
        if overrideHost:
            authServerHost = overrideHost
            authServerSource = "KEYCLOAK_SERVER_HOST/KEYCLOAK_SERVER_PORT environment variables"
        if overridePort:
            try:
                authServerPort = int(overridePort)
                authServerSource = "KEYCLOAK_SERVER_HOST/KEYCLOAK_SERVER_PORT environment variables"
            except ValueError:
                logger.error(f"Invalid KEYCLOAK_SERVER_PORT '{overridePort}', keeping port {authServerPort}")
        # ##### END Allow KEYCLOAK_SERVER_HOST / KEYCLOAK_SERVER_PORT to override the ENVIRONMENT mapping #####

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
        
        Args:
            token: Access token to verify
            service: Service name
            method: Verification method ('local' or 'remote')
        
        Returns:
            Verification response as a dictionary
        """
        logger.info(f"Verifying authentication token validity for {service} service ...")
        url = f"{self.url_base}/v1/security/verify"
        http_headers = {"Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"}
        logger.info(f"Calling endpoint {url} on Authentication Server ...")
        verification_response = None
        try:
            logger.debug(f"VERIFY_SSL_CERTS environment variable is set to {self.verify_ssl_certs} ...")
            if self.verify_ssl_certs:
                logger.debug(f"Verify SSL certificate using CA certificate {self.ca_bundle_path}")
                response = requests.post(url, 
                                        json={'service': service}, 
                                        headers=http_headers,
                                        verify=self.ca_bundle_path)                
            else:
                logger.debug(f"SSL certificate will not be verified")
                response = requests.post(url, 
                                        json={'service': service}, 
                                        headers=http_headers,
                                        verify=self.verify_ssl_certs)
            verification_response = response.json()
            logger.debug(f"Return Code: {response.status_code}\n")
            # ****** START - Uncomment for debug purposes in development ONLY ********
            #logger.debug(f"Response Body: {response.__dict__}\n")
            #logger.debug(f"Verification Response: {verification_response}\n")
            # ****** END - Uncomment for debug purposes in development ONLY ********
            if response.status_code == 200:
                logger.info("Token verification successful !!!")
            else:
                logger.warning("Token verification failed !!!")
        except Exception as e:
            verification_response = None
            logger.error(f"Token verification failed: {e}")
        return True if verification_response and response.status_code == 200 else False

####################################################
##### Initialize configuration reader instance #####
####################################################
authClient = AuthClient()