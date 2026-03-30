#!/bin/bash

# Install extensions from extensions.json
echo "Installing VSCode extensions for Django development..."

# Read extensions from JSON and install them
jq -r '.recommendations[]' .vscode/extensions.json | while read extension; do
    echo "Installing: $extension"
    code --install-extension "$extension" --force
done

echo ""
echo "✅ All extensions installed!"
echo ""
echo "Optional extensions can be installed from:"
echo "  • .vscode/extensions-optional.json"
echo "  • .vscode/extensions-minimal.json (for minimal setup)"
