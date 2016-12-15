function initTree($tree, autoopen, autoescape) {
    var error_node = null;

    function createLi(node, $li) {
        // Create edit link
        var $title = $li.find('.jqtree-title');
        $title.after('<a href="'+ node.url +'" class="edit">['+ $tree.data('label-edit') +']</a>');
        if(node.storage_url) {
            $title.after('<a href="'+ node.storage_url +'" class="edit">['+ $tree.data('label-cargo') +']</a>');
        }
        if(node.transfer_url) {
            $title.after('<a href="'+ node.transfer_url +'" class="edit">['+ $tree.data('label-transfer') +']</a>');
        }
        if(node.view_url) {
            $title.after('<a href="'+ node.view_url +'" class="edit">['+ $tree.data('label-view') +']</a>');
        }
    }

    function handleMove(e) {
        if(confirm("move node?")) {
            var info = e.move_info;
            var data = {
                target_id: info.target_node.id,
                position: info.position
            };

            removeErrorMessage();

            e.preventDefault();

            jQuery.ajax({
                type: 'POST',
                url: info.moved_node.move_url,
                data: data,
                beforeSend: function (xhr, settings) {
                    // Set Django csrf token
                    var csrftoken = jQuery.cookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function () {
                    info.do_move();
                },
                error: function () {
                    var $node = $(info.moved_node.element).find('.jqtree-element');
                    $node.append('<span class="mptt-admin-error">' + $tree.data('label-move-failed') + '</span>');

                    error_node = info.moved_node;
                }
            });
        } else {
            location.reload();
        }
        function removeErrorMessage() {
            if (error_node) {
                $(error_node.element).find('.mptt-admin-error').remove();
                error_node = null;
            }
        }
    }

    function handleLoadFailed(response) {
        $tree.html($tree.data('label-error'));
    }

    $tree.tree({
        autoOpen: autoopen,
        autoEscape: autoescape,
        dragAndDrop: true,
        onCreateLi: createLi,
        saveState: $tree.data('save_state'),
        useContextMenu: $tree.data('use_context_menu'),
        onLoadFailed: handleLoadFailed,
        closedIcon: $tree.data('rtl') == '1' ? '&#x25c0;' : '&#x25ba;'
    });

    $tree.bind('tree.move', handleMove);
}

jQuery(function() {
    var $tree = jQuery('#tree');
    var autoopen = $tree.data('auto_open');
    var autoescape = $tree.data('autoescape');

    var hash = document.location.hash.substr(1);
    var parts = hash.split("/");

    if(parts.length == 2) {
        $.getJSON("/base/get_object_ancestors/" + hash + "/", function(response) {
            var ancestors = response;
            var node_id = ancestors.pop();
            if(ancestors.length) {
                var state = {
                    "open_nodes":ancestors,
                    "selected_node":[node_id]
                };
                localStorage.setItem('base_' + parts[0].toLowerCase(), JSON.stringify(state));
                initTree($tree, autoopen, autoescape);
            }
        });
        document.location.hash = "";
    } else {
        initTree($tree, autoopen, autoescape);
    }

});
