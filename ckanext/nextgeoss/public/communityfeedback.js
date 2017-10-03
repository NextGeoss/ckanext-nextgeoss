function communityFeedback(catalogueID, catalogueNamespace, title)
// Create a community feedback and insert it into the page.
{
  this.catalogueID = catalogueID;
  this.catalogueNamespace = catalogueNamespace;
  this.title = title;

  this.getFeedbackUrl = function() {
    // Get the URL for feedback feed.
    var url = 'http://www.opengis.uab.cat/cgi-bin/nimmbus/nimmbus.cgi?SERVICE=WPS&REQUEST=EXECUTE&IDENTIFIER=NB_RESOURCE:ENUMERATE&LANGUAGE=eng&STARTINDEX=1&COUNT=100&FORMAT=text/xml&TYPE=FEEDBACK&TRG_TYPE_1=CITATION&TRG_FLD_1=CODE&TRG_VL_1='+this.catalogueID+'&TRG_OPR_1=EQ&TRG_NXS_1=AND&TRG_TYPE_2=CITATION&TRG_FLD_2=NAMESPACE&TRG_VL_2='+this.catalogueNamespace+'&TRG_OPR_2=EQ'
    return url
  };

  this.getAddFeedbackUrl = function() {
    // Get the URL for adding feedback.
    var url = 'http://www.opengis.uab.cat/nimmbus/index.htm?target_title='+this.title+'&target_code='+this.catalogueID+'&target_codespace='+this.catalogueNamespace+'&page=ADDFEEDBACK&share_borrower_1=Anonymous'
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

        this.getFromNimmbus(entryDict["link"], getFeedbackItem, context);

      };
    };
  };

  this.createBaseEntryDict = function(entry) {
    // Parse the entry XML from the feebdack feed and return a dictionary
    // with the important data.
    var title = entry.getElementsByTagName("title")[0].textContent;

    var author = entry.getElementsByTagName("name")[0].textContent;

    var updated = entry.getElementsByTagName("updated")[0].textContent;

    var link = entry.getElementsByTagName("link")[0].getAttribute("href");

    var commentId = link.split("RESOURCE=")[1].split("&USER=")[0];

    var entryDict = {
      "title": title,
      "author": author,
      "updated": updated,
      "link": link,
      "commentId": commentId
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

  this.getFeedbackItem = function(entry, context) {
    // Parse an individual feedback item from NiMMbus and then pass the
    // resulting dictionary to another function to be rendered and inserted
    // into the page.
    var commentId = context["commentId"];

    var feedback = entry.responseXML;

    // Parse the feedback and insert fallback values if certain
    // data is missing.
    try {
      var title = feedback.getElementsByTagName("mcc\:description")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent;
    } catch(err) {
      var title = "";
    };

    if (title.length == 0) {
      title = "Untitled";
    };

    try {
      var updated = feedback.getElementsByTagName("cit\:date")[0]
        .getElementsByTagName("gco\:DateTime")[0].textContent;
    } catch(err) {
      var updated = "";
    };

    if (updated.length == 0) {
      updated = "Undefined";
    };

    try {
      var author = feedback.getElementsByTagName("cit\:CI_Individual")[0]
        .getElementsByTagName("cit\:name")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent;
    } catch(err) {
      author = "";
    };

    if (author.length == 0) {
      author = "Unknown";
    };

    try {
      var abstract = feedback.getElementsByTagName("guf\:abstract")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent;
    } catch(err) {
      var abstract = "";
    };

    if (abstract.length == 0) {
      abstract = "No abstract available"
    };

    try {
      var rating = feedback.getElementsByTagName("guf\:GUF_RatingCode")[0]
        .getAttribute("codeListValue");
    } catch(err) {
      var rating = "No rating available"
    };

    try {
      var comment = feedback.getElementsByTagName("guf\:comment")[0]
        .getElementsByTagName("gco\:CharacterString")[0].textContent;
    } catch(err) {
      var comment = ""
    };

    if (comment.length == 0) {
      comment = "No comment available"
    };

    try {
      var motivation = feedback
        .getElementsByTagName("guf\:GUF_MotivationCode")[0]
        .getAttribute("codeListValue");
    } catch(err) {
      var motivation = "Undefined";
    };

    var entryDict = {
      "title": title,
      "commentId": commentId,
      "updated": updated,
      "author": author,
      "abstract": abstract,
      "rating": rating,
      "comment": comment
    };

    this.createFeedbackHtml(entryDict, commentId)
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
          <div id="'+entryDict['commentId']+'" class="collapse"></div>\
          <a href="#'+entryDict['commentId']+'" data-toggle="collapse" class="collapsed">\
            <span class="if-collapsed">Read more</span>\
            <span class="if-not-collapsed">Read less</span>\
          </a>\
        </div>\
      </li>';
    
    if (context["action"] == "show") {
      $("#end-feedback-items").before(feedItem);
    } else if (context["action"] == "update") {
      $("#start-feedback-items").after(feedItem);
    };
  };

  this.createFeedbackHtml = function(entryDict, commentId) {
    // Create the HTML representing a feedback item's additional data
    // and insert it into the existing item in the list.
    var feedbackItem = 
      '<p><span class="comment-part-name">Abstract: </span>'+entryDict['abstract']+'</p>\
      <p><span class="comment-part-name">Rating: </span>'+entryDict['rating']+'</p>\
      <p><span class="comment-part-name">Comment: </span>'+entryDict['comment']+'</p>\
      <p><span class="comment-part-name">Motivation: </span>'+entryDict['motivation']+'</p>'

    $("#"+entryDict["commentId"]).prepend(feedbackItem);
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
      showFeedback(feedbackFeed, context={"action": "show"});
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
          this.getFromNimmbus(entryDict["link"], getFeedbackItem, context);

        } else {
          break;
        };
      };
    };
  };

  // Add the add feedback button to the page.
  $("#community-feedback-anchor").after('<div id="feedback-button-center"><a href="#community-feedback" onclick="javascript:showFeedbackForm();" class="btn btn-primary">Add feedback</a></div>');

  return this.loadFeedback()
} 
