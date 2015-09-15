/**
 * Created by chenfengyuan on 9/15/15.
 */
(function($){
    console.log($);
    var container = $('#board');
    console.log(container);
    for (var i = 0; i < 100; i++) {
        container.append('<div class="square" id="square-' + i + '"><div class="inner-square"><div class="triangle triange-red"></div></div></div>');
	}
})($);