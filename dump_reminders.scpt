-- Dump all incomplete reminders per list as JSON-like lines
tell application "Reminders"
	set targetLists to {"⚙️ Automation", "Home", "Seminary (Education)", "Cleaning", "Shelved", "Finance", "Followup", "Todo", "Bee", "Open pilot", "Shopping", "Costco", "Grocery", "Prescription", "Wishlist", "Transfer money"}
	set output to ""
	repeat with listName in targetLists
		try
			set aList to list listName
			set rems to (every reminder of aList whose completed is false)
			repeat with r in rems
				set rName to name of r
				set rID to id of r
				try
					set dDate to due date of r
					set dStr to (dDate as string)
				on error
					set dStr to "none"
				end try
				set output to output & listName & "	" & rID & "	" & rName & "	" & dStr & linefeed
			end repeat
		end try
	end repeat
	return output
end tell
