(function () {
  // add format method
  if (!String.prototype.format) {
    String.prototype.format = function() {
      var args = arguments;
      return this.replace(/\{(\d+)\}/g,
        function(m,i){
            return args[i];
        });
    }
  }

  function handle() {
    var location = window.location.toString();
    var timeline = new Timeline();
    var sourcelist = new SourceList();
    var subscribe = new Subscribe();
    subscribe.handle();
    if (location.indexOf("timeline") !== -1) {
      timeline.handle();
    }
    else if (location.indexOf("sourcelist") != -1) {
      sourcelist.handle();
    }
  }

  function Timeline() {
    this.moreArticleTmpl =
      ["<a class=\"article-item-link\" href=\"#\">",
        "<div class=\"article-item pure-g\">",
        "<div class=\"pure-u-3-4\">",
        "<h5 class=\"article-name\"  id={article.id}>{article.name}</h5>",
        "</div>",
        "<div class=\"pure-u-3-4\">",
        "<p class=\"article-source\" id={article.id}>{article.site}</p>",
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
        if ($target.prop('tagName') == 'DIV') { // select the parent div
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
        var loadUrl = "/timeline/load_articles/{0}/".format(page);
        $.get(loadUrl, function (data) {
          if (data.success) {
            info = data.data.info;
            lastPage = data.data.last_page
            if (lastPage == false) {
              that.appendArticle(info);
              event.target.innerHTML = originText;
              page++;
            }
            else {
              if (info) {
                that.appendArticle(info);
              }
              moreArticleButton.hide();
              $("#no-more-article-prompt").show();
            }
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
            name: articles[i].name,
            site: articles[i].site
          }
        }
        var renderResult = nano(this.moreArticleTmpl, article_info);
        $articleList.append(renderResult);
      }
    }
  };

  function SourceList () {
    this.$idList = $(".site-delete");
    this.$modal = $("#unsubscribe-modal");
    this.$modalPrompt = $("#unsubscribing-prompt");
    this.$confirmButton = $("#confirm-unsubscribe");

    this.$modal.modal({
      keyboard: true,
      show: false
    })

    this.unsubscribeUrl = "/sourcelist/unsubscribe/{0}/";
  };

  SourceList.prototype = {
    constructor: SourceList,

    handle: function() {
      this.initUnsubscribe();
    },

    initUnsubscribe: function() {
      var that = this;
      this.$idList.on('click', function(event) {
        var $target = $(event.target);
        var id = $target.attr("id");
        var $titleBox = $(".site-title").filter("#" + id);
        var title = $titleBox.text();
        //console.log("title = " + title);

        var $parentBox = $(".source-grid").filter("#" + id);
        //console.log($parentBox);

        that.$modalPrompt.text("确认取消订阅 <" + title + "> 吗？");
        that.$modal.modal('show');
        that.$confirmButton.on('click', function() {
          that.$modal.modal('hide');
          $parentBox.fadeOut();

          // unsubscribe
          that.unsubscribe(id);
        });
      });
    },

    unsubscribe: function(siteId) {
      console.log("in unsubscribe");
      $.post(this.unsubscribeUrl.format(siteId));
    }
  };

  Subscribe = function () {
    this.buttonId = "#subscribe-source";
    this.modalId = "#subscribe-modal";
    this.formId = "#new-source-form";
    this.inputId = "#new-source-site";
    this.promptId = "#subscribing-prompt";
    this.confirmId = "#confirm-subscribe";
    this.cancelId = "#cancel-subscribe";

    this.$button = $(this.buttonId);
    this.$modal = $(this.modalId);
    this.$newSourceForm = $(this.formId);
    this.$input = $(this.inputId);
    this.$prompt = $(this.promptId);
    this.$confirmButton = $(this.confirmId);
    //this.$cancelButton = $(this.cancelId);
    //
    this.subscribeUrl = "/subscribe/";
  };

  Subscribe.prototype = {
    constructor: Subscribe,

    handle: function () {
      var that = this;
      this.$button.on('click', function() {
        that.$confirmButton.show();
        that.$modal.modal('show');
        that.$newSourceForm.show();
        that.$prompt.hide();
        that.$input.val("");
      });

      //this.$cancelButton.on('click', function() {
      //  console.log("click canel");
      //  that.$modal.modal('hide');
      //});

      this.$confirmButton.click(function() {
        site = that.$input.val();
        if (site) {
          that.subscribe(site);
        }
      });

    },

    subscribe: function (site) {
      var that = this;
      this.$newSourceForm.fadeOut(function () {
        that.$prompt.show();
        that.$confirmButton.hide();
        //var promptText = that.$prompt.text();
        // subscribe
        $.post("/subscribe/", {'site': site}, function(data, textStatus, xhr) {
          console.log(xhr.status);
          if (xhr.status != 200) {
            that.$prompt.text('订阅失败');
            window.setTimeout(function() {
              that.$modal.modal('hide');
            }, 2000);
          }
          var success = data.success;
          if (success) {
            that.$prompt.text('订阅成功');
            window.setTimeout(function() {
              that.$modal.modal('hide');
              if (window.location.toString().indexOf('sourcelist') != -1) {
                window.location.reload();
              }
            }, 2000);
          }
          else {
            that.$prompt.text('订阅失败');
            window.setTimeout(function() {
              that.$modal.modal('hide');
            }, 2000);
          }
        }, "json");
      });
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
