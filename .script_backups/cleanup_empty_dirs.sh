#!/bin/bash

# Script to remove empty directories from the project
echo "🧹 Cleaning up empty directories..."

# Check if a directory is empty
is_empty() {
  [ -z "$(ls -A "$1")" ]
}

# List of directories to check
DIRS_TO_CHECK=(
  "ai/agent"
  "ai/probabilistic"
  "ai/search"
  "ai/training"
  "backend/ai"
  "docker/backend"
  "docker/frontend"
  "docker/hadoop"
  "reflectly_bigdata/backend/services"
)

REMOVED_COUNT=0

# Remove empty directories
for dir in "${DIRS_TO_CHECK[@]}"; do
  if [ -d "$dir" ] && is_empty "$dir"; then
    echo "🗑️  Removing empty directory: $dir"
    rmdir "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT+1))
  elif [ -d "$dir" ]; then
    echo "⚠️  Directory not empty, skipping: $dir"
  else
    echo "ℹ️  Directory doesn't exist: $dir"
  fi
done

# Check if parent directories are now empty and can be removed
check_parent_dirs() {
  local dir=$(dirname "$1")
  if [ "$dir" != "." ] && [ -d "$dir" ] && is_empty "$dir"; then
    echo "🗑️  Removing now-empty parent directory: $dir"
    rmdir "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT+1))
    check_parent_dirs "$dir"  # Recursively check higher-level parent directories
  fi
}

# Check parent directories of our removed directories
for dir in "${DIRS_TO_CHECK[@]}"; do
  check_parent_dirs "$dir"
done

echo "✅ Cleanup complete! Removed $REMOVED_COUNT empty directories."
