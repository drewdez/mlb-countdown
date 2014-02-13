var pcPassed = false;
var exPassed = false;
var rsPassed = false;

var msecPerMinute = 1000 * 60;
var msecPerHour = msecPerMinute * 60;
var msecPerDay = msecPerHour * 24;

function updateCountdowns() {
	var now = new Date();
	if(!pcPassed) {
		pcPassed = getWait(now, pcReport, "Pitchers and catchers have reported!",
			"pitchers and catchers report.", "#pcWait");
	}
	if(!exPassed) {
		exPassed = getWait(now, exOpener, "The exhibition season has begun!",
			"the exhibition season begins.", "#exWait");
	}
	if(!rsPassed) {
		rsPassed = getWait(now, rsOpener, "The regular season has begun!",
			"the regular season begins.", "#rsWait");
	}
};

function getWait(currentTime, eventTime, passedText, comingText, targetObject) {
	var timeDiff = eventTime - currentTime;
	if(timeDiff > 0) {
		var countdownString = "";	
		leader = true;
		var days = Math.floor(timeDiff / msecPerDay);
		timeDiff -= (days * msecPerDay);
		var hours = Math.floor(timeDiff / msecPerHour);
		timeDiff -= (hours * msecPerHour);
		var minutes = Math.floor(timeDiff / msecPerMinute);
		timeDiff -= (minutes * msecPerMinute);
		var seconds = Math.floor(timeDiff / 1000);

		var countdownArray = [[days, "day"], [hours, "hour"], 
							 [minutes, "minute"], [seconds, "second"]];

		for(var i = 0; i < countdownArray.length; i++) {
			if(countdownString !== "") {
				leader = false;
			}
			countdownString += getCountdownStringComponent(countdownArray[i][0],
				countdownArray[i][1], leader);
		}

		countdownString = countdownString.concat(" until " + comingText);
		$(targetObject).text(countdownString);
		return false //indicates date has not passed
	}
	else {
		$(targetObject).text(passedText);
		return true //indicates date has passed
	}
};

function getCountdownStringComponent(value, unit, leader) {
	component = "";
	if(value > 0) {
		if(!leader) {
			component += ", ";
		}
		component += (value + " " + unit);				
		if(value > 1) {
			component += "s";
		}
	}
	return component;
}