import sys
import firewall_client

def main():
    if len(sys.argv) < 2:
        print("Usage: firewall-C.py <IP>")
        sys.exit(0)

    ip = sys.argv[1]
    result = firewall_client.check(ip)
    if result == '1':  
        sys.exit(1)
    else:  
        sys.exit(0)

if __name__ == "__main__":
    main()
