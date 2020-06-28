$(document).ready(function() {
    $('.spinner').hide();

    $("input[name=url]").on("invalid", function () {
        this.setCustomValidity("Please enter a valid YouTube URL.");
    });

    $('form').on('submit', function(event){
        event.preventDefault();
        var url = $('.form-control').val();
        console.log(url);

        var regex = /^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))(.{11})$/;
        var match = regex.exec(url);
        var embedded_url = 'http://www.youtube.com/embed/'+ match[1];
        $('#embedded-video').html('<div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="' + embedded_url + '" frameborder="0" allowfullscreen></iframe></div>');

        var csrftoken = $("[name=csrfmiddlewaretoken]").val();

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $(document).ajaxStart(function(){
            $('.spinner').show();
        });

        $.ajax({
            url: '/',
            dataType: 'json',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({'youtube-url': url}),

            success: function(json) {
                console.log(json);
                $(document).ajaxStop(function() {
                    $('.spinner').hide();
                });
                $('#transcript-result').html('<div class="transcript"><h6>Transcript:</h6>' + json.transcript + '</div>');
            },

            error: function(jqXhr, textStatus, errorThrown) {
                var response_json = $.parseJSON(jqXhr.responseText);
                console.log(response_json)
                $(document).ajaxStop(function() {
                    $('.spinner').hide();
                });
                if (jqXhr.status === 503) {
                    $('#transcript-result').html('<div class="error">' + response_json.error + '</div>');
                    var ajaxPOST = this;
                    var timeout = jqXhr.getResponseHeader('retry-after');
                    console.log('Retrying in ' + timeout + ' seconds');
                    setTimeout(function () {
                        $.ajax(ajaxPOST);
                    }, timeout*1000);
                }

                if (jqXhr.status === 400) {
                    $('#transcript-result').html('<div class="error">' + response_json.error + '</div>');
                }

                if (jqXhr.status === 500) {
                    $('#transcript-result').html('<div class="error">' + response_json.error + '</div>');
               }
            },
        });
    });
});
