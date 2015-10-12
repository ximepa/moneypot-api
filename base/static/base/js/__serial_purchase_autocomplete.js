/**
 * Created by maxim on 9/30/15.
 */

(function ($) {
    $(document).ready(function() {

        var iter = 10;

        function check() {
            return $(".autocomplete-light-widget input.autocomplete").length;
        }

        function bind_events() {
            //var url = $(".autocomplete-wrapper-js").data("url");

            $(".autocomplete-light-widget select").on("change", function(e, choice, autocomplete) {
                var $select = $(e.target);
                var item = $select.val();
                if(item) {
                    item = item[0];
                } else {
                    item = 0;
                }

                console.log(item);

                var $field = $("#id_purchase-autocomplete");
                var $widget = $field.parents('.autocomplete-light-widget').yourlabsWidget();
                $widget.autocomplete.data = {"item_id":item}

            })
        }

        function countdown() {
            iter = iter - 1;
            console.log("countdown "+iter);
            if(!check() && iter>0) {
                setTimeout(function(){
                    countdown();
                }, 500)
            }
            else if(check()) {
                setTimeout(function(){
                    bind_events();
                }, 500)
            }
        }

        countdown();

    });

})(grp.jQuery);