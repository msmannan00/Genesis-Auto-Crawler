import eventlet

import requests
import socket

# Set a default socket timeout to ensure no operation blocks indefinitely
socket.setdefaulttimeout(15)

def fetch_bbc_via_tor():
    try:
        # Use the Tor proxy settings
        proxies = {
            "http": "socks5h://127.0.0.1:9150",  # Adjust the port if needed (9150 or 9050)
            "https": "socks5h://127.0.0.1:9150"
        }

        # Custom headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        # Use eventlet to enforce a hard timeout for the request
        with eventlet.Timeout(5):  # 30-second timeout
            response = requests.get("http://buyreal4ka5ulaeatencombd52pnihjmnjfubtad4ze4dixp76ovrrid.onion/reviews.php", headers=headers, proxies=proxies, timeout=(5, 5))
            response.raise_for_status()  # Raise an exception if the request failed

            # Return the response content
            return response.text[:500]  # Print the first 500 characters

    except eventlet.Timeout:
        # Log the timeout and return a safe response
        return "Request forcibly timed out"

    except socket.timeout:
        # Handle socket-level timeout
        return "Socket timeout occurred"

    except Exception as ex:
        # Handle any other exceptions to prevent worker crash
        return f"An unexpected error occurred: {str(ex)}"

# Main function to run the program
if __name__ == "__main__":
    result = fetch_bbc_via_tor()
    print(result)
