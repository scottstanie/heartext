$(document).ready(function() {
    // CSRF setup for ajax calls
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $('#input-url-button').on('click', function() {
        var inputUrl = $('#input-url').data('grocery-id');

        console.log('input url', input-url);
        fetchTextAndInsert(url);
    });


});


function fetchTextAndInsert(url) {
    var $get = $.ajax({
        type: 'POST',
        url: '/parse/',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify(url),
        success: function(data) {
            console.log("Success getting", url);
            $('#text-input').val(data);
        }
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
