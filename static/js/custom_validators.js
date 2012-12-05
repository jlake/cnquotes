/*
 * 自定义验证项目
*/
$.extend($.validator.messages, {
	required: '该项必填',
	remote: '请修改该项',
	email: '请输入邮件地址',
	url: '请输入URL',
	dateISO: '请输入日期(ISO)',
	number: '请输入数字',
	digits: '请输入整数',
	creditcard: '请输入信用卡号码',
	equalTo: '请再次输入相同的值',
	accept: '请输入具有合法扩展名的值',
	maxlength: $.validator.format('请输入长度小于等于 {0} 的文字'),
	minlength: $.validator.format('请输入长度大于等于 {0} 的文字'),
	rangelength: $.validator.format('请输入长度为 {0} 至 {1} 的文字'),
	range: $.validator.format('请输入 {0} 至 {1} 的数字'),
	max: $.validator.format('请输入小于等于 {0} 的数字'),
	min: $.validator.format('请输入大于等于 {0} 的数字')
});

$.validator.addMethod('regex', function(value, element, param) {
	var regex = param;
	if(typeof(param) == 'string') {
		regex = new RegExp(param);
	}
	return (regex.test(value)) ? true : false;
}, '输入有误');
