$(document).ready(function(){
	var profileContainer = $('.profileContainer'),
	header = $('.cd-main-header'),
	sidebar = $('.cd-side-nav'),
	sidebarTrigger = $('.cd-nav-trigger'),
	topNavigation = $('.cd-top-nav');

	var resizing = false;
	moveNavigation();
	console.log("it comes here");
	$.ajax({
        type:"GET",
        url:"/profile",
        datatype: 'html',
        success: function(data){
           $(".content-wrapper").html(data);
        }
    });

	$(window).on('resize', function(){
		if( !resizing ) {
			(!window.requestAnimationFrame) ? setTimeout(moveNavigation, 300) : window.requestAnimationFrame(moveNavigation);
			resizing = true;
		}
	});

	var scrolling = false;
	checkScrollbarPosition();
	$(window).on('scroll', function(){
		if( !scrolling ) {
			(!window.requestAnimationFrame) ? setTimeout(checkScrollbarPosition, 300) : window.requestAnimationFrame(checkScrollbarPosition);
			scrolling = true;
		}
	});

	function checkMQ() {
		//check if mobile or desktop device
		return window.getComputedStyle(document.querySelector('.profileContainer'), '::before').getPropertyValue('content').replace(/'/g, "").replace(/"/g, "");
	}

	function checkSelected(mq) {
		//on desktop, remove selected class from items selected on mobile/tablet version
		if( mq == 'desktop' ) $('.has-children.selected').removeClass('selected');
	}

	function checkScrollbarPosition() {
		var mq = checkMQ();
		
		if( mq != 'mobile' ) {
			var sidebarHeight = sidebar.outerHeight(),
				windowHeight = $(window).height(),
				profileContainerHeight = profileContainer.outerHeight(),
				scrollTop = $(window).scrollTop();

			( ( scrollTop + windowHeight > sidebarHeight ) && ( profileContainerHeight - sidebarHeight != 0 ) ) ? sidebar.addClass('is-fixed').css('bottom', 0) : sidebar.removeClass('is-fixed').attr('style', '');
		}
		scrolling = false;
	}



	sidebarTrigger.on('click', function(event){
		event.preventDefault();
		$([sidebar, sidebarTrigger]).toggleClass('nav-is-visible');
	});

	function moveNavigation(){
  		var mq = checkMQ();
        
        if ( mq == 'mobile' && topNavigation.parents('.cd-side-nav').length == 0 ) {
        	detachElements();
			topNavigation.appendTo(sidebar);
		} else if ( ( mq == 'tablet' || mq == 'desktop') &&  topNavigation.parents('.cd-side-nav').length > 0 ) {
			detachElements();
			topNavigation.appendTo(header.find('.cd-nav'));
		}
		checkSelected(mq);
		resizing = false;
	}

	function detachElements() {
		topNavigation.detach();
	}

});

$(".cd-side-nav li").on("click", function() {
      $(".cd-side-nav li").removeClass("active");
      $(this).addClass("active");
      console.log("this here:",this);
});

function handleClick(el){
	console.log("id here:",el.id);
	$.ajax({
        type:"GET",
        url:"/"+el.id,
        datatype: 'html',
        success: function(data){
           $(".content-wrapper").html(data);
        }
    });
}