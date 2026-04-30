tell application "Reminders"
	set todayList to every reminder whose due date is less than or equal to (current date) and completed is false
	set countCleared to 0
	repeat with r in todayList
		set due date of r to missing value
		set countCleared to countCleared + 1
	end repeat
	return "Cleared due dates for " & countCleared & " reminders in Apple Reminders."
end tell
