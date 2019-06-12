// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

ckan.module('nextgeoss_read_more_paragraph', function ($) {
  return {
    initialize: function () {
      var paragraphs = this.el.children('p');
      var ellipsestext = "...";
      var moretext = "Read More";
      var lesstext = "Read Less";

      if (paragraphs.length > 1) {
        var visibleParagraph = paragraphs[0];
        var invisibleParagraphs = paragraphs.slice(1);

        visibleParagraph.append(ellipsestext);
        invisibleParagraphs.hide();

        var moreLink = $('<a>', { class: 'morelink', text: moretext });
        moreLink.insertAfter(visibleParagraph);
      }


      $(".morelink").click(function () {
        invisibleParagraphs.toggle()
        if($(this).hasClass("less")) {
            $(this).removeClass("less");
            $(this).html(moretext);
        } else {
            $(this).addClass("less");
            $(this).html(lesstext);
        }
      });
    }
  };
});
