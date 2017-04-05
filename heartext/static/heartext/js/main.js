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
    // Turn http:// strings into <a> tags
    $('p').linkify();
    $('div').linkify();

    $('#playlist-download-btn').on('click', function() {
        let playlistId = window.location.href.substr(window.location.href.lastIndexOf('/') + 1);
        downloadPlaylist(playlistId);
    });

    $('#input-url-btn').on('click', function() {
        let inputUrl = $('#input-url').val();

        console.log('input url', inputUrl);
        fetchTextAndInsert(inputUrl);
    });

    $('#submit-text').on('click', function() {
        let title = $('#snippet-title-input').val();
        let inputText = $('#text-input').val();
        let inputUrl = $('#input-url').val();
        let voice = $('#voice-select').find('option:selected').data('voice');
        let speedFactor = $('#speed-select').val();
        console.log("Submitting text");
        submitText(title, inputText, inputUrl, voice, speedFactor);
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

function downloadPlaylist(playlistId) {
    var $dd = $.ajax({
        type: 'POST',
        url: '/polly/download_playlist/',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify({
          playlistId: 1,
        }),
        success: function(data) {
            console.log("Success");
            window.location.href = '/polly/download_zip/' + playlistId + '/';
        }
    });
}


function fetchTextAndInsert(url) {
    var $post = $.ajax({
        type: 'GET',
        url: '/parse/',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: { url: url },
        success: function(data) {
            console.log("Success getting", url);
            $('#text-input').val(data.text);
        }
    });
}

function submitText(title, text, url, voice, speedFactor=1) {
    var $post = $.ajax({
        type: 'POST',
        url: '/polly/convert/',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify({
          title: title,
          text: text,
          voice:voice,
          speed: speedFactor,
          url: url
        }),
        success: function(data) {
          console.log("converting, uplaoded to s3");
          console.log(data);
          console.log("-----")
          let snippetId = data.snippet_id;
          let jobId = data.job_id;
          let refreshId = setInterval(function() {
            $.ajax({
              type: 'GET',
              url: '/polly/progress/',
              contentType: 'application/json; charset=utf-8',
              dataType: 'json',
              data: { jobId: jobId },
              success: function(data) {
                console.log(data);
                $('#progress-bar').attr('style','width: ' + data.pct_done + '%');
                if (data.state === 'SUCCESS' || data.pct_done >= 100) {
                  clearInterval(refreshId);
                  displaySuccess(snippetId);
                }
              }
            });
          }, 500);
        }
    });
}

function pollProgress(jobId) {
  // Not implemented yet
    var $post = $.ajax({
        async: false,
        type: 'GET',
        url: '/polly/progress/',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: { jobId: jobId },
        success: function(data) {
            console.log(data);
            return data;
        }
    });
}

function displaySuccess(snippetId) {
  $('#snippet-link').html('<a href="/snippets/' + snippetId +
                          '/">Success! Click here to see the snippet details</a>');
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
