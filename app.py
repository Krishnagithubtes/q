from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    url = request.form['url']
    result = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36'
    }

    try:
        # Main page request
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        result['status'] = f"Status Code: {response.status_code}"

        # XSS detection
        result['xss'] = "Possible XSS found" if "<script>" in response.text.lower() else "No XSS found"

        # Clickjacking protection check
        frame_option = response.headers.get('X-Frame-Options')
        result['clickjacking'] = "Protected from clickjacking" if frame_option else "Vulnerable to clickjacking"

        # SQL Injection simulation
        test_url = url + "'"
        try:
            test_resp = requests.get(test_url, headers=headers, timeout=5, verify=False)
            if "sql" in test_resp.text.lower() or "syntax" in test_resp.text.lower():
                result['sqli'] = "Possible SQL Injection vulnerability"
            else:
                result['sqli'] = "No SQL Injection vulnerability"
        except Exception as sqli_error:
            result['sqli'] = f"SQLi check failed: {str(sqli_error)}"

        # Security headers
        result['headers'] = {
            'X-Content-Type-Options': response.headers.get('X-Content-Type-Options', 'Missing'),
            'Content-Security-Policy': response.headers.get('Content-Security-Policy', 'Missing'),
            'Strict-Transport-Security': response.headers.get('Strict-Transport-Security', 'Missing')
        }

    except requests.exceptions.SSLError as ssl_error:
        result['error'] = f"SSL error: {str(ssl_error)}"
    except requests.exceptions.RequestException as req_error:
        result['error'] = f"Request error: {str(req_error)}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"

    return render_template('result.html', result=result, url=url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)