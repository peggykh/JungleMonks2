

	window.setTimeout(function() {
    $(".alert alert-info").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove(); 
    });
}, 5000);

