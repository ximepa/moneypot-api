(function ($) {
    $(document).ready(function () {
        $('body').on('change', '.autocomplete-light-widget select[name$=source]', function () {
            var sourceSelectElement = $(this);
            var itemSelectElements = $("select[id^='id_transaction_items-'][name*='category']");
            var itemWidgetElements = itemSelectElements.parents('.autocomplete-light-widget');

            // When the country select changes
            value = $(this).val();

            $.each(itemWidgetElements, function () {
                if (value) {
                    // If value is contains something, add it to autocomplete.data
                    $(this).yourlabsWidget().autocomplete.data = {
                        'source_id': value[0]
                    };
                } else {
                    // If value is empty, empty autocomplete.data
                    $(this).yourlabsWidget().autocomplete.data = {}
                }
            });

            // example debug statements, that does not replace using breakbpoints and a proper debugger but can hel
            // console.log($(this), 'changed to', value);
            // console.log(regionWidgetElement, 'data is', regionWidgetElement.yourlabsWidget().autocomplete.data)
        })
    });
})(grp.jQuery);