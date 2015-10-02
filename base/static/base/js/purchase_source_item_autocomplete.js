(function ($) {
    $(document).ready(function () {

        var $inlines = $('.grp-tabular');

        $inlines.on('change', "select[id^='id_purchase_items-'][name*='category']", function() {

            var category_id = $(this).val();
            var source_id = $("#id_source").val();

            if (source_id && category_id) {
                var $price = $(this).closest('.grp-tr').find("input[id^='id_purchase_items-'][name*='price']");
                $.get("/base/ajax/price/" + source_id[0]+"/" + category_id[0]+"/" +
                    "?selector_uah=" + $($price[0]).attr('id') +
                    "&selector_usd=" + $($price[1]).attr('id'), function(response){
                    var $usd=$("#"+response.selector_usd);
                    var $uah=$("#"+response.selector_uah);
                    //$usd.val("");
                    //$uah.val("");
                    if(!(response.price_usd=="n/a") && !($usd.val())) {
                        $usd.val(response.price_usd);
                    } else {
                        $usd.attr('placeholder', response.price_usd);
                    }
                    if(!(response.price_uah=="n/a") && !($uah.val())) {
                        $uah.val(response.price_uah);
                    } else {
                        $uah.attr('placeholder', response.price_uah);
                    }
                })
            }

        });
    });

})(grp.jQuery);