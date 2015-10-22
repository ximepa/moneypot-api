/**
 * Created by maxim on 10/22/15.
 */

/**
 * Created by maxim on 9/28/15.
 */

(function ($) {
    $(document).ready(function () {

        var save_warranty_date = function(serial_id, date, selector) {
            var url = "/base/ajax/serial_warranty/"+serial_id+"/"+date+"/";
            $.get(url +
                "?selector=" + selector, function(response){
                var $i = $("#"+response.selector);
                console.log($i);
                $i.removeClass("changed");
                if (!response.success) {
                    $i.addClass("error")
                }
            })
        };

        var delete_warranty_date = function(serial_id, date, selector) {
            var url = "/base/ajax/serial_warranty_delete/"+serial_id+"/";
            $.get(url +
                "?selector=" + selector, function(response){
                var $i = $("#"+response.selector);
                console.log($i);
                $i.removeClass("changed");
                if (!response.success) {
                    $i.addClass("error")
                }
            })
        };

        var $inputs = $(".date-warranty-wrapper-js input");
        var $buttons = $(".date-warranty-wrapper-js .confirm-js");

        $inputs.datepicker({dateFormat: 'yy-mm-dd'});

        $buttons.on('click', function(e){
            var $b = $(this);
            var $i = $b.parent().find('input');
            if($i.val()){
                save_warranty_date($b.parent().data('itemId'), $i.val(), $i.attr("id"));
            } else {
                delete_warranty_date($b.parent().data('itemId'), $i.val(), $i.attr("id"));
            }
        });

        $inputs.on('change', function(e) {
            $(this).removeClass("error");
            $(this).addClass("changed");
        });

    });

})(grp.jQuery);