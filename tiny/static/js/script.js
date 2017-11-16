$(document).ready(function() {

  /*
   * Navigation.
   */

  // focus/unfocus navigation search bar on search icon click
  $('.navbar-default .search-form .search-btn').click(function() {
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
  $('a.sign-out').click(function(e) {
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

  // takes a post and creates a card to display
  function createPostCard(post) {
    return (
      '<div class="post-card">' +
        '<div class="col-sm-5 post-image" style="background-image:url(' + post.image_url + ')">' +
          '<a href="/post/' + post.id  +'/show"></a>' +
        '</div>' +
        '<div class="col-sm-7 post-details">' +
          '<div class="post-details-top">' +
            '<a href="/post/' + post.id + '/show">' +
              '<h2 class="title">' + post.title + '</h2>' +
            '</a>' +
            '<a href="/post/' + post.id + '/show">' +
              '<h3 class="preview">' + post.preview + '</h3>' +
            '</a>' +
          '</div>' +
          '<div class="post-details-bottom">' +
            '<div class="wrapper">' +
              '<a href="/user/' + post.author.id + '/show">' +
                '<img src="' + post.author.avatar_url + '" class="avatar" alt="' + post.author.display_name +'\'s avatar">' +
              '</a>' +
            '</div>' +
            '<div class="wrapper">' +
              '<a class="author-name" href="/user/' + post.author.id + '/show">' + post.author.display_name + '</a>' +
              '<span class="created">' + formatDate(post.created) + '</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }

  /*
   * Home page.
   */

  if ($(document.body).hasClass('home')) {
    var size = 12;
    var offset = 0;
  
    function loadPosts() {
      // make sure we hide load button
      var loadMore = $('.load-more').addClass('hidden');

      var url = '/search/query?size=' + size + '&offset=' + offset;

      $.get(url, function(results) {
        postsDiv = $('.posts');

        // append the results to the page
        for (var i = 0; i < results.length; i++) {
          postsDiv.append(
            '<div class="col-sm-6">' +
              createPostCard(results[i]) +
            '</div>'
          );
        }

        // make sure we increase offset so we can page through results
        offset += size;

        // show load button if there are, potentially, more results
        if (results.length == size) {
          loadMore.removeClass('hidden');
        }
      });
    }
  
    // initial first load
    loadPosts();
  
    // make sure we debounce the load button
    $('.load-more').click(_.debounce(loadPosts, 250, { 'leading': true }));
  }

  /*
   * User profile page.
   */

  if ($(document.body).hasClass('user') && $(document.body).hasClass('show')) {
    var size = 12;
    var offset = 0;
  
    function loadPosts() {
      // make sure we hide load button
      var loadMore = $('.load-more').addClass('hidden');

      var userId = window.location.pathname.split('/')[2];
      var url = '/user/' + userId + '/posts?size=' + size + '&offset=' + offset;

      $.get(url, function(results) {
        postsDiv = $('.posts');

        // append the results to the page
        for (var i = 0; i < results.length; i++) {
          postsDiv.append(
            '<div class="col-sm-12">' +
              createPostCard(results[i]) +
            '</div>'
          );
        }

        // make sure we increase offset so we can page through results
        offset += size;

        // show load button if there are, potentially, more results
        if (results.length == size) {
          loadMore.removeClass('hidden');
        }
      });
    }
  
    // initial first load
    loadPosts();
  
    // make sure we debounce the load button
    $('.load-more').click(_.debounce(loadPosts, 250, { 'leading': true }));     
  }

  /*
   * Search pages.
   */

  if ($(document.body).hasClass('search')) {
    var size = 12;
    var offset = 0;
    var terms = getUrlParameter('terms');
    $('.page .search-input').val(terms);
  
    function loadPosts() {
      // make sure we hide load button
      var loadMore = $('.load-more').addClass('hidden');

      var url = '/search/query?terms=' + terms + '&size=' + size + '&offset=' + offset;

      $.get(url, function(results) {
        postsDiv = $('.posts');

        // append the results to the page
        for (var i = 0; i < results.length; i++) {
          postsDiv.append(
            '<div class="col-sm-12">' +
              createPostCard(results[i]) +
            '</div>'
          );
        }

        // make sure we increase offset so we can page through results
        offset += size;

        // show load button if there are, potentially, more results
        if (results.length == size) {
          loadMore.removeClass('hidden');
        }
      });
    }
  
    // initial first load
    if (terms) {
      loadPosts();
    }
  
    // make sure we debounce the load button
    $('.load-more').click(_.debounce(loadPosts, 250, { 'leading': true }));
  
    $('.page .search-form').submit(function(e) {
      e.preventDefault();
      $('.posts').empty();
      terms = $('.page .search-input').val();
      var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?terms=' + terms;
      window.history.pushState({path:newurl},'',newurl);
      offset = 0;
      loadPosts();
    });
  }

  function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  }

});
