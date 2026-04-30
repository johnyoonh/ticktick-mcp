#!/bin/bash
# Today Cleanup Execution Script
# Uses EventKitCLI to reorganize Apple Reminders

CLI="/Users/john/repos/mcp-server-apple-events/bin/EventKitCLI"
TODAY="2026-04-30"
ERRORS=0
SUCCESS=0

run_update() {
    local desc="$1"
    shift
    echo "→ $desc"
    result=$("$CLI" "$@" 2>&1)
    if echo "$result" | grep -q '"status" : "success"'; then
        echo "  ✅ OK"
        ((SUCCESS++))
    else
        echo "  ❌ FAILED: $result"
        ((ERRORS++))
    fi
}

run_delete() {
    local desc="$1"
    local id="$2"
    echo "→ $desc"
    result=$("$CLI" --action delete --id "$id" 2>&1)
    if echo "$result" | grep -q '"status" : "success"'; then
        echo "  ✅ Deleted"
        ((SUCCESS++))
    else
        echo "  ❌ FAILED: $result"
        ((ERRORS++))
    fi
}

echo "============================================"
echo "STEP 1: Clear ALL stale due dates"
echo "============================================"

# Seminary (Education)
run_update "RDS - PhD Prep Reading books: clear due date" \
    --action update --id "B9FF3D95-BDEF-4C1F-951A-064C7910BAD7" --dueDate "" --startDate ""

run_update "Prepare for essay exam: clear due date" \
    --action update --id "F9C83A3E-B1A7-425F-9DCB-361718D62737" --dueDate "" --startDate ""

# ⚙️ Automation (clearing dates before some get moved)
run_update "Schedule for meeting/marathon: clear due date" \
    --action update --id "3F760663-084F-44E4-90DA-61B02035580E" --dueDate "" --startDate ""

run_update "Get better at using Lucidchart: clear due date" \
    --action update --id "3F08E621-F613-42EC-BB7A-6430BBD7B3E7" --dueDate "" --startDate ""

run_update "Complain about BloodLap: clear due date" \
    --action update --id "4FA09FEE-AF0F-457F-B678-C5FE0F528227" --dueDate "" --startDate ""

run_update "Run immediately after work: clear due date" \
    --action update --id "63F7D721-1B02-4984-A834-66BF49D3BB76" --dueDate "" --startDate ""

run_update "Crypto currency email ca: clear due date" \
    --action update --id "A254311A-365E-48B8-8081-17CDF7DC0CF0" --dueDate "" --startDate ""

run_update "California reclaim filing: clear due date" \
    --action update --id "50C8D3AE-D848-4AC7-9EEC-D3AED04D21A0" --dueDate "" --startDate ""

run_update "Removing dot from email: clear due date" \
    --action update --id "2C99BF9B-6F8D-4DF2-A5F1-89E5795C795E" --dueDate "" --startDate ""

run_update "Putting dad's work into AI: clear due date" \
    --action update --id "68E4708B-4F53-4C71-9C64-B3B3C4B4BA41" --dueDate "" --startDate ""

run_update "MCP for Bee: clear due date" \
    --action update --id "285382C5-D3BA-46EB-A256-E14FFFF85589" --dueDate "" --startDate ""

run_update "Research AI for missionary: clear due date" \
    --action update --id "5DBB70A6-4CE2-4740-AF82-881A0326B179" --dueDate "" --startDate ""

# Followup
run_update "Delaware Corporation Tax: keep due date (real deadline 2028)" \
    --action read-by-id --id "B9A6854B-4946-4D74-B121-C658CE01FE43"
echo "  ℹ️  Skipping — this is a real future deadline (2028-02-25)"

echo ""
echo "============================================"
echo "STEP 2: Re-categorize misplaced tasks"
echo "============================================"

run_update "Complain about BloodLap → Followup" \
    --action update --id "4FA09FEE-AF0F-457F-B678-C5FE0F528227" --targetList "Followup"

run_update "Crypto currency email ca → Finance" \
    --action update --id "A254311A-365E-48B8-8081-17CDF7DC0CF0" --targetList "Finance"

run_update "California reclaim filing → Finance" \
    --action update --id "50C8D3AE-D848-4AC7-9EEC-D3AED04D21A0" --targetList "Finance"

run_update "Schedule for meeting/marathon → Home" \
    --action update --id "3F760663-084F-44E4-90DA-61B02035580E" --targetList "Home"

run_update "Run immediately after work → Home" \
    --action update --id "63F7D721-1B02-4984-A834-66BF49D3BB76" --targetList "Home"

run_update "Research AI for missionary → Seminary (Education)" \
    --action update --id "5DBB70A6-4CE2-4740-AF82-881A0326B179" --targetList "Seminary (Education)"

run_update "Document open pilot → ⚙️ Automation" \
    --action update --id "49EEB632-08EB-4074-8175-4934B83CCACF" --targetList "⚙️ Automation"

run_update "Update openpilot via wifi → ⚙️ Automation" \
    --action update --id "0B4E235E-A26C-45DB-8117-A79916CC0CFC" --targetList "⚙️ Automation"

run_update "Buy cable management → Home" \
    --action update --id "FB0EA458-15E1-4DDA-BF21-71AC1BD2CC68" --targetList "Home"

echo ""
echo "============================================"
echo "STEP 3: Delete Siri dictation errors"
echo "============================================"

run_delete "Delete 'Vocab' from Grocery" "F4B9D516-B0AB-4A06-B835-DD78E63F52E4"
run_delete "Delete 'Tic tic' from Grocery" "3FD7993F-984F-4E4A-A695-0A2293B9441D"
run_delete "Delete 'Slow down more in the intersections exit' from Todo" "4EAD52A3-FB35-4535-AA2B-9BE29DB9360D"

echo ""
echo "============================================"
echo "STEP 4: Set Today tasks with time slots"
echo "============================================"

# Morning (9:00 AM) — Running
run_update "Running → Morning 9AM today" \
    --action update --id "418EE826-D038-4831-A14B-D409FFB3263C" --dueDate "${TODAY}T09:00:00"

# Morning (9:00 AM) — Sending reports
run_update "Sending reports → Morning 9AM today" \
    --action update --id "B81DE1BF-DD66-4C43-8ECA-AB0BAD3A3390" --dueDate "${TODAY}T09:00:00"

# Afternoon (1:00 PM) — Update social profile
run_update "Update social profile → Afternoon 1PM today" \
    --action update --id "52CE6CFA-C55A-4871-A28F-AE3E180BD78B" --dueDate "${TODAY}T13:00:00"

echo ""
echo "============================================"
echo "SUMMARY"
echo "============================================"
echo "✅ Succeeded: $SUCCESS"
echo "❌ Failed: $ERRORS"
