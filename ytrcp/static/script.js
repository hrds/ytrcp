


 $(document).ready( function() {
        $('#result').click(function() {
           $.ajax("{{ url_for('getComments') }}").done(function (reply) {
              $('#winner').html(reply);
           });
        });
    });