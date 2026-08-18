"""
Script to test HTTP connection to local Flask server.
"""
import urllib.request
import urllib.error

def check_url(url):
    try:
        req = urllib.request.urlopen(url, timeout=3)
        print(f"SUCCESS to {url} - Status Code: {req.status}")
        return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error on {url}: Status {e.code}")
        return False
    except Exception as e:
        print(f"Failed to connect to {url}: {e}")
        return False

if __name__ == '__main__':
    print("Testing connections:")
    check_url("http://127.0.0.1:5001/")
    check_url("http://localhost:5001/")
    check_url("http://127.0.0.1:5001/api/health")
