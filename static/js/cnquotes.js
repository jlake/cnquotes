/**
 * 中国名言名句 javascript
 *
 * @author Jlake Ou ouzhiwei(at)gmail.com
 * @version 1.0 2010-10-19
 */
$(document).ready(function() {
	var $editForm = $('#editForm');
	// 标签输入
	var winCache = {};
	$('input.easyinput').each(function(i, element) {
		var $field = $(element);
		var $helperButton = $('<span class="search" />');
		var sName = $field.attr('name');
		var $fieldLabel = $('label[for="' + sName + '"]');
		if($fieldLabel.length > 0) {
			$fieldLabel.append($helperButton);
		} else {
			$field.after($helperButton);
		}
		$helperButton.click(function(){
			$(".tagwin").hide();
			if(winCache[sName]) {
				winCache[sName].show();
			} else {
				winCache[sName] = $('<div class="tagwin">');
				var jsonData = eval('(' + $.ajax({
					url: '/helper/' + sName,
					async: false
				}).responseText + ')');
				$closeButton = $('<img src="/static/images/x-red.gif" style="margin:5px;float:right;" alt="关闭" />').click(function(e) {
					winCache[sName].hide();
				});
				var $inputHelper = $('<ul class="inputhelper" style="height:150px;" for="' + sName + '">');
				for(var i=0; i<jsonData.length; i++) {
					$item = $('<li>' + jsonData[i] + '</li>').click(function() {
						$field.val($(this).html()).focus();
						winCache[sName].hide();
					});
					$inputHelper.append($item);
				}
				var offset = $field.offset();
				var nTop = Math.round(offset.top - 175);
				var nLeft = Math.round(offset.left);
				winCache[sName].css({
					'position': 'absolute',
					'margin': 0,
					'top': nTop + 'px',
					'left': nLeft + 'px',
					'width': '600px',
					'height': '170px',
					'border': '1px solid #666',
					'border-radius': '5px',
					'padding': '2px',
					'background': '#CCC',
					'color': '#000',
					'opacity': '0.8',
					'z-index': '999'
				}).append(
					$closeButton
				).append(
					$inputHelper
				).appendTo(document.body).show();
			}

		});
	});
	// 复制，编辑
	$('a.edit,a.copy').click(function(e){
		var copyMode = $(this).hasClass('copy');
		$.get('/edit/' + $(this).attr('key'), function(json) {
			if(json.error) {
				alert(json.error);
				return false;
			}
			for(var name in json.data) {
				if(name == 'quotes') {
					$editForm.find("textarea[name='" + name + "']").val(json.data[name]);
				} else {
					$editForm.find("input[name='" + name + "']").val(json.data[name]);
				}
			}
			if(copyMode) {
				$editForm.find("input[name='key']").val('');
			} else {
				$editForm.find("input[name='key']").val(json.key);
			}
			$editForm.find("textarea[name='quotes']").focus();
		}, 'json');
	});
	$('a.delete').click(function(e){
		if(confirm('真的要删除吗？')){
			document.location.href='/delete/' + $(this).attr('key');
		}
	});
	$('input.vote').click(function(e){
		$target = $(this);
		$.post('/vote', {key: $(this).attr('key')}, function(json) {
			if(json.error) {
				alert(json.error);
				return false;
			}
			$target.siblings('span').html(json.vote_cnt);
		}, 'json')
	});

	if($editForm.length) {
		$editForm.validate({
			ignoreTitle: true,
			errorClass: 'input-error',
			errorElement: 'span'
		});
		$('#saveQuotes').click(function(){
			$editForm.submit();
		});
	}

	// 查询
	$searchForm = $('#searchForm');
	$('a.dynasty').click(function(e){
		$searchForm.find("input[name='free']").val('');
		$searchForm.find("input[name='dynasty']").val($(this).attr('filter'));
		$searchForm.submit();
	});
	$('a.category').click(function(e){
		$searchForm.find("input[name='free']").val('');
		$searchForm.find("input[name='category']").val($(this).attr('filter'));
		$searchForm.submit();
	});
	$('a.author').click(function(e){
		$searchForm.find("input[name='free']").val('');
		$searchForm.find("input[name='author']").val($(this).attr('filter'));
		$searchForm.submit();
	});
	$('a.book').click(function(e){
		$searchForm.find("input[name='free']").val('');
		$searchForm.find("input[name='book']").val($(this).attr('filter'));
		$searchForm.submit();
	});

	// 输入查询
	var _search_author = function(){
		location.href = "/?search_author=" + $('#author_name').val()
	}
	$('.search.author').click(_search_author);
	$('#author_name').keyup(function(e){
		if(e.keyCode == 13)
			_search_author();
	});
	var _search_book = function(){
		location.href = "/?search_book=" + $('#book_name').val()
	}
	$('.search.book').click(_search_book);
	$('#book_name').keyup(function(e){
		if(e.keyCode == 13)
			_search_book();
	});

	// 复制
	var bClipLoaded = false;
	var sKey = '';
	ZeroClipboard.setMoviePath( 'http://' + window.location.host + '/static/swf/ZeroClipboard.swf' );
	var clip = new ZeroClipboard.Client();

	clip.setText( '' );
	clip.hide();
	clip.setHandCursor( true );
	clip.setCSSEffects( true );

	clip.addEventListener('load', function(client){
		bClipLoaded = true;
	});

	clip.addEventListener('onMouseDown', function(client) {
		var sText = $.trim($('#' + sKey).text());
		clip.setText(sText);
	});
	/*
	clip.addEventListener('complete', function(client, text) {
		console.log("Copied text", text );
	});
	*/
	$('a.clip').live('mouseover', function(e) {
		if(!bClipLoaded) {
			clip.glue(this);
		} else {
			clip.reposition(this);
		}
		clip.show();
		sKey = $(this).attr('key');
	});
});