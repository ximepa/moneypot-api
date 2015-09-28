/**
 * Created by maxim on 9/28/15.
 */

(function ($) {
    $(document).ready(function () {

        var $field = $("#id_parent-autocomplete");
        var $widget = $field.parents('.autocomplete-light-widget').yourlabsWidget();
        $widget.autocomplete.data = {"all_nodes":1}

    });

})(grp.jQuery);