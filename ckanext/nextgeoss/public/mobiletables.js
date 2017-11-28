function mobileTable()
// Reformat additional info/metadata tables for mobile displays.
// The relevat CSS is in nextgeoss.css.
{
  $(document).ready(
    function () { 
      if ($(window).width() < 768) {
        $( "table" ).toggleClass( "mobile-table" );
        $('table').find('td').unwrap().wrap($('<tr/>')
            );
      }
    }
  );
};