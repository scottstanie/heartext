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


    $('#input-url-btn').on('click', function() {
        var inputUrl = $('#input-url').val();

        console.log('input url', inputUrl);
        fetchTextAndInsert(inputUrl);
    });


});


function fetchTextAndInsert(url) {
    var $post = $.ajax({
        type: 'POST',
        url: '/parse/',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify({ url: url }),
        success: function(data) {
            console.log("Success getting", url);
            $('#text-input').val(data.text);
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
