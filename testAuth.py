import os
from client.authClient import authClient
# Initialize logger at the top so it's available everywhere
from client.logger.loggerFactory import logger_factory
logger = logger_factory.get_logger('testAuth')

# Quick test when run as main module
if __name__ == "__main__":
    logger.info("Running authClient quick test ...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT')}")
    logger.info(f"Auth Server Host: {authClient.auth_server_host}")
    logger.info(f"Auth Server Port: {authClient.auth_server_port}")
    logger.info(f"ENFORCE_HTTPS: {authClient.enforce_https}")
    logger.info(f"VERIFY_SSL_CERTS: {authClient.verify_ssl_certs}")
    if authClient.enforce_https:
        logger.info("HTTPS is enforced for communication with the authentication server.")
    if not authClient.verify_ssl_certs:
        logger.warning("SSL certificate verification is DISABLED. This is insecure and not recommended for production environments.")
    # ===== Quick test of authentication and verification ======
    # Test authentication
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    service = os.getenv("SERVICE")
    token = authClient.authenticate(username, password, service)
    if token:
        print(f"Authentication successful. Token: {token}")
        # Test token verification
        is_valid = authClient.verify(token, service)
        if is_valid:
            print("Token verification successful.")
        else:
            print("Token verification failed.")
    else:
        print("Authentication failed.")