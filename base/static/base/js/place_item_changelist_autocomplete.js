/**
 * Created by maxim on 9/30/15.
 */

(function ($) {
    $(document).ready(function() {

        var iter = 10;

        function check() {
            return $(".field-custom_cell .autocomplete-wrapper-js input.autocomplete").length;
        }

        function bind_events() {
            var url = $(".autocomplete-wrapper-js").data("url");
            $(".field-custom_cell .autocomplete-wrapper-js select").on("change", function(e, choice, autocomplete) {
                var $select = $(e.target);
                var cell = $select.val();
                if(cell) {
                    cell = cell[0];
                } else {
                    cell = 0;
                }
                var item = $select.closest(".autocomplete-wrapper-js").data("item-id");
                $.get(url +"/" + item + "/" + cell +"/" +
                    "?selector=" + $select.attr('id'), function(response){
                    console.log(response);
                })
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