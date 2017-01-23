$(document).ready(function() { 

	// обновление списка постов
	$('.upd_link').click(function(event){
		event.preventDefault();
		pk = $(this).attr('pk');
		url = '/b/update/' + pk + '/'
		$('.post_list').load(url)
	});

	// При загрузке страницы первый раз обновляет список постов
	$('.upd_link').trigger('click');
	
	// обновляет список постов раз в 10 секунд
	setInterval(function(){
		$('.upd_link').trigger('click');
	},30000)
	
	// При нажатии на кнопку пожаловаться 
	// Показывает модальное окно с формой для жалоб
	// подставляя в скрытое поле айди "цели"
	$('#main_area').on('click', '.send_complaint', function(){
		var complaint_target_id= $(this).attr('post');
		$('#overlay').fadeIn(400, 
		 	function(){
				$('#complaint_div') 
					.css('display', 'block')
					.animate({opacity: 1, top: '50%'}, 200)
					.load('/b/complaint', function(){
						$('#id_complaint_target').attr('value', complaint_target_id)
						$('#comp_form').submit(function(e){
							e.preventDefault();
							var data = $(this).serialize();
							$.ajax({
								type: 'POST',
								url: '/b/complaint/',
								data: data,
								cache: false, 
								success: function(data){
									if(data == 'ok'){
										$('#messagess_div').append('<div>Жалоба успешно отправлена</ div>')
														   .trigger('click');
										$('#overlay').trigger('click');
									} else {
										$('#messagess_div').append('<div>' + data+ '</ div>')
														   .trigger('click');										
									}
								}
							});//параметры ajax
						});// после сабмита

				});//callback function после ajax загрузки 
			});//callback function после #overlay.fadeIn
	});// конец обработчика


	// при клике на айди из списка тредов
	// открывается окно ответом 
	// туда добавляется айди
	// при сабмите - пост запрос и редирект
 	$('#main_area').on('click', '.id_link' ,function(event){
 		event.preventDefault();
		var id = $(this).attr('id');
		// Если запрос пришел со страницы списка
		// То пк вытягивается из атрибута ссылки
		// и объявляется переменная для редиректа
		if (path == '/b/'){
			var pk = $(this).attr('pk');
			var url = '/b/posting/' + pk + '/';
			var redirect_url = '/b/' + pk;
		} else {
			// тут переменную pk подставляет скрипт в начале шаблона деталки
			var url = '/b/posting/' + thread_pk + '/';
			var redirect_url = "";
		};

 		$('#post_form_div').css('display', 'block')
 							.animate({opacity: 1}, 400)
 							.load(url, function(){
			var textarea = document.getElementById('id_post_text');
			var post_res = document.getElementById('id_post_res'); 								
			textarea.focus();
			textarea.value += '[id]' + id + '[/id]';
			post_res.value += id + " ";
			$('#subm_post_form').click(function(event){
				event.preventDefault();
				$(this).hide();
				$('#posting_form').trigger('submit');
			});			
			$('#posting_form').submit(function(event){
				event.preventDefault();
				var data = $(this).serializeArray();
				var fd = new FormData();
				fd.append('post_media', $('#id_post_media')[0].files[0]);
				console.log(fd)
				for (var i = 0; i<data.length; i++){
					fd.append(data[i].name, data[i].value);
				};
				$.ajax({
					type: 'POST',
					url: url,
					data: fd,
					processData: false,
					contentType: false,
					datatype: 'json',  
					success: function(data){
						if (redirect_url != ""){
							if (data == "ok"){
								$('#id_post_text')[0].value = '';
								$('.close').trigger('click');
								$(location).attr('href', redirect_url);
							} else {
								$('#messagess_div').append('<div>' + data+ '</ div>')
								 				   .trigger('click');
							};
						} else {
							if (data == "ok"){
								$('#id_post_text')[0].value = '';
								$('.close').trigger('click');
								$('.upd_link').trigger('click');
								$('#messagess_div').append('<div>Пост успешно создан</div>')
												   .trigger('click');
							} else {
								$('#messagess_div').append('<div>' + data+ '</ div>')
											       .trigger('click');
						        $('#subm_post_form').show();
							};
						};
					} // success
				}); //Параметры ajax
			}); //обработчик сабмита
		}); //callback лоада
	}); // конец всего обработчика


 	// По клику показывает блок сообщений.
 	// Через 3 секунды убирает его и очищает. 
 	$('#messagess_div').click(function(){
 		$(this).show(200);
 		setTimeout(function(){
 			$('#messagess_div').hide(200)
 				   .empty();
 		}, 3000);
 	});

 	// По клику на "крестик" закрывает форму постинга
 	$('#post_form_div').on('click', '.close', function(){
 		$('#post_form_div').animate({opacity: 0}, 400)
 						   .css('display', 'none');	
 	});


	// Открывает пустую форму при клике на соответствующую ссылку
	// Дублирует много кода из события по .id_link
	// По возможности - переделать.
 	$('.show_form_link').click(function(event){
 		event.preventDefault();
 		var url = '/b/posting/' + pk + '/';
 		$('#post_form_div').css('display', 'block')
 							.animate({opacity: 1}, 400)
 							.load(url, function(){
			var textarea = document.getElementById('id_post_text');								
			textarea.focus();
				$('#subm_post_form').click(function(event){
					event.preventDefault();
					$(this).hide();
					$('#posting_form').trigger('submit');
				});
				$('#posting_form').submit(function(event){
					$('.b_subm').css('display', 'none');
					event.preventDefault();
					var data = $(this).serializeArray();
					var fd = new FormData();
					fd.append('post_media', $('#id_post_media')[0].files[0]);
					console.log(fd)
					for (var i = 0; i<data.length; i++){
						fd.append(data[i].name, data[i].value);
					};
				$.ajax({
					type: 'POST',
					url: url,
					data: fd,
					processData: false,
					contentType: false,
					datatype: 'json',  
					success: function(data){
						if (data == "ok"){
							$('#id_post_text')[0].value = '';
							$('#messagess_div').append('<div>Пост успешно создан</div>')
							                   .trigger('click');
							$('.upd_link').trigger('click');
							$('.close').trigger('click');
						} else {
							$('#messagess_div').append('<div>' + data+ '</ div>')
											       .trigger('click');
					        $('#subm_post_form').show();
						}; // конец if'a
					} // success
				}); //Параметры ajax
			}); //обработчик сабмита
		}); //callback лоада
	}); // конец всего обработчика


 	// Масштабирование скроллом мыши
 	// Удалить его нахуй и переписать 

 	//направление колесика 
 	var delta;

 	 //Переменная значения зума, что бы значение было присвоено 1 раз
 	var isCall = false;
 	if(!isCall){
 		var zoom = 1;
 		isCall = true;
 	}

 	// функция для добавления обработчика событий
 	function addHandler(object, event, handler){
 		if(object.addEventListener){
 			object.addEventListener(event, handler, false);
 		} else if (object.attachEvent){
 			object.attachEvent('on' + event, handler);
 			} else {
 			// ???
 			}
 		};

 	var media_content_div = document.getElementById('media_content_div');
 	var form_post_div = document.getElementById('post_form_div');

 	// добавление обработчиков для разных браузеров
	addHandler(media_content_div, 'DOMMouseScroll', wheel);
	addHandler(media_content_div, 'mousewheel', wheel);	
		

	// функция обрабатываюшая событие прокрутки
	function wheel(event){  // в this находится масштабируемый див
		event = event || window.event;
		// Опера и ИЕ работают со свойством wleelDelta
		if (event.wheelDelta){
			delta = event.wheelDelta / 120;
			// в опере значение с противоположным знаком
			if (window.opera){
				delta = -delta;
			}
			// для Gecko
		} else if (event.detail) {
			delta = -event.detail / 3;
			// Запрещаем обработку события по умолчанию, если есть
		} if (event.preventDefault){
			event.preventDefault();
		} else {
			event.returnValue = false;
		}
		target = document.getElementById($(this).attr('id'));
		// выполняем зум
		if (delta > 0) {
			zoom += 0.1;
			target.style.MozTransform = zoom; // Firefox
			target.style.OTransform = zoom; // Opera
			target.style.zoom = zoom;
		} else {
			zoom -= 0.1;
			target.style.MozTransform = zoom;
			target.style.OTransform = zoom;
			target.style.zoom = zoom;
		}
	};
 

 	// при наведении курсора на ответ
 	// показывается пост с этим ответом
 	$('#main_area').on('click', '.link_show_thread', function(event){
 		event.preventDefault();
 		var id = $(this).attr('conid');
 		var pos = $(this).offset();
 		var left = pos['left'] + 10;
 		var top = pos['top'] + 10;
 		var new_pos = {'top': top, 'left': left};
 		var url = '/b/show/' + id + '/';
 		var show_post_id = 'show_' + id;
 		var id_for_select = '#'+ show_post_id;	
 		if(!document.getElementById(show_post_id)){
	 		var div = '<div class="show" id="' + show_post_id + '">';
	 		$('#main_area').append(div);
	 		var this_post = $(id_for_select);
	 		this_post.load(url);
	 		this_post.offset(new_pos);	
	 	};	
 	});



 	// при клике на картинку в посте\треде открывается фуллсайз
 	$('#main_area').on('click', 'a.media_content', function(event){
		event.preventDefault();
		var url = $(this).attr('href')
		$('#overlay').fadeIn(400, function(){
			$('#media_content_div').css('display', 'block')
								   .html("<img src='"+ url +"' id=\'asd\'>");				 	  
		});
 	});


	// при клике на подложку "удаляются" модальные окна
	$('#overlay').click( function(){ 
		$('#complaint_div').css('display', 'none');
		$('#media_content_div').css('display', 'none');
		$('#post_form_div').css('display', 'none');
		$('#overlay').fadeOut(400);
	});

	// событие для иконки скрытия треда
	$('.hide_thread_link').click(function(){
		var id = $(this).attr('thid');
		var content_id = '#content_' + id;
		var post_list_id = '#post_list_' + id;
		var head_id = '#head_' + id;
		if ($(this).attr('hide') == 'false'){
			$(this).removeClass('glyphicon-minus-sign')
					.addClass('glyphicon-plus-sign')
					.attr('hide', 'true');
			$(content_id).css('display', 'none');
			$(post_list_id).css('display', 'none');
			$(head_id).addClass('hide_thread_head');
		} else {
			$(this).removeClass('glyphicon-plus-sign')
					.addClass('glyphicon-minus-sign')
					.attr('hide', 'false');
			$(content_id).css('display', 'block');
			$(post_list_id).css('display', 'block');
			$(head_id).removeClass('hide_thread_head');		
		};
	});

	// событие на клик по иконке "показать тред"
	// только для скрытых постов
	$('.show_thread_link').click(function(){
		var id = $(this).attr('thid');
		alert(id)
		var content_id = '#content_' + id;
		var post_list_id = '#post_list_' + id;
		var head_id = '#head_' + id;
		$(this).removeClass('glyphicon-plus-sign show_thread_link')
				.addClass('glyphicon-minus-sign hide_thread_link')
		$(content_id).css('display', 'block');
		$(post_list_id).css('display', 'block');
		$(head_id).removeClass('hide_thread_head');
	});



	// По клику удаляет сплывающий пост со страницы
	$('#main_area').on('dblclick', '.show', function(){
		$(this).remove();
	})
	$('#main_area').on('click', '.pop_close', function(){
		var id = "#show_" + $(this).attr('pid');
		console.log(id)
		$(id).remove();
	});

	// событие показывает скрытый текст у тредов с длинным текстом
	$('.short_text').click(function(event){
		event.preventDefault();
		tid = $(this).attr('tid');
		sel_st = '#st_' + tid
		sel_ft = '#ft_' + tid
		$(sel_st).css('display', 'none')
		$(sel_ft).css('display', 'inline')		

	});

	// показывает/скрывает форму создания треда
	$('#create_form_link').click(function(){
		$('#create_form').slideToggle(200);
	});



	// При наведении на показанный пост он становится перетаскиваемым
	// (костыль, потом переделать)
	$('#main_area').on('mouseenter', '.show', function(){
		$(this).draggable();
	})

	// перетаскиваемые элементы на странице
	$('#media_content_div').draggable();
	$('#post_form_div').resizable({handles:'all'});


}); // document.ready()

