function updateCountdowns() {
	$("#pcWait").text(getCountdownText(pcReport, "Pitchers and catchers",
		"reported", "report"));
	$("#exWait").text(getCountdownText(exOpener, "The exhibition season",
		"began", "begins"));
	$("#rsWait").text(getCountdownText(rsOpener, "The regular season",
		"began", "begins"));
};

function getCountdownText(event, subject, pastVerb, futureVerb) {
	if(moment().isAfter(event)) {
		var verb = pastVerb;
	} else {
		var verb = futureVerb;
	}
	return(subject + " " + verb + " " + event.fromNow() + " (" + event.calendar() + ").");
};