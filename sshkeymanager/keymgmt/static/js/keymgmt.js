$( document ).ready(function() {
var substringMatcher = function(strs) {
  return function findMatches(q, cb) {
    var matches, substrRegex;
 
    // an array that will be populated with substring matches
    matches = [];
 
    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');
 
    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        // the typeahead jQuery plugin expects suggestions to a
        // JavaScript object, refer to typeahead docs for more info
        matches.push({ value: str });
      }
    });
 
    cb(matches);
  };
};

/*
*    SSH Account Key Update
*/

$('#sshaccount_keyring_view .typeahead').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
},
{
  name: 'sshkeyrings',
  displayKey: '',
  source: substringMatcher(sshkeyrings)
});

$('#sshaccount_keyring_view').bind('typeahead:selected', function(obj, search, name) {
    $('<li class="tag-cloud">'+search.value+'</li>').appendTo("#sshaccount_keyrings");
    $('#sshaccount_keyring_selector').val('');
    return false;
});

$('#sshaccount_key_view .typeahead').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
},
{
  name: 'sshkeys',
  displayKey: '',
  source: substringMatcher(sshkeys)
});

$('#sshaccount_key_view').bind('typeahead:selected', function(obj, search, name) {
    $('<li class="tag-cloud">'+search.value+'</li>').appendTo("#sshaccount_keys");
    $('#sshaccount_key_selector').val('');
    return false;
});


$("#sshaccount_key_update_submit").click(function(e){
    var keyrings = [];
    $('#sshaccount_keyrings').find('li').each(function() {
        keyrings.push($(this).text());
    });
    $('#keyrings').val(keyrings.join(','));
    var keys = [];
    $('#sshaccount_keys').find('li').each(function() {
        keys.push($(this).text());
    });
    $('#keys').val(keys.join(','));
});


/*
*    SSH Keyring add Keys
*/

$('#sshkeyring_keys .typeahead').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
},
{
  name: 'sshkeys',
  displayKey: '',
  source: substringMatcher(sshkeys)
});

$('#sshkeyring_keys').bind('typeahead:selected', function(obj, search, name) {
    $('<li class="tag-cloud">'+search.value+'</li>').appendTo("#sshkeys");
    $('#keys_selector').val('');
    return false;
});


$('#sshaccount_name .typeahead').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
},
{
  name: 'sshaccount_available',
  displayKey: '',
  source: substringMatcher(sshaccount_available)
});



$("#sshkeyring_submit").click(function(e){
    var keys = [];
    $('#sshkeys').find('li').each(function() {
        keys.push($(this).text());
    });
    $('#keys').val(keys.join(','));
});


});