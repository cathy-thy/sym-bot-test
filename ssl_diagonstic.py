#!/usr/bin/env python3
"""
SSL Certificate Diagnostic Script
Run this to diagnose the SSL certificate issue with develop2.symphony.com
"""

import ssl
import socket
import certifi
import requests
import sys
import os

def check_environment():
    """Check Python environment and certificate locations"""
    print("=== ENVIRONMENT CHECK ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check environment variables
    ssl_vars = ['SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
    for var in ssl_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")
    
    print(f"Certifi bundle location: {certifi.where()}")
    print()

def check_certificates():
    """Check if Let's Encrypt certificates are in the bundle"""
    print("=== CERTIFICATE BUNDLE CHECK ===")
    try:
        with open(certifi.where(), 'r') as f:
            cert_content = f.read()
            
        # Check for different Let's Encrypt authorities
        le_authorities = [
            "Let's Encrypt",
            "ISRG Root X1",
            "ISRG Root X2",
            "R3",
            "R10",
            "R11"
        ]
        
        found_authorities = []
        for authority in le_authorities:
            if authority in cert_content:
                found_authorities.append(authority)
        
        if found_authorities:
            print(f"✅ Found Let's Encrypt authorities: {', '.join(found_authorities)}")
        else:
            print("❌ No Let's Encrypt authorities found in certificate bundle")
            
    except Exception as e:
        print(f"❌ Error reading certificate bundle: {e}")
    print()

def test_python_ssl():
    """Test direct Python SSL connection"""
    print("=== PYTHON SSL CONNECTION TEST ===")
    try:
        context = ssl.create_default_context()
        with socket.create_connection(('develop2.symphony.com', 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname='develop2.symphony.com') as ssock:
                cert = ssock.getpeercert()
                print("✅ Python SSL connection successful")
                print(f"Certificate subject: {cert.get('subject', 'Unknown')}")
                print(f"Certificate issuer: {cert.get('issuer', 'Unknown')}")
                print(f"Certificate expires: {cert.get('notAfter', 'Unknown')}")
                return True
    except Exception as e:
        print(f"❌ Python SSL connection failed: {e}")
        return False
    print()

def test_requests_library():
    """Test requests library SSL connection"""
    print("=== REQUESTS LIBRARY TEST ===")
    try:
        response = requests.get('https://develop2.symphony.com', timeout=10, allow_redirects=False)
        print(f"✅ Requests library connection successful (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Requests library connection failed: {e}")
        return False
    print()

def get_certificate_chain():
    """Get and display the certificate chain"""
    print("=== CERTIFICATE CHAIN ANALYSIS ===")
    try:
        import subprocess
        result = subprocess.run([
            'openssl', 's_client', '-connect', 'develop2.symphony.com:443',
            '-servername', 'develop2.symphony.com', '-showcerts'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            output = result.stdout
            # Extract certificate info
            if "CN=develop2.symphony.com" in output:
                print("✅ Server certificate found")
            if "Let's Encrypt" in output or "R11" in output:
                print("✅ Let's Encrypt certificate chain detected")
            if "Verify return code: 0 (ok)" in output:
                print("✅ Certificate verification successful with system tools")
            else:
                print("⚠️  Certificate verification may have issues")
        else:
            print(f"❌ OpenSSL test failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not run OpenSSL test: {e}")
    print()

def main():
    """Run all diagnostic tests"""
    print("Symphony SSL Certificate Diagnostic Tool")
    print("=" * 50)
    
    check_environment()
    check_certificates()
    
    ssl_works = test_python_ssl()
    requests_works = test_requests_library()
    
    get_certificate_chain()
    
    print("=== SUMMARY ===")
    if ssl_works and requests_works:
        print("✅ All tests passed - SSL should be working")
        print("The issue might be specific to the Symphony SDK configuration.")
    elif not ssl_works:
        print("❌ Python SSL connection failed")
        print("RECOMMENDED FIXES:")
        print("1. Update certificates: pip install --upgrade certifi")
        print("2. If on macOS: /Applications/Python\\ 3.x/Install\\ Certificates.command")
        print("3. Check if you're behind a corporate proxy/firewall")
    elif not requests_works:
        print("❌ Requests library failed")
        print("RECOMMENDED FIXES:")
        print("1. Update requests: pip install --upgrade requests urllib3")
        print("2. Check proxy settings")

if __name__ == "__main__":
    main()