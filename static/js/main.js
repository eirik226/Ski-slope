$(function () {
    console.log( "ready!" );
	$('.utleie').on('click', function(){
	    var utleie = this;
		var post_id = $(this).find('h2').attr('id');
		$.ajax({
			type:'GET',
			url: '/delete' + '/' + post_id,
			context: utleie,
			success:function(result){
			    if(result['status'] === 1){
				    $(this).remove();
					console.log(result);
				}
			}
		});
	});
});