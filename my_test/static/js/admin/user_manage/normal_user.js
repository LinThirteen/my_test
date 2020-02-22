$(function () {



  // 编辑标签
  let $tagEdit = $(".btn-edit");  // 1. 获取编辑按钮
  $tagEdit.click(function () {    // 2. 点击触发事件
    let _this = this;
    let userId = $(this).parents('tr').data('id');
    let sTagName = $(this).parents('tr').data('name');
    let remark = $(this).parents('tr').data('remark');
    fAlert.alertOneInput({
      title: "编辑备注文本",
      text: "你正在编辑 " + sTagName + " 的备注",
      placeholder: "请输入备注内容",
      value: remark,
      confirmCallback: function confirmCallback(inputVal) {
        console.log(inputVal);

        let sDataParams = {
          "remark": inputVal
        };

        $.ajax({
          // 请求地址
          url: "/admin/normal_user/" + userId + "/",  // url尾部需要添加/
          // 请求方式
          type: "POST",
          data: JSON.stringify(sDataParams),
          // 请求内容的数据类型（前端发给后端的格式）
          contentType: "application/json; charset=utf-8",
          // 响应数据的格式（后端返回给前端的格式）
          dataType: "json",
        })
          .done(function (res) {
            if (res.errno === "0") {
              // 更新标签成功
              $(_this).parents('tr').find('td:nth-child(1)').text(inputVal);
              swal.close();
               setTimeout(function () {
                window.location.reload();
              }, 1000);
              message.showSuccess("备注修改成功");
            } else {
              swal.showInputError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });

      }
    });
  });


  //vip_normal
  let $type_vip = $(".btn-vip");
  $type_vip.click(function () {
    let _this = this;
    let userId = $(this).parents('tr').data('id');
    let sTagName = $(this).parents('tr').data('name');
    let type_vip = $(this).val();
    fAlert.alertConfirm({
      title: "确定将  " + sTagName + " 设为" + type_vip + "吗",
      type: "info",
      confirmText: "确认",
      cancelText: "取消",
      confirmCallback: function confirmCallback() {

        let sDataParams = {
          "type_vip": type_vip
        };

        $.ajax({
          // 请求地址
          url: "/admin/normal_user/" + userId + "/",  // url尾部需要添加/
          // 请求方式
          type: "PUT",
          data: JSON.stringify(sDataParams),
          // 请求内容的数据类型（前端发给后端的格式）
          contentType: "application/json; charset=utf-8",
          dataType: "json",
        })
          .done(function (res) {
            if (res.errno === "0") {
              // 更新标签成功
              message.showSuccess("修改成功");
               setTimeout(function () {
                window.location.reload();    //重载地址...  用于刷新网页.
              }, 800);
            } else {
              swal.showInputError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });
      }
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