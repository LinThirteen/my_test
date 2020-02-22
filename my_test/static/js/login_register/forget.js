$(function () {
    let $mobile_phone = $("#mobile");
    let $send_message = $("#sms-captcha-captcha");
    let $login = $('.form-contain');


    $mobile_phone.blur(function () {
    check_mobile_phone();
  });


  function check_mobile_phone() {
  let Mobile_phone = $mobile_phone.val();
  let sReturnValue = "";
  if (Mobile_phone === ""){
    message.showError('手机号不能为空!');
    return
  }
  if(!(/^1[345789]\d{9}$/).test(Mobile_phone)){
    message.showError('手机号码格式不正确,请重新输入！');
    return
  }
 $.ajax({
      url: '/mobiles/' + Mobile_phone + '/',
      type: 'GET',
      dataType: 'json',
      async: false
    })
      .done(function (res) {
        if (res.count !== 0) {
          message.showSuccess("电话: " + res.mobile + '   已注册')
          sReturnValue = "success"
        } else {
          message.showError("电话: " + res.mobile + '    不存在');
          sReturnValue = ""
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
        sReturnValue = ""
      });
    return sReturnValue

  }


  $send_message.click(function () {
    // 判断手机号是否输入
    if (check_mobile_phone() !== "success") {
      return
    }

    // 正常
    let SdataParams = {
      "mobile": $mobile_phone.val(),   // 获取用户输入的手机号
    };
    // for test
    // let SdataParams = {
    //   "mobile": "1806508",   // 获取用户输入的手机号
    //   "text": "ha3d",  // 获取用户输入的图片验证码文本
    //   "image_code_id": "680a5a66-d9e5-4c3c-b8ea"  // 获取图片UUID
    // };

    // 向后端发送请求
    $.ajax({
      // 请求地址
      url: "/forget_sms_codes/",
      // 请求方式
      type: "POST",
      // 向后端发送csrf token
      headers: {
                // 根据后端开启的CSRFProtect保护，cookie字段名固定为X-CSRFToken
                "X-CSRFToken": getCookie("csrf_token")
      },
      // data: JSON.stringify(SdataParams),
      data: JSON.stringify(SdataParams),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
      async: false
    })
      .done(function (res) {
        if (res.errno === "0") {
          // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
           message.showSuccess('短信验证码发送成功');
          let num = 60;
          // 设置一个计时器
          let t = setInterval(function () {
            if (num === 1) {
              // 如果计时器到最后, 清除计时器对象
              clearInterval(t);
              // 将点击获取验证码的按钮展示的文本恢复成原始文本
              $send_message.html("获取验证码");
            } else {
              num -= 1;
              // 展示倒计时信息
              $send_message.html(num + "秒");
            }
          }, 1000);
        } else {
          message.showError(res.errmsg);


        }
      })
      .fail(function(){
        message.showError('服务器超时，请重试！');
      });

  });







  $login.submit(function (e) {
    // 阻止默认提交操作
    e.preventDefault();

    // 获取用户输入的内容
    let sMobile =$mobile_phone.val();  // 获取用户输入的手机号码字符串
    let sSmsCode = $("input[name=sms_code]").val();


    // 判断手机号是否为空，是否已注册
    if (check_mobile_phone() !== "success") {
      return
    }


    // 判断用户输入的短信验证码是否为6位数字
    if (!(/^\d{6}$/).test(sSmsCode)) {
      message.showError('短信验证码格式不正确，必须为6位数字！');
      return
    }

    // 发起注册请求
    // 1、创建请求参数
    let SdataParams = {
      "mobile": sMobile,
      "sms_code": sSmsCode
    };

    // 2、创建ajax请求
    $.ajax({
      // 请求地址
      url: "/forget_login/",  // url尾部需要添加/
      // 请求方式
      type: "POST",
      data: JSON.stringify(SdataParams),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          // 注册成功
          message.showSuccess('恭喜你，登录成功！');
          setTimeout(function () {
            // 注册成功之后重定向到主页
            window.location.href = /index/;
          }, 1000)
        } else {
          // 注册失败，打印错误信息
          message.showError(res.errmsg);
            window.location.href = /forget_sms_codes/;
        }
      })
      .fail(function(){
        message.showError('服务器超时，请重试！');
      });

  });








// get cookie using jQuery
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
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

  // Setting the token on the AJAX request
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });

});