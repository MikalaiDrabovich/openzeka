/**
 * Created by super on 15.09.2016.
 */
// OpenZeka: Application delete confirmation popup
$(function () {
    $('body').confirmation({
        selector: '[data-toggle="confirmation"]'
    });

    $('.confirmation-callback').confirmation({
        onConfirm: function () {
            alert('confirm')
        },
        onCancel: function () {
            alert('cancel')
        }
    });
});
// OpenZeka: save token
$(function () {
    var submit_form = function (e) {
        var arr = $(this).attr('href').split('#');
        // save_token: equal to {{ url_for('core.save_token') }}
        $.getJSON('/save_token', {
            client_id: arr[1],
            client_secret: arr[2],
            grant_type: "client_credentials"
        }, function (data) {
            $('#client_token' + (arr[1])).text(data.result);
        });
        return false;
    };

    $('a#generate_token').bind('click', submit_form);

    $('input[type=text]').bind('keydown', function (e) {
        if (e.keyCode == 13) {
            submit_form(e);
        }
    });
});

// tabbed
$(document).ready(function () {

    $(".next-step").click(function (e) {

        var $active = $('.nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);

    });
    $(".prev-step").click(function (e) {

        var $active = $('.nav-tabs li.active');
        prevTab($active);

    });
});

// OpenZeka: Homepage image classification javascript
$(document).ready(
    function () {
        $('#classifyfile').attr('disabled', true);
        $('#imagefile').change(
            function () {
                if ($(this).val()) {
                    $('#formupload').submit();
                }
            }
        );
    }
);