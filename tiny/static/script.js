$(document).ready(function() {
  
  // focus/unfocus navigation search bar on search icon click
  $('.navbar-default .glyphicon-search').click(function() {
    $('.navbar-default input').focus();
  });
  
  // show navigation search form
  $('.navbar-default input').focusin(function() {
    $('form').addClass('expanded');
  });

  // hide navigation search form
  $('.navbar-default input').focusout(function(e) {
    if (!e.target.value) {
      $('form').removeClass('expanded');
    }
  });

});
  