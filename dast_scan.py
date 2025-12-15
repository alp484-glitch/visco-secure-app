import time
import os
from zapv2 import ZAPv2
from requests.exceptions import ProxyError

# ⚠️ Note: Please replace YOUR_ZAP_API_KEY with your actual API key set in ZAP
# The ZAP API Key is a mandatory parameter for security reasons.
ZAP_API_KEY = "8aoro2qqd6m34nqtai6e1588m3"
ZAP_PROXY_ADDRESS = "127.0.0.1"
ZAP_PROXY_PORT = 8080

target = "http://127.0.0.1:5001"
REPORT_FILENAME = "dast_report.html"

# Configure ZAP with API Key and proxy settings
try:
    zap = ZAPv2(
        proxies={
            "http": f"http://{ZAP_PROXY_ADDRESS}:{ZAP_PROXY_PORT}",
            "https": f"http://{ZAP_PROXY_ADDRESS}:{ZAP_PROXY_PORT}"
        },
        apikey=ZAP_API_KEY  # Add API Key
    )
    print(f"✅ Successfully initialized ZAPv2 client.")

except Exception as e:
    print(f"❌ Error during ZAPv2 initialization: {e}")
    print("Please check if ZAP is running and if the API Key and proxy address (127.0.0.1:8080) are configured correctly.")
    exit(1)

print(f"\n🚀 Starting DAST scan for target: {target}")
print("-" * 30)

# 1. Spider crawling
try:
    print("🕸️ Starting spider crawling...")
    # Ensure ZAP's proxy mode is enabled and access the target to let ZAP record the session
    # You can manually access the target website once in the ZAP UI first
    spider_scan_id = zap.spider.scan(target)

    # Add wait to ensure the scan starts
    time.sleep(2)

    while int(zap.spider.status(spider_scan_id)) < 100:
        print(f"   Spider crawling progress: {zap.spider.status(spider_scan_id)}%")
        time.sleep(2)
    print("✅ Spider crawling completed.")

except ProxyError as pe:
    print(f"❌ Connection Error during Spider Scan: {pe}")
    print("Please confirm that the ZAP application is running and listening on 127.0.0.1:8080.")
    exit(1)
except Exception as e:
    print(f"❌ An error occurred during Spider Scan: {e}")
    exit(1)

# 2. Active scanning
print("\n🛡️ Starting active scanning...")
try:
    ascan_scan_id = zap.ascan.scan(target)

    # Add wait to ensure the scan starts
    time.sleep(5)

    while int(zap.ascan.status(ascan_scan_id)) < 100:
        print(f"   Active scanning progress: {zap.ascan.status(ascan_scan_id)}%")
        time.sleep(5)
    print("✅ Active scanning completed.")

except Exception as e:
    print(f"❌ An error occurred during Active Scan: {e}")

# 3. Generate report
print("\n📝 Generating scan report...")
try:
    report = zap.core.htmlreport()
    with open(REPORT_FILENAME, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ Scan report saved to {REPORT_FILENAME}")
except Exception as e:
    print(f"❌ Error generating report: {e}")

# 4. Check for high-risk vulnerabilities
print("\n⚠️ Checking for high-risk vulnerabilities...")
try:
    alerts = zap.core.alerts()
    high_alerts = [a for a in alerts if a["risk"] == "High"]

    if high_alerts:
        print(f"🛑 Found {len(high_alerts)} high-risk vulnerabilities:")
        for alert in high_alerts:
            print(f"- **{alert['alert']}** (Risk: {alert['risk']}, Confidence: {alert['confidence']})")
            print(f"  > URL: {alert['url']}")
        # According to the original code logic, exit with non-zero code when high-risk vulnerabilities are found
        exit_code = 1
    else:
        print("🎉 No high-risk vulnerabilities found.")
        exit_code = 0

except Exception as e:
    print(f"❌ Error checking alerts: {e}")
    exit_code = 1

print("\n---")
print(f"✨ DAST scan finished! Exiting with code {exit_code}")
exit(exit_code)