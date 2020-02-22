$(function () {



  // 删除标签
  let $goodsDel = $(".btn-del");  // 1. 获取删除按钮
  $goodsDel.click(function () {   // 2. 点击触发事件
    let _this = this;
    let goodsId = $(this).data('goods-id');
    swal({
      title: "确定删除这条订单吗?",
      text: "删除之后，将无法恢复！",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "确定删除",
      cancelButtonText: "取消",
      closeOnConfirm: true,
      animation: 'slide-from-top',
    }, function () {

      $.ajax({
        // 请求地址
        url: "/admin/order_delete/" + goodsId + "/",  // url尾部需要添加/
        // 请求方式
        type: "DELETE",
        dataType: "json",
      })
        .done(function (res) {
          if (res.errno === "0") {
            // 更新标签成功
            message.showSuccess("删除订单成功");
            window.location.href = '/admin/order_list/';
          } else {
            swal({
              title: res.errmsg,
              type: "error",
              timer: 1000,
              showCancelButton: false,
              showConfirmButton: false,
            })
          }
        })
        .fail(function () {
          message.showError('服务器超时，请重试！');
        });
    });

  });



  //发货
  let $goodsPut = $(".btn-put");  // 1. 获取删除按钮
  $goodsPut .click(function () {   // 2. 点击触发事件
    let _this = this;
    let goodsId = $(this).data('goods-id');
    swal({
      title: "确定给这条订单发货吗?",
      text: "发货之后，将无法修改！",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#419962",
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      closeOnConfirm: true,
      animation: 'slide-from-top',
    }, function () {

      $.ajax({
        // 请求地址
        url: "/admin/order_put/" + goodsId + "/",  // url尾部需要添加/
        // 请求方式
        type: "PUT",
        dataType: "json",
      })
        .done(function (res) {
          if (res.errno === "0") {
            // 更新标签成功
            message.showSuccess("订单发货成功");
            window.location.href = '/admin/order_list/';
          } else {
            swal({
              title: res.errmsg,
              type: "error",
              timer: 1000,
              showCancelButton: false,
              showConfirmButton: false,
            })
          }
        })
        .fail(function () {
          message.showError('服务器超时，请重试！');
        });
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




