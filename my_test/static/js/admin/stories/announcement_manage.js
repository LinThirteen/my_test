$(function () {
   let $updateBtn = $(".update-btn");  // 保存按钮


   $updateBtn.click(function () {

    let $update_id = $(this).parents('li').data("announcment-id");
    let $update_content = $(this).parents('li').find('#contents').val();





    let sDataParams = {
      "content":$update_content,
      "announcment_id": $update_id,
    };


    $.ajax({
      // 请求地址
      url: "/admin/announcement_update/" + $update_id + "/",  // url尾部需要添加/
      // 请求方式
      type: "PUT",
      data: JSON.stringify(sDataParams),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          message.showSuccess("更新成功");
          // fAlert.alertSuccessToast("更新成功");

          setTimeout(function () {
            window.location.href = '/admin/announcement/';
          }, 800)
        } else {
          swal.showInputError(res.errmsg);
        }
      })

      .fail(function () {
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