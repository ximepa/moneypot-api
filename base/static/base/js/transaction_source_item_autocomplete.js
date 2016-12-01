(function ($) {
    $(document).ready(function () {
        var $body = $('body');
        var $inlines = $('.grp-tabular');

        $("#id_source-wrapper").closest("div").append(
            '&nbsp;' +
            '<img class="js-add-source" ' +
            'src="/static/base/img/warehouse-128.png" width="24px" height="24px" ' +
            'style="background-color:grey; cursor:pointer;">'
        );

        $(".js-add-source").click(function(){
            var widget = $("#id_source").parents('.autocomplete-light-widget').yourlabsWidget();
            widget.selectChoice($('<span data-value="6">ОСНОВНИЙ СКЛАД</span>'));
        });

        var set_source = function() {

            var value = $(".autocomplete-light-widget #id_source").val();

            if(!value) {
                //console.log('no source');
                return
            }

            var itemCategoryElements = $("select[id^='id_transaction_items-'][name*='category']");
            var itemSerialElements = $("select[id^='id_transaction_items-'][name*='serial']");
            var itemChunkElements = $("select[id^='id_transaction_items-'][name*='chunk']");
            var itemSelectElements = $("#invalid_selector");
            itemSelectElements = itemSelectElements.add(itemSerialElements);
            itemSelectElements = itemSelectElements.add(itemCategoryElements);
            itemSelectElements = itemSelectElements.add(itemChunkElements);
            var itemWidgetElements = itemSelectElements.parents('.autocomplete-light-widget');

            $.each(itemWidgetElements, function () {
                $(this).yourlabsWidget().autocomplete.data = $(this).yourlabsWidget().autocomplete.data || {};
                if (value) {
                    $(this).yourlabsWidget().autocomplete.data.source_id = value[0];
                } else {
                    delete $(this).yourlabsWidget().autocomplete.data.source_id;
                }
            });
        };

        var set_destination = function() {
            var itemSelectElements = $("select[id^='id_transaction_items-'][name*='destination']");
            var itemWidgetElements = itemSelectElements.parents('.autocomplete-light-widget');
            var value = $(".autocomplete-light-widget #id_destination").val();

            if(!value) {
                //console.log('no destination');
                return
            }

            $.each(itemWidgetElements, function () {
                if (value) {
                    // If value is contains something, add it to autocomplete.data
                    $(this).yourlabsWidget().autocomplete.data = {
                        'place_id': value[0]
                    };
                } else {
                    // If value is empty, empty autocomplete.data
                    $(this).yourlabsWidget().autocomplete.data = {}
                }
            });
        };

        $body.on('change', '.autocomplete-light-widget #id_source', function () {
            set_source();
        });

        set_source();

        $body.on('change', '.autocomplete-light-widget #id_destination', function () {
            set_destination();
        });

        set_destination();
        
        var set_inline_category = function($inline) {
            var value = $inline.val();

            if(!value) {
                //console.log('no inline category');
                return
            }

            var $widget = $inline.closest('.grp-tr')
                .find("select[id^='id_transaction_items-'][name*='serial']")
                .parents('.autocomplete-light-widget');
            $widget.yourlabsWidget().autocomplete.data = $widget.yourlabsWidget().autocomplete.data || {};
            if (value) {
                $widget.yourlabsWidget().autocomplete.data.category_id = value[0];
            } else {
                delete $widget.yourlabsWidget().autocomplete.data.category_id;
            }

            $widget = $inline.closest('.grp-tr')
                .find("select[id^='id_transaction_items-'][name*='chunk']")
                .parents('.autocomplete-light-widget');
            $widget.yourlabsWidget().autocomplete.data = $widget.yourlabsWidget().autocomplete.data || {};
            if (value) {
                $widget.yourlabsWidget().autocomplete.data.category_id = value[0];
            } else {
                delete $widget.yourlabsWidget().autocomplete.data.category_id;
            }

            var source = $("#id_source").val();

            if (source && value) {
                var $quantity = $inline.closest('.grp-tr').find("input[id^='id_transaction_items-'][name*='quantity']");

                $.get("/base/ajax/qty/"+source[0]+"/"+value[0]+"/?selector="+$quantity.attr('id'), function(response){
                    $("#"+response.selector).attr('placeholder', response.qty);
                });

                var $cell = $inline.closest('.grp-tr').find(".cell_from");
                var rnd = parseInt(Math.random()*10000);
                $cell.attr("id", "id_cell_from_"+rnd);

                $.get("/base/ajax/cell/"+source[0]+"/"+value[0]+"/?rnd="+rnd+"&selector="+$cell.attr('id'), function(response){
                    $("#"+response.selector).html(response.cell);
                });
            }
        };
        
        $inlines.on('change', "select[id^='id_transaction_items-'][name*='category']", function() {
            set_inline_category($(this));
        });

        $.each($inlines.find("select[id^='id_transaction_items-'][name*='category']"), function() {
            set_inline_category($(this));
        });


        $inlines.on('change', "select[id^='id_transaction_items-'][name*='-serial']", function() {
            var value = $(this).val();

            if (value) {
                var $category = $(this).closest('.grp-tr').find(
                    "input[id^='id_transaction_items-'][name*='category-autocomplete']"
                );

                $.get("/base/ajax/serial_category/"+value[0]+"/?selector="+$category.attr('id'), function(response){
                    if (response.category_id) {
                        var $autocomplete_field = $("#"+response.selector);
                        var $select = $autocomplete_field.next('select');
                        var $widget = $autocomplete_field.parents('.autocomplete-light-widget').yourlabsWidget();
                        //$autocomplete_field.val(response.category_name);
                        $select.html('<option selected="selected" value="'+response.category_id+'"></option>');
                        $widget.deck.find(".append-option-html").html('<span style="display: inline-block;"' +
                            ' class="remove">ˣ</span>'+response.category_name);
                    }
                })
            }

            var source = $("#id_source").val();

            if (source && value) {
                var $cell = $(this).closest('.grp-tr').find(".cell_from");
                var rnd = parseInt(Math.random()*10000);
                $cell.attr("id", "id_cell_from_"+rnd);

                $.get("/base/ajax/cell/"+source[0]+"/0/"+value[0]+"/?rnd="+rnd+"&selector="+$cell.attr('id'), function(response){
                    $("#"+response.selector).html(response.cell);
                });
            }

        });

    });

})(grp.jQuery);