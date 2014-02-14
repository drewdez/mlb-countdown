$(document).ready(function() {
	$('#placeholder').prop('selected', true);
	$("form").submit(function( event ) {
		console.log($("select").val());
		if($("select").val() === null) {
			event.preventDefault();
		}
	});
});