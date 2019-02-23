/*
 * Helpers
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
  var parsedDate = new Date(date);
  return monthNames[parsedDate.getMonth()] + ' ' + parsedDate.getDate() + ' ' + parsedDate.getFullYear();
}

function getUrlParameter(name) {
  var regex = new RegExp('[\\?&]' + name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]') + '=([^&#]*)');
  var results = regex.exec(location.search);
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

function PostLoader(options) {
  // get and normalise options
  this.baseUrl = options.baseUrl;
  this.urlParameters = options.urlParameters || '';
  this.limit = options.limit || 12;
  this.skip = options.skip || 0;
  this.postCardCols = options.postCardCols || 12;
  this.postsContainer = options.postsContainer || $('.posts');
  this.loadMoreBtn = options.loadMoreBtn || $('.load-more');

  this.loadPosts = this.loadPosts.bind(this);

  // make sure we debounce load more button
  this.loadMoreBtn.click(_.debounce(this.loadPosts, 250, { 'leading': true }));
}

PostLoader.prototype.loadPosts = function() {
  // should hide button when we trigger another request
  this.loadMoreBtn.addClass('hidden');

  // build the request url
  var url = this.baseUrl + '?limit=' + this.limit + '&skip=' + this.skip;
  if (this.urlParameters) {
    url += '&' + this.urlParameters;
  }

  $.get(url, function(results) {
    // append the results to the page
    results.forEach(function(result) {
      this.postsContainer.append(createPostCard(result, this.postCardCols));
    }.bind(this));

    // make sure we increase skip so we can page through results
    this.skip += results.length;

    // show button if there are, potentially, more results
    if (results.length === this.limit) {
      this.loadMoreBtn.removeClass('hidden');
    }
  }.bind(this), 'json');
};

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

function CommentLoader(options) {
  // get and normalise options
  this.postId = options.postId;
  this.limit = options.limit || 12;
  this.skip = options.skip || 0;
  this.commentsContainer = options.commentsContainer || $('.comments');
  this.loadMoreBtn = options.loadMoreBtn || $('.load-more-comments');

  this.loadComments = this.loadComments.bind(this);

  // make sure we debounce load more button
  this.loadMoreBtn.click(_.debounce(this.loadComments, 250, { 'leading': true }));
}

CommentLoader.prototype.loadComments = function() {
  // should hide button when we trigger another request
  this.loadMoreBtn.addClass('hidden');

  // build the request url
  var url = '/post/' + this.postId + '/comments?limit=' + this.limit + '&skip=' + this.skip;

  $.get(url, function(results) {
    // append the comments to the page
    results.forEach(function(result) {
      this.commentsContainer.append(createCommentCard(result));
    }.bind(this));

    // make sure we increase skip so we can page through comments
    this.skip += results.length;

    // show the button again
    this.loadMoreBtn.removeClass('hidden');
  }.bind(this), 'json');
};

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

/*
 * Navigation
 */

// focus/unfocus navigation search bar on search icon click
$('.navbar-default .search-form .search-btn').click(function() {
  $('.navbar-default .search-input').removeClass('collapsed').focus();
});
  
// show navigation search form on focus
$('.navbar-default .search-input').focusin(function() {
  $('.navbar-default .search-input').removeClass('collapsed');
});

// hide navigation search form on unfocus
$('.navbar-default .search-input').focusout(function(e) {
  if (!e.target.value) {
    $('.navbar-default .search-input').addClass('collapsed');
  }
});

$('.navbar-default .sign-out').click(handleSignOut);

/*
 * Home page
 */

if ($(document.body).hasClass('home')) {
  new PostLoader({
    baseUrl: '/post/latest',
    postCardCols: 6
  }).loadPosts();
}

/*
 * User pages
 */

if ($(document.body).hasClass('user')) {
  // show page
  if ($(document.body).hasClass('show')) {
    new PostLoader({
      baseUrl: '/user/' + window.location.pathname.split('/')[2] + '/posts'
    }).loadPosts();
  } 
  
  // sign out page
  else if ($(document.body).hasClass('sign-out')) {
    $('.page .sign-out').click(handleSignOut);
  }
}

/*
 * Post pages
 */

if ($(document.body).hasClass('post')) {
  // show page
  if ($(document.body).hasClass('show')) {
    // load the comments
    new CommentLoader({
      postId: window.location.pathname.split('/')[2]
    }).loadComments();

    var commentForm = $('.comment-form');

    commentForm.find('#text').on('input', function() {
      commentForm.find('.form-group').removeClass('has-error');
      commentForm.find('.help-block').text('');
    });

    // leave comment on form submit
    commentForm.submit(function(e) {
      e.preventDefault();

      var url = commentForm.attr('action');

      $.post(url, commentForm.serialize(), function() {
        commentForm[0].reset();
        commentForm.find('.form-group').removeClass('has-error');
        commentForm.find('.help-block').text('Added comment!');
      }).fail(function(response) {
        commentForm.find('.form-group').addClass('has-error');
        commentForm.find('.help-block').text(response.responseJSON.errors);
      });
    });
  }

  // create/update page
  if ($(document.body).hasClass('create') || ($(document.body).hasClass('update'))) {
    // update preview tab on click
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
}

/*
 * Search page
 */

if ($(document.body).hasClass('search')) {
  // get search terms from the url and add to search input
  var terms = encodeURIComponent(getUrlParameter('terms'));
  $('.page .search-input').val(decodeURIComponent(terms));

  // load the posts
  var postLoader = new PostLoader({
    baseUrl: '/search',
    urlParameters: 'terms=' + terms
  });

  postLoader.loadPosts();

  // perform search on form submit
  $('.page .search-form').submit(function(e) {
    e.preventDefault();

    // make sure we clear current posts
    $('.posts').empty();
    
    // set new url with terms
    terms = encodeURIComponent($('.page .search-input').val());
    var newurl = window.location.protocol + '//' + window.location.host + window.location.pathname + '?terms=' + terms;
    window.history.pushState({ path:newurl }, '', newurl);
    
    // update the post load and perform query
    postLoader.urlParameters = 'terms=' + terms;
    postLoader.skip = '0';
    postLoader.loadPosts();
  });
}
