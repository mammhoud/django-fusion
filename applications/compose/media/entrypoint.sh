#!/bin/sh
set -e

SSL_DIR="/etc/nginx/ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "🔐 Generating self-signed certificate..."

    # Try to create the directory; if it fails we assume the volume is read-only
    # and the certificates have been pre-mounted externally.
    if mkdir -p "$SSL_DIR" 2>/dev/null && touch "$SSL_DIR/.write_test" 2>/dev/null; then
        rm -f "$SSL_DIR/.write_test"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$KEY_FILE" \
            -out "$CERT_FILE" \
            -subj "/CN=$DJANGO_HOST"
        echo "✅ Self-signed certificate created."
    else
        echo "⚠️  SSL directory is read-only. Using pre-existing certificates."
        # If the directory is read-only, the files must already exist.
        # If not, the container will fail when nginx starts – which is expected.
    fi
else
    echo "✅ Certificates already present."
fi

exec "$@"
