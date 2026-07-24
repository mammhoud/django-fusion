

#!/bin/bash
set -e  # stop on error


echo "=== 1. Checking Oversized Files in Working Directory (Over 10MB) ==="
find . -type f -not -path '*/.*' -size +10M -exec ls -lh {} \; 2>/dev/null




echo "⚠️  WARNING: This script will rewrite Git history!"
echo "   Make a FULL backup of this repository before proceeding."
echo "   Press Ctrl+C now to cancel, or Enter to continue..."
read

# ------------------------------
# 1. Delete local files/folders
# ------------------------------
echo "🧹 Deleting local build artifacts and logs..."
find . -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name ".next"        -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name "target"       -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name "logs"         -type d -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf **/logs/ 2>/dev/null || true

# ------------------------------
# 2. Untrack them from Git index
# ------------------------------
echo "📦 Untracking from Git index..."
git rm -r --cached "**/node_modules/" 2>/dev/null || true
git rm -r --cached "**/.next/"        2>/dev/null || true
git rm -r --cached "**/target/"       2>/dev/null || true
git rm -r --cached "**/logs/"         2>/dev/null || true

# ------------------------------
# 3. Stage and commit the cleanup
# ------------------------------
echo "💾 Committing local cleanup..."
git add -u
git commit -m "chore: remove build artifacts, logs, node_modules, target dirs" || echo "Nothing to commit"

# ------------------------------
# 4. Permanently delete the large blobs from history
#    (using the exact paths you listed)
# ------------------------------
echo "🔥 Rewriting history to purge large files..."
# Install git-filter-repo if missing
if ! command -v git-filter-repo &> /dev/null; then
    echo "Installing git-filter-repo..."
    pip install git-filter-repo
fi

# Purge these exact paths (and also the whole directories for safety)
git filter-repo --path logs/gunicorn-error.log --invert-paths \
                --path logs/ --invert-paths \
                --path **/logs/ --invert-paths \
                --path node_modules/ --invert-paths \
                --path .next/ --invert-paths \
                --path target/ --invert-paths

# ------------------------------
# 5. Show final size and instructions
# ------------------------------
echo "✅ Done! Repository size now:"
du -sh .git

echo ""
echo "📌 Next steps:"
echo "  1. Review the rewritten history with: git log --oneline"
echo "  2. Force-push to remote: git push --force-with-lease origin generic"
echo "  3. All collaborators must re-clone or rebase onto the new history."



