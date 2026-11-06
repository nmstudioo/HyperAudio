#!/bin/bash
REPORT="REPO_REPORT.md"
echo "# Repository Report: HyperAudio" > $REPORT
echo "Generated on: $(date)" >> $REPORT
echo "" >> $REPORT

echo "## 1. Git Status" >> $REPORT
echo '```text' >> $REPORT
echo "Branch: $(git branch --show-current)" >> $REPORT
echo "Latest Commit: $(git log -1 --pretty=format:"%h - %s (%cr)")" >> $REPORT
echo "" >> $REPORT
git status -s >> $REPORT
if [ -z "$(git status -s)" ]; then echo "Working tree clean." >> $REPORT; fi
echo '```' >> $REPORT
echo "" >> $REPORT

echo "## 2. Recent Commits" >> $REPORT
echo '```text' >> $REPORT
git log -5 --pretty=format:"%h - %s (%cr)" >> $REPORT
echo "" >> $REPORT
echo '```' >> $REPORT
echo "" >> $REPORT

echo "## 3. CI/CD Status (Latest 3 Runs)" >> $REPORT
echo '```text' >> $REPORT
gh run list -L 3 >> $REPORT
echo '```' >> $REPORT
echo "" >> $REPORT

echo "## 4. File Structure (Depth 3)" >> $REPORT
echo '```text' >> $REPORT
# Use find if tree is not installed, formatting it nicely
find . -maxdepth 3 -not -path '*/\.git*' -not -path '*/node_modules*' -not -name '*.pyc' | sort | sed 's|[^/]*/|  |g' >> $REPORT
echo '```' >> $REPORT
echo "" >> $REPORT

echo "## 5. Core Tests Status" >> $REPORT
echo '```text' >> $REPORT
python3 tests/check.py >> $REPORT 2>&1
echo '```' >> $REPORT
echo "" >> $REPORT

echo "## 6. Release Blockers (from HANDOFF.md)" >> $REPORT
if [ -f "HANDOFF.md" ]; then
    cat HANDOFF.md >> $REPORT
else
    echo "HANDOFF.md not found." >> $REPORT
fi

echo "Report generated: $REPORT"
