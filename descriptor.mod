version="0.91"
tags={
	"1.18 'Crane'"
	"Character Interactions"
	"Decisions"
	"Events"
}
name="Relics of Legend: The Old World"
supported_version="1.18.4"

	
//if = {
		limit = { exists = scope:newly_created_artifact }
		scope:newly_created_artifact = {
			set_owner = root
		}
	}