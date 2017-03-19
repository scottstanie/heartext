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

    $('#submit-text').on('click', function() {
        let inputText = $('#text-input').val();
        let speedFactor = $('#speed-up-factor').val();
        console.log("Submitting text");
        submitText(inputText, speedFactor);
    });

    $('#upload-file-name').on('change', function() {
        let file = this.files[0];
        if (file.size > 1000000) {
            alert('max upload size is 1MB')
        }

        // Also see .name, .type
    });

    $('#upload-button').on('click', function() {
    $.ajax({
        // Your server script to process the upload
        url: '/upload/',
        type: 'POST',

        // Form data
        data: new FormData($('#upload-form')[0]),

        // Tell jQuery not to process data or worry about content-type
        // You *must* include these options!
        cache: false,
        contentType: false,
        processData: false,
        success: function(data) {
            console.log("Success uploading file");
            $('#text-input').val(data.text);
        }
    });
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

function submitText(text, speedFactor=1) {
    var $post = $.ajax({
        type: 'POST',
        url: '/polly/convert/',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify({ text: text, speed: speedFactor }),
        success: function(data) {
            console.log("Success converting, now downloading");
            window.location.href = '/polly/download/'
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
