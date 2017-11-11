$(document).ready(function() {

  // focus/unfocus navigation search bar on search icon click
  $('.navbar-default .glyphicon-search').click(function() {
    $('.navbar-default .search-input').removeClass('collapsed').focus()
  });
  
  // show navigation search form
  $('.navbar-default .search-input').focusin(function() {
    $(this).removeClass('collapsed');
  });

  // hide navigation search form
  $('.navbar-default .search-input').focusout(function(e) {
    if (!e.target.value) {
      $(this).addClass('collapsed');
    }
  });

  // sign user out when button in navbar clicked
  $('.navbar-default .sign-out').click(function() {
    $.post('/user/sign-out', function() {
      window.location.href = '/user/sign-out';
    });
  });

});
  