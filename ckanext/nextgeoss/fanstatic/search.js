$().ready(function(){
   $('input[name="range_picker"]').daterangepicker({
       "locale": {
           "format": "YYYY-MM-DD",
           "separator": " - ",
           "applyLabel": "Apply",
           "cancelLabel": "Clear",
           "fromLabel": "From",
           "toLabel": "To",
           "weekLabel": "W",
           "daysOfWeek": [
               "Su",
               "Mo",
               "Tu",
               "We",
               "Th",
               "Fr",
               "Sa"
           ],
           "monthNames": [
               "January",
               "February",
               "March",
               "April",
               "May",
               "June",
               "July",
               "August",
               "September",
               "October",
               "November",
               "December"
           ],
           "firstDay": 1
       },
       "showCustomRangeLabel": true,
       "autoUpdateInput": false,
       "alwaysShowCalendars": true,
       "ranges": {
           'Today': [moment(), moment()],
           'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
           'Last 7 Days': [moment().subtract(6, 'days'), moment()],
           'Last 30 Days': [moment().subtract(29, 'days'), moment()],
           'This Month': [moment().startOf('month'), moment().endOf('month')],
           'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }).on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD') + ' - ' + picker.endDate.format('YYYY-MM-DD'));
    }).on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });

   $('input[name="timerange_start"]').daterangepicker({
       "locale": {
       "format": "YYYY-MM-DD",
       "separator": " - "
     },
      "singleDatePicker": true,
    }).on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD'));
    }).on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });  

   $('input[name="timerange_end"]').daterangepicker({
       "locale": {
       "format": "YYYY-MM-DD",
       "separator": " - "
     },
      "singleDatePicker": true,
    }).on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD'));
    }).on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });
});