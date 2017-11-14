$(document).ready(function() {
  
  /*
   * Navigation.
   */

  // focus/unfocus navigation search bar on search icon click
  $('.navbar-default .glyphicon-search').click(function() {
    $('.navbar-default .search-input').removeClass('collapsed').focus();
  });
    
  // show navigation search form on focus
  $('.navbar-default .search-input').focusin(function() {
    $(this).removeClass('collapsed');
  });
  
  // hide navigation search form on unfocus
  $('.navbar-default .search-input').focusout(function(e) {
    if (!e.target.value) {
      $(this).addClass('collapsed');
    }
  });
  
  /*
   * Sign out.
   */

  // sign user out when clicked
  $('.sign-out').click(function(e) {
    e.preventDefault();
    $.post('/user/sign-out', function() {
      window.location.href = '/user/sign-out';
    });
  });
  
  /*
   * Dates.
   */

  var monthNames = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
  ];

  function formatDate(date) {
    date = new Date(date);
    return monthNames[date.getMonth()] + ' ' + date.getDate();
  }

  /*
   * Post cards.
   */

  function createPostCard(post) {
    return (
      '<div class="post-card">' +
        '<div class="col-sm-5 post-image" style="background-image:url(' + post.image_url + ')">' +
          '<a href="/post/show/' + post.id  +'"></a>' +
        '</div>' +
        '<div class="col-sm-7 post-details">' +
          '<a href="/post/show/' + post.id + '">' +
            '<h2>' + post.title + '</h2>' +
          '</a>' +
          '<a href="/post/show/' + post.id + '">' +
            '<h3>' + post.introduction + '</h3>' +
          '</a>' +
          '<div class="post-bottom">' +
            '<div class="wrapper">' +
              '<a href="/user/show/' + post.author.id + '">' +
                '<img src="' + post.author.avatar_url + '" class="avatar" alt="' + post.author.display_name +'\'s avatar">' +
              '</a>' +
            '</div>' +
            '<div class="wrapper">' +
              '<a class="author-name" href="/user/show/' + post.author.id + '">' + post.author.display_name + '</a>' +
              '<span class="published">' + formatDate(post.published) + '</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }
  
  /*
   * Home page.
   */

  if ($(document.body).hasClass('home') || $(document.body).hasClass('user-show')) {
    var size = 12;
    var offset = 0;
    var order = true;

    // CHANGE THIS
    var columns = $(document.body).hasClass('home') ? 6 : 12;
  
    function loadPosts() {
      // make sure we hide load button
      var loadMore = $('.load-more').hide();

      var url = '/post/search?size=' + size + '&offset=' + offset + '&order=' + order;

      $.get(url, function(results) {
        postsDiv = $('.posts');

        // append the results to the page
        for (var i = 0; i < results.length; i++) {
          postsDiv.append(
            '<div class="col-sm-' + columns + '">' +
              createPostCard(results[i]) +
            '</div>'
          );
        }

        // make sure we increase offset so we can page through results
        offset += size;

        // show load button if there are, potentially, more results
        if (results.length == size) {
          loadMore.show();
        }
      });
    }
  
    // initial first load
    loadPosts();
  
    // make sure we debounce the load button
    $('.load-more').click(_.debounce(loadPosts, 250, { 'leading': true })); 
  }

});
    