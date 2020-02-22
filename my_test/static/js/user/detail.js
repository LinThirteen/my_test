$(function () {
  let $smsCodeBtn = $('#sms-captcha-captcha');  //获取短信验证
  let $textareas = $('#test');      //个性签名
  let $sex = $('#sex');          //性别
  let $mobile = $('#mobile');    //电话
  let $address = $('#address');  //地址
  let $detail = $('.form-contains');  // 获取注册表单元素
  let $top = $('#top');



  $smsCodeBtn.click(function () {
    // 判断手机号是否输入
    if (fn_check_mobile() !== "success") {
      return
    }

        let SdataParams = {
         "mobile": $mobile.val(),// 获取用户输入的手机号
 
       };

       // 向后端发送请求
       $.ajax({
         // 请求地址
         url: "/detail_phone/",
         // 请求方式
         type: "POST",
         // 向后端发送csrf token
         // headers: {
         //           // 根据后端开启的CSRFProtect保护，cookie字段名固定为X-CSRFToken
         //           "X-CSRFToken": getCookie("csrf_token")
         // },
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
                   $smsCodeBtn.html("获取验证码");
                 } else {
                   num -= 1;
                   // 展示倒计时信息
                   $smsCodeBtn.html(num + "秒");
                 }
               }, 1000);
             } else {
               message.showError(res.errmsg);
             }
           })
           .fail(function () {
             message.showError('服务器超时，请重试！');
           });


  });
    function fn_check_mobile() {
    let sMobile = $mobile.val();  // 获取用户输入的手机号码字符串
    let sReturnValue = "";
    if (sMobile === "") {
      message.showError('手机号不能为空！');
      return
    }
    if (!(/^1[345789]\d{9}$/).test(sMobile)) {
      message.showError('手机号码格式不正确，请重新输入！');
      return
    }
    sReturnValue = "success"

    return sReturnValue

  }



  $detail.submit(function (e) {
    // 阻止默认提交操作
    e.preventDefault();

    // 获取用户输入的内容
    let $sPassword = $("input[name=password]").val();
    let $sPasswordRepeat = $("input[name=password_repeat]").val();
    let $sMobile = $('#mobile').val();  // 获取用户输入的手机号码字符串
    let $textareas = $('#test').val();      //个性签名
    let $sex = $('#sex').val();          //性别
    let $address = $('#address').val();    //地址
    let $sSmsCode = $("input[name=sms_code]").val();//地址
    let $topimage =$('#top').attr('src');


    // 判断手机号是否为空，是否已注册
    if (fn_check_mobile() !== "success") {
      return
    }


    if(!$sPassword && !$sPasswordRepeat){

       let SdataParams = {
        "mobile": $sMobile,
        "sex": $sex,
        "address": $address,
        "textareas": $textareas,
        "sms_code": $sSmsCode,
         "topimage":$topimage
      };

      // 2、创建ajax请求
      $.ajax({
        // 请求地址
        url: "/detail_put/",  // url尾部需要添加/
        // 请求方式
        type: "PUT",
        data: JSON.stringify(SdataParams),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
      })
          .done(function (res) {
            if (res.errno === "0") {
              // 注册成功
              message.showSuccess('修改成功！');
              setTimeout(function () {
                // 注册成功之后重定向到主页
                window.location.href = /detail/;
              }, 800)
            } else {
              // 注册失败，打印错误信息
              message.showError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });

    // 判断用户输入的密码是否为空
   }else {
       // 判断用户输入的密码是否为空
      if ((!$sPassword) || (!$sPasswordRepeat)) {
        message.showError('密码或确认密码不能为空');
        return
      }

      // 判断用户输入的密码和确认密码长度是否为6-20位
      if (($sPassword.length < 6 || $sPassword.length > 20) ||
          ($sPasswordRepeat.length < 6 || $sPasswordRepeat.length > 20)) {
        message.showError('密码和确认密码的长度需在6～20位以内');
        return
      }

      // 判断用户输入的密码和确认密码是否一致
      if ($sPassword !== $sPasswordRepeat) {
        message.showError('密码和确认密码不一致');
        return
      }


      // 判断用户输入的短信验证码是否为6位数字
      if (!(/^\d{6}$/).test($sSmsCode)) {
        message.showError('短信验证码格式不正确，必须为6位数字！');
        return
      }

      // 发起注册请求
      // 1、创建请求参数
      let SdataParams = {
        "password": $sPassword,
        "password_repeat": $sPasswordRepeat,
        "mobile": $sMobile,
        "sex": $sex,
        "address": $address,
        "textareas": $textareas,
        "sms_code": $sSmsCode,
        "topimage":$topimage
      };

      // 2、创建ajax请求
      $.ajax({
        // 请求地址
        url: "/detail_put/",  // url尾部需要添加/
        // 请求方式
        type: "PUT",
        data: JSON.stringify(SdataParams),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
      })
          .done(function (res) {
            if (res.errno === "0") {
              // 注册成功
              message.showSuccess('修改成功！');
              setTimeout(function () {
                // 注册成功之后重定向到主页
                window.location.href = /detail/;
              }, 800)
            } else {
              // 注册失败，打印错误信息
              message.showError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });
    }
  });



// ================== 上传至七牛（云存储平台） ================
  let $progressBar = $(".progress-bar");
  QINIU.upload({
    "domain": "http://q2p2pu8od.bkt.clouddn.com/",  // 七牛空间域名
    "uptoken_url": "/upload_token/",	 // 后台返回 token的地址
    "browse_btn": "upload-btn",		// 按钮
    "success": function (up, file, info) {	 // 成功
      let domain = up.getOption('domain');
      let res = JSON.parse(info);
      let filePath = domain + res.key;
      console.log(filePath);
      $top.attr('src',filePath);


      // $thumbnailUrl.val('');
      // $thumbnailUrl.val(filePath);
    },
    "error": function (up, err, errTip) {
      // console.log('error');
      console.log(up);
      console.log(err);
      console.log(errTip);
      // console.log('error');
      message.showError(errTip);
    },
    "progress": function (up, file) {
      let percent = file.percent;
      $progressBar.parent().css("display", 'block');
      $progressBar.css("width", percent + '%');
      $progressBar.text(parseInt(percent) + '%');
    },
    "complete": function () {
      $progressBar.parent().css("display", 'none');
      $progressBar.css("width", '0%');
      $progressBar.text('0%');
    }
  });











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