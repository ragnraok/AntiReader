(function () {
  function handle() {
    var location = window.location.toString();
    var timeline = new Timeline();
    var sourcelist = new SourceList();
    if (location.indexOf("timeline") !== -1) {
      timeline.handle();
    }
    else if (location.indexOf("sourcelist") != -1) {
      //sourcelist.handle();
    }
  }

  function Timeline() {
    this.moreArticleTmpl =
      ["<a class=\"article-item-link\" href=\"#\">",
        "<div class=\"article-item pure-g\">",
        "<div class=\"pure-u-3-4\">",
        "<h5 class=\"article-name\"  id={article.id}>{article.name}</h5>",
        "</div>",
        "</div>",
        "</a>"].join("\n");
  };

  Timeline.prototype = {
    constructor: Timeline,

    handle: function () {
      this.loadDefaultArticle();
      this.loadDefaultArticle()
      this.initLoadArticle();
      this.initAddMoreArticle();
    },

    loadDefaultArticle: function () {
      var $articleContainer = $('#main');
      var $articleItem = $('.article-name').first();
      var articleId = $articleItem.attr('id');
      $articleContainer.load("/timeline/" + articleId);
      this.updateTimelineBoxClass(articleId);
    },

    initLoadArticle: function () {
      var $articleContainer = $("#main");
      var $articleItem = $(".article-item-link");
      var that = this;
      $("#article-list").delegate(".article-item-link", "click", function (event) {
        event.stopPropagation();
        $("#loading-article-prompt").show();
        $target = $(event.target);
        var articleId;
        if ($target.prop('tagName') == 'DIV') {
          articleId = $target.find('.article-name').attr('id');
        }
        else {
          articleId = $target.attr('id');
        }
        if (articleId) {
          $articleContainer.load("/timeline/" + articleId, function () {
            $("#loading-article-prompt").hide();
            that.updateTimelineBoxClass(articleId);
          });
        }
      });
    },

    updateTimelineBoxClass: function (articleId) {
      var $allItem = $(".article-item");
      $allItem.each(function (index, element) {
        element = $(element);
        var $articleName = element.find(".article-name");
        var id = $articleName.attr("id");
        if (id === articleId) {
          element.addClass("article-item-selected");
        }
        else {
          element.removeClass("article-item-selected");
        }
      });
    },

    initAddMoreArticle: function () {
      var moreArticleButton = $(".load-more-article-box");
      var page = 1;
      var that = this;
      moreArticleButton.click(function (event) {
        var originText = event.target.innerHTML;
        event.target.innerHTML = "Loading..."
        var loadUrl = "/timeline/load_articles/" + page + "/";
        $.get(loadUrl, function (data) {
          info = data.info;
          lastPage = data.last_page
          if (lastPage == false) {
            that.appendArticle(info);
            event.target.innerHTML = originText;
            page++;
          }
          else {
            moreArticleButton.hide();
            $("#no-more-article-prompt").show();
          }
        });
      });
    },

    appendArticle: function (articles) {
      var $articleList = $("#article-list");
      for (var i = 0; i < articles.length; i++) {
        article_info = {
          article:{
            id: articles[i].id,
            name: articles[i].name
          }
        }
        var renderResult = nano(this.moreArticleTmpl, article_info);
        $articleList.append(renderResult);
      }
    }
  };

  function SourceList() {

  };

  SourceList.prototype = {
    handle: function() {
    }
  };


  /*
  * the nano template engine: https://github.com/trix/nano/blob/master/nano.js
  */
  function nano(template, data) {
    return template.replace(/\{([\w\.]*)\}/g, function(str, key) {
      var keys = key.split("."), v = data[keys.shift()];
      for (var i = 0, l = keys.length; i < l; i++) v = v[keys[i]];
      return (typeof v !== "undefined" && v !== null) ? v : "";
    })
  };

  // start handle
  $(document).ready(function () {
    handle();
  });

})();
