phrases = [];
$(function() {
	$('#sentiment_submit').bind('click', function() {
		if ($('input[name="sentiment"]:checked').length && $('input[name="relevance"]:checked').length) {
			$.post($SCRIPT_ROOT + '/set_sentiment', {
				'sentiment': $('input[name="sentiment"]:checked').val(),
				'relevance': $('input[name="relevance"]:checked').val(),
				'phrases': phrases
			}, function(data) {
				if(data.error==0) {
					$('#document_text').text(data.text);
					phrases = [];
					$('#phrase_box').html('');
					$('input[name="sentiment"]').prop('checked', false);
					$('input[name="relevance"]').prop('checked', false);
				} else if(data.error==1) {
					alert('Submission failed, please try again later.')
				} else alert('Submission error, please contact the administrator.');
			}, 'json');
			return false;
		} else {
			alert('Please enter a value for both the sentiment and a relevance.')
		}
		return false;
	});
});
selected = Array.apply(null, Array(text.length)).map(Number.prototype.valueOf,-1);
lastIndex = -2;
function update_view() {
	var ht = '';
	phrases = [];
	for (var i = 0; i < selected.length; i++) {
		if(selected[i] != -1) {
			var beg = i;
			var end = beg;
			for(end;end<selected.length && selected[end] == selected[beg];end++);
			var phrase = text.slice(beg,end).join(' ');
			ht += '<span onclick="add_phrase('+selected[i]+')" class="highlighted">' +
			phrase + '</span> ';
			phrases.push(phrase);
			i = end - 1;
		} else {
			ht += '<span onclick="add_phrase('+ i +')">'+text[i]+'</span> ';
		}
	}
	$('#document_text').html(ht);
	$('#phrase_box').html(phrases.join("<br/>"));
}
function add_phrase(index) {
	if(selected[index] != -1) { // The word is currently highlighted.
		var curGroup = selected[index]; // The group this word belongs to.
		// Dissolve the group.
		var i = index;
		while(i < selected.length && selected[i] == curGroup) {
			selected[i] = -1;
			i+=1;
		}
		i = index - 1;
		while(i >= 0 && selected[i] == curGroup) {
			selected[i] = -1;
			i-=1;
		}
		lastIndex = -2;
	} else { // The word is not highlighted.
		if(lastIndex-index == -1 || lastIndex-index == 1) { // Adjacent word selected.
			selected[index] = selected[lastIndex];
		} else {
			selected[index] = index;
		}
		lastIndex = index;
	}
	update_view();
}