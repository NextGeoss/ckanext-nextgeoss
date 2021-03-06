function communityFeedback(catalogueID, catalogueNamespace, title)
// Create a community feedback and insert it into the page.
{
  this.catalogueID = catalogueID;
  this.catalogueNamespace = catalogueNamespace;
  this.title = title;

  this.getFeedbackUrl = function() {
    // Get the URL for feedback feed.
    var url = 'https://www.opengis.uab.cat/cgi-bin/nimmbus/nimmbus.cgi?SERVICE=WPS&REQUEST=EXECUTE&IDENTIFIER=NB_RESOURCE:ENUMERATE&CONTENT=full&LANGUAGE=eng&STARTINDEX=1&COUNT=100&FORMAT=text/xml&TYPE=FEEDBACK&TRG_TYPE_1=CITATION&TRG_FLD_1=CODE&TRG_VL_1='+this.catalogueID+'&TRG_OPR_1=EQ&TRG_NXS_1=AND&TRG_TYPE_2=CITATION&TRG_FLD_2=NAMESPACE&TRG_VL_2='+this.catalogueNamespace+'&TRG_OPR_2=EQ'
    return url
  };

  this.getAddFeedbackUrl = function() {
    // Get the URL for adding feedback.
    var url = 'https://www.opengis.uab.cat/nimmbus/index.htm?target_title='+this.title+'&target_code='+this.catalogueID+'&target_codespace='+this.catalogueNamespace+'&page=ADDFEEDBACK&share_borrower_1=Anonymous'
    return url
  };

  this.loadFeedback = function() {
    // Initiate the process of inserting the community feedback into the page.
    // Called when the page is first loaded.
    var url = this.getFeedbackUrl();
    var context = {
      "action": "show",
    };
    this.getFromNimmbus(url, showFeedback, context);
  };

  this.showFeedback = function(feedbackFeed, context) {
    // Show the feedback if there's feedback. If there's no feedback,
    // show a message instead.
    var entries = this.xmlToEntries(feedbackFeed);

    if (entries.length == 0) {
      $("#community-feedback-anchor").after('<p class="feedback-item" id="no-comments-yet">No comments yet. Be the first to leave feedback about this dataset.</p>')
    } else {
      $("#community-feedback-anchor").after('<ul class="feedback-list"><div id="start-feedback-items"></div><div id="end-feedback-items"></div></ul>');
    
      // Insert the core of each feedback item into the page and
      // then request and insert the rest of it when it is available.
      for(var i = 0, size = entries.length; i < size ; i++){

        var entryDict = this.createBaseEntryDict(entries[i]);
        this.renderFeedbackFeed(entryDict, context);

        context = {
          "action": "show",
          "commentId": entryDict["commentId"]
        };
      };
    };
    this.readMore();
  };

  this.createBaseEntryDict = function(entry) {
    // Parse the entry XML from the feebdack feed and return a dictionary
    // with the important data.
    var title = entry.getElementsByTagName("title")[0].textContent;

    var author = entry.getElementsByTagName("name")[0].textContent;

    var updated = entry.getElementsByTagName("updated")[0].textContent;

    var link = entry.getElementsByTagName("link")[0].getAttribute("href");

    var commentId = link.split("RESOURCE=")[1].split("&USER=")[0];

    var content = entry.getElementsByTagName("content")[0];

    try {
      var abstract = content.getElementsByTagName("guf\:abstract")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent;
    } catch(err) {
      try {
        abstract = content.getElementsByTagName("abstract")[0]
          .getElementsByTagName("CharacterString")[0].textContent;
      } catch(err) {
        abstract = "";
      };
    };
    if (abstract.length == 0) {
    abstract = "No abstract available"
    };

    try {
      var rating = content.getElementsByTagName("guf\:GUF_RatingCode")[0]
        .getAttribute("codeListValue");
    } catch(err) {
      try {
        var rating = content.getElementsByTagName("GUF_RatingCode")[0]
          .getAttribute("codeListValue");
      } catch(err) {
        var rating = ""
      };
    };
    if (rating.length == 0) {
      rating = "No rating available"
    };


    try {
      var comment = content.getElementsByTagName("guf\:comment")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent;
    } catch(err) {
      try {
        comment = content.getElementsByTagName("comment")[0]
          .getElementsByTagName("CharacterString")[0].textContent;
      } catch(err) {
        var comment = ""
      };
    };
    if (comment.length == 0) {
      comment = "No comment available"
    };

    try {
      var motivation = content.getElementsByTagName("guf\:GUF_MotivationCode")[0]
        .getAttribute("codeListValue");
    } catch(err) {
      try {
        var motivation = content.getElementsByTagName("GUF_MotivationCode")[0]
          .getAttribute("codeListValue");
      } catch(err) {
        var motivation = "";
      };
    };
    if (motivation.length == 0) {
      motivation = "No motivation available";
    };

    // Get information about the "target" of the feedback
    try {
      var target = content.getElementsByTagName("guf\:GUF_FeedbackTarget")[0]
        .getElementsByTagName("guf\:resourceRef")[0]
        .getElementsByTagName("cit\:CI_Citation")[0]
        .getElementsByTagName("cit\:title")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent
    } catch(err) {
      try {
        var target = content.getElementsByTagName("GUF_FeedbackTarget")[0]
          .getElementsByTagName("resourceRef")[0]
          .getElementsByTagName("CI_Citation")[0]
          .getElementsByTagName("title")[0]
          .getElementsByTagName("CharacterString")[0].textContent
      } catch(err) {
        var target = "";
      };
    };
    if (target.length == 0) {
      target = "No info about target available";
    };

    // Get information about the "publication" related to the feedback
    try {
      var publication = content.getElementsByTagName("guf\:publication")[0]
        .getElementsByTagName("qcm\:QCM_Publication")[0]
        .getElementsByTagName("cit\:title")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent
    } catch(err) {
      try {
        var publication = content.getElementsByTagName("publication")[0]
          .getElementsByTagName("QCM_Publication")[0]
          .getElementsByTagName("title")[0]
          .getElementsByTagName("CharacterString")[0].textContent
      } catch(err) {
        var publication = "";
      };
    };
    if (publication.length == 0) {
      publication = "No publication info available";
    };

    var entryDict = {
      "title": title,
      "author": author,
      "updated": updated,
      "link": link,
      "commentId": commentId,
      "abstract": abstract,
      "rating": rating,
      "comment": comment,
      "motivation": motivation,
      "target": target,
      "publication": publication
    };

    return entryDict
  };

  this.getFromNimmbus = function(url, callback, context) {
    // Retrieve a feedback feed or a feedback item from NiMMbus and then process
    // it with a callback function. The context is used by the callback function
    // to determine how the request data must be handled.
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
      if(xhttp.readyState === 4) {
        if(xhttp.status === 200) { 
          callback(xhttp, context);
        } else {
          console.log('An error occurred during your request: ' 
            +  xhttp.status + ' ' + xhttp.statusText);
        } 
      }
    }

    xhttp.open("GET", url, true);
    xhttp.send(null);
  };

  this.renderFeedbackFeed = function(entryDict, context) {
    // Create the HTML representing the core data for a feedback item
    // and insert it into the page. If action == show, we insert the item
    // at the bottom of the list of feedback items, creating a list in reverse
    // chronological order. If action == update, we insert the item at the top
    // of the existing list, mainaining the reverse chronological order.
    var feedItem = 
      '<li data-commentId="'+entryDict['commentId']+'">\
        <div class="feedback-item">\
          <h4>'+entryDict['title']+'</h4>\
          <p>'+entryDict['updated']+' by '+entryDict['author']+'</p>\
          <div id="'+entryDict['commentId']+'" class="additional-content">\
            <p><span class="comment-part-name">Abstract: </span>'+entryDict['abstract']+'</p>\
            <p><span class="comment-part-name">Rating: </span>'+entryDict['rating']+'</p>\
            <p><span class="comment-part-name">Comment: </span>'+entryDict['comment']+'</p>\
            <p><span class="comment-part-name">Motivation: </span>'+entryDict['motivation']+'</p>\
            <p><span class="comment-part-name">Target title: </span>'+entryDict['target']+'</p>\
            <p><span class="comment-part-name">Publication title: </span>'+entryDict['publication']+'</p>\
          </div>\
          <a class="read-button">Read more</a>\
        </div>\
      </li>';
    
    if (context["action"] == "show") {
      $("#end-feedback-items").before(feedItem);
    } else if (context["action"] == "update") {
      $("#start-feedback-items").after(feedItem);
    };
    $('collapse').off();
  };

  this.showFeedbackForm = function() {
    // Open NiMMbus in a popup window. If the user enters feedback,
    // NiMMbus automatically closes the window. When the popup window
    // is closed (whether by NiMMbus or by the user if they choose not
    // make a comment), try to update feedback.
    var feedbackWindow = window
      .open(this.getAddFeedbackUrl(), "connectWindow", "scrollbars=yes");

    feedbackWindow.focus();

    var monitor = setInterval(function() {

      if (feedbackWindow.closed) {
        var url = this.getFeedbackUrl();
        getFromNimmbus(url, updateFeedback);
        clearInterval(monitor);
      }

      }, 300);

    return false;
  };

  this.xmlToEntries = function(feedbackFeed) {
    // Convert feedback feed to a list of entries.
    var xmlDoc = feedbackFeed.responseXML;
    var entries = xmlDoc.getElementsByTagName("entry");

    return entries
  };

  this.updateFeedback = function(feedbackFeed, url) {
    // Handle four cases:
    //
    // 1. If there are no entries in the feed and the no comments message is
    // present, there has been no change, so do nothing.
    // 2. If there are no entries in the feed and the no comments message is
    // not present, then all the previous comments have been deleted, so 
    // remove the old feedback list and then show the no comments message 
    // again by calling showFeedback().
    // 3. If there are entries in the feed and the no comments messages is
    // present, then the first comment or comments have just been added, so
    // remove the no comments message and show the feedback by calling 
    // showFeedback().
    // 4. If there are entries in the feed and the no comments message is not
    // present, then update the feedback with any new comments.
    var entries = this.xmlToEntries(feedbackFeed);

    // 1.
    if (entries.length == 0 && $("#no-comments-yet").length) {
      return false;
    // 2.
    } else if (entries.length == 0 && !$("#no-comments-yet").length) {
      $(".feedback-list").remove();
      this.showFeedback(feedbackFeed, context={"action": "show"});
    // 3.
    } else if (entries.length != 0 && $("#no-comments-yet").length) {
      $("#no-comments-yet").remove();
      this.showFeedback(feedbackFeed, context={"action": "show"});
    // 4.
    } else if (entries.length != 0 && !$("#no-comments-yet").length) {

      var topEntry = $("ul.feedback-list li").first();
      var topCommentId = topEntry.attr("data-commentId");

      for(var i = 0, size = entries.length; i < size ; i++){

        var entryDict = this.createBaseEntryDict(entries[i]);

        var commentId = entryDict["commentId"];

        if (commentId != topCommentId) {
          
          context = {
            "action": "update",
            "commentId": commentId
          };
          this.renderFeedbackFeed(entryDict, context);
        } else {
          this.readMore(); // Ensure updates are bound to our toggle function.
          break;
        };
      };
    };
  };

  this.readMore = function () {
    // Show/hide additional content for each feedback item.
    $(".read-button").off();
    // readMore is called each time feedback is loaded or updated,
    // so we need to call off first to prevent binding the function multiple
    // times each time the updates are added to the page.
    $(".read-button").on("click", function () {
      $readButton = $(this);
      $additionalContent = $readButton.prev();
      $additionalContent.slideToggle(200, function () {
        $readButton.text(function () {
          return $additionalContent.
            is(":visible") ? "Read less" : "Read more";
        });
      });
    });
  };

  // Add the add feedback button to the page and load the feedback.
  $("#community-feedback-anchor").after('<div id="feedback-button-center"><a href="#community-feedback" onclick="javascript:showFeedbackForm();" class="btn btn-primary">Add feedback</a></div>');
  return this.loadFeedback()
} 
