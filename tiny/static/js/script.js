$(document).ready(function() {

  /*
   * Helpers.
   */

  function handleSignOut(e) {
    e.preventDefault();
    $.post('/user/sign-out', function() {
      window.location.href = '/user/sign-out';
    });
  }

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
    return monthNames[date.getMonth()] + ' ' + date.getDate() + ' ' + date.getFullYear();
  }

  function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  }

  // NEED TO SORT THIS OUT!!!!!!
  function addPostLoader(options) {
    // get and normalise the options
    var baseUrl = options.baseUrl;
    var limit = options.limit || 12;
    var skip = options.skip || 0;
    var postCardCols = options.postCardCols || 12;
    var postsContainer = options.postsContainer || $('.posts');
    var loadMoreBtn = options.loadMoreBtn || $('.load-more');
    var initialLoad = options.initialLoad;

    function loadPosts() {
      // should hide button when we trigger another request
      loadMoreBtn.addClass('hidden');

      var url = baseUrl + '?limit=' + limit + '&skip=' + skip;

      $.get(url, function(results) {
        // append the results to the page
        for (var i = 0; i < results.length; i++) {
          postsContainer.append(createPostCard(results[i], postCardCols));
        }

        // make sure we increase skip so we can page through results
        skip += limit;

        // show button if there are, potentially, more results
        if (results.length == limit) {
          loadMoreBtn.removeClass('hidden');
        }
      }, 'json');
    }

    if (initialLoad) {
      loadPosts();
    } else {
      loadMoreBtn.removeClass('hidden');
    }

    // make sure we debounce the button
    loadMoreBtn.click(_.debounce(loadPosts, 250, { 'leading': true }));

    return {
      setBaseUrl: function(url) {
        baseUrl = url;
      },
      setSkip: function(newSkip) {
        skip = newSkip;
      },
      reload: loadPosts
    }
  }

  // takes a post and creates a card to display
  function createPostCard(post, wrapperCols) {
    if (!wrapperCols) {
      wrapperCols = 12;
    }

    var postCard = $(
      '<div class="post-card-wrapper col-sm-' + wrapperCols + '">' +
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
                '<h3 class="lead-paragraph">' + post.lead_paragraph + '</h3>' +
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
        '</div>' +
      '</div>'
    );

    // so long titles and paragraphs are truncated
    postCard.find('.title, .lead-paragraph').dotdotdot({ height: 'watch', watch: true });
    
    return postCard;
  }

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

  $('.navbar-default .sign-out').click(handleSignOut);
  
  /*
   * Home page.
   */

  if ($(document.body).hasClass('home')) {
    addPostLoader({
      baseUrl: '/post/latest',
      postCardCols: 6,
      initialLoad: true
    });
  }

  /*
   * User profile page.
   */

  if ($(document.body).hasClass('user') && $(document.body).hasClass('show')) {
    addPostLoader({
      baseUrl: '/user/' + window.location.pathname.split('/')[2] + '/posts',
      initialLoad: true,
    });
  }

  /*
   * User sign out page.
   */

  if ($(document.body).hasClass('user') && $(document.body).hasClass('sign-out')) {
    $('.page .sign-out').click(handleSignOut);
  }

  /*
   * Search page.
   */

  if ($(document.body).hasClass('search')) {
    var terms = encodeURIComponent(getUrlParameter('terms'));
    $('.page .search-input').val(decodeURIComponent(terms));

    var postLoader = addPostLoader({
      baseUrl: '/search?terms=' + terms,
      initialLoad: true,
    });
  
    $('.page .search-form').submit(function(e) {
      e.preventDefault();
      $('.posts').empty();
      terms = encodeURIComponent($('.page .search-input').val());
      var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?terms=' + terms;
      window.history.pushState({path:newurl},'',newurl);
      postLoader.setBaseUrl('/search?terms=' + terms);
      postLoader.setSkip(0);
      postLoader.reload();
    });
  }

  if ($(document.body).hasClass('post')) {
    $('#preview-select').click(function() {
      $.post('/post/preview', {
        'content': $('#content').val()
      }, function(e) {
        $('#preview-tab').empty().append(
          '<h1>' + $('#title').val() + '</h1>' +
          '<p class="lead">' + $('#lead_paragraph').val() + '</p>' +
          '<img class="post-img" src="' + $('#image_url').val() + '" alt="' + $('#title').val() + '">'
        ).append(e.html);
      });
    });
  }

  /*
   * Comments.
   */

  $(".comment-form").submit(function(e) {
    e.preventDefault();
    var url = $(".comment-form").attr("action");
    $.post(url, $(".comment-form").serialize(), function(res) {
      $(".comment-form")[0].reset();
    }).fail(function(res) {
      console.log(res.responseJSON.errors);
    });
  });

  if ($(document.body).hasClass('post') && $(document.body).hasClass('show')) {
    var limit = 12;
    var skip = 0;
    var loadMoreBtn = $('.load-more-comments');
    var postId = window.location.pathname.split('/')[2];
    var commentsContainer = $('.comments');

    function loadComments() {
      var url = '/post/' + postId + '/comments?limit=' + limit + '&skip=' + skip;

      $.get(url, function(results) {
        // append the comments to the page
        for (var i = 0; i < results.length; i++) {
          commentsContainer.append(createCommentCard(results[i]));
        }

        // make sure we increase skip so we can page through comments
        skip += limit;

        // show button if there are, potentially, more results
        if (results.length != limit) {
          loadMoreBtn.addClass('hidden');
        } else {
          loadMoreBtn.removeClass('hidden');
        }
      }, 'json');
    }

    loadComments();

    // make sure we debounce the button
    loadMoreBtn.click(_.debounce(loadComments, 250, { 'leading': true }));
  }

  function createCommentCard(comment) {
    return (
      '<div class="comment-card">' +
        '<div class="author-info">' +
          '<div class="wrapper">' +
            '<a class="author-name" href="/user/' + comment.author.id  + '/show">' +
              '<img class="avatar" src="' + comment.author.avatar_url +'">' +
            '</a>' +
          '</div>' +
          '<div class="wrapper">' +
            '<a class="author-name" href="/user/' + comment.author.id  + '/show">' +
              comment.author.display_name +
            '</a>' +
            '<span class="date">' +
              formatDate(comment.created) +
            '</span>' +
          '</div>' +
        '</div>' +
        '<div class="text">' +
          comment.text +
        '</div>' +
      '</div>'
    );
  }

});
