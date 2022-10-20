$(document).ready(function() {
  $('#identification').submit(function(event) {
    event.preventDefault();
    sendAjaxForm("#identification_form");
  });
});

function sendAjaxForm(form_ajax) {
  var form = $(form_ajax);
  $.ajax({
    url: form.attr('action'),
    type: 'POST',
    data: form.serialize(),
    success: function (response) {
      if (response["success"] == true) {
        var url = response["url"];
        setLocation(url);
        $("#identification").slideUp(300, loadContent(url));
      } else {
        console.log("Ошибка");
        console.log(response);
      }
    }
  });
}
function setLocation(curLoc){
    try {
      history.pushState(null, null, curLoc);
      return;
    } catch(e) {}
    location.hash = '#' + curLoc;
}
function loadContent(url) {
  var toLoad = url;
  console.log(toLoad);
  $('html').load(toLoad,'', null);
}