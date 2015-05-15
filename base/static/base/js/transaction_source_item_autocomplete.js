(function ($) {
    $(document).ready(function () {
        var $body = $('body');
        var $inlines = $('.grp-tabular');

        $body.on('change', '.autocomplete-light-widget #id_source', function () {
            var itemCategoryElements = $("select[id^='id_transaction_items-'][name*='category']");
            var itemSerialElements = $("select[id^='id_transaction_items-'][name*='serial']");
            var itemSelectElements = $("#invalid_selector");
            itemSelectElements = itemSelectElements.add(itemSerialElements);
            itemSelectElements = itemSelectElements.add(itemCategoryElements);
            var itemWidgetElements = itemSelectElements.parents('.autocomplete-light-widget');

            // When the country select changes
            var value = $(this).val();

            $.each(itemWidgetElements, function () {
                $(this).yourlabsWidget().autocomplete.data = $(this).yourlabsWidget().autocomplete.data || {};
                if (value) {
                    // If value is contains something, add it to autocomplete.data
                    $(this).yourlabsWidget().autocomplete.data.source_id = value[0];
                } else {
                    // If value is empty, empty autocomplete.data
                    delete $(this).yourlabsWidget().autocomplete.data.source_id;
                }
            });
        });

        $body.on('change', '.autocomplete-light-widget #id_destination', function () {
            var itemSelectElements = $("select[id^='id_transaction_items-'][name*='destination']");
            var itemWidgetElements = itemSelectElements.parents('.autocomplete-light-widget');

            // When the country select changes
            var value = $(this).val();

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
        });

        $inlines.on('change', "select[id^='id_transaction_items-'][name*='category']", function() {
            var value = $(this).val();

            var $widget = $(this).closest('.grp-tr')
                .find("select[id^='id_transaction_items-'][name*='serial']")
                .parents('.autocomplete-light-widget');
            $widget.yourlabsWidget().autocomplete.data = $widget.yourlabsWidget().autocomplete.data || {};
            if (value) {
                $widget.yourlabsWidget().autocomplete.data.category_id = value[0];
            } else {
                delete $widget.yourlabsWidget().autocomplete.data.category_id;
            }
            console.log($widget.yourlabsWidget().autocomplete.data);
        });
    });

})(grp.jQuery);