$(function () {

  let iPage = 1;  //默认第1页
  let iTotalPage = 2; //默认总页数为2
  let bIsLoadData = false;   // 是否正在向后台加载数据

    let showHeight = $(window).height();                    //1903

    // 整个网页的高度
    let pageHeight = $(document).height();             //1914

    // 页面可以滚动的距离
    let canScrollHeight = pageHeight - showHeight ;


 $(window).scroll(function () {


    // 页面滚动了多少,这个是随着页面滚动实时变化的
    let nowScroll = $(document).scrollTop();
                                                               // 1173
    if ((canScrollHeight - nowScroll) < -350  ) {
      // 判断页数，去更新新闻数据
      canScrollHeight = canScrollHeight +490;
      if (!bIsLoadData) {
        bIsLoadData = true;
        console.log(iPage)
        // 如果当前页数据如果小于总页数，那么才去加载数据
        if (iPage < iTotalPage) {
          iPage += 1;
          setTimeout(function(){
      // 所有的逻辑
            $(".tab003").remove();  //删除标签
            fn_load_content()

                  },800);
       // $(".tab002").remove();  //删除标签
       //      fn_load_content()


        } else {
          message.showInfo('已全部加载，没有更多内容！');
          $(".tab003").remove();  // 删除标签
          $(".tab004").append($('<li style="background-color:#f4efea;border-radius:25px;text-align: center;line-height: 30px;list-style-type:none;border: 2px solid #5bc0de ;width: 200px;margin-left: 470px;margin-top: 50px" class="tab003"><a href="#tab02" class="tab002"  style="width: 50px;text-decoration:none;">已全部加载，没有更多内容！</a></li>'))

        }
      }
    }
  });


 function fn_load_content() {

    // 创建请求参数
    let sDataParams = {
      "page": iPage
    };

    // 创建ajax请求
    $.ajax({
      // 请求地址
      url: "/doc/doc_down/",  // url尾部需要添加/
      // 请求方式
      type: "GET",
      data: sDataParams,
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          iTotalPage = res.data.total_pages;  // 后端传过来的总页数
          if (iPage === 1) {
            $("#tab001").html("")
          }

          res.data.stories.forEach(function (doc) {

            let content = `  <div style="width:560px;height: 245px;background-color: #f4efea;float: left;display: inline;margin: 5px;border: 2px solid #5bc0de ;border-radius: 10px">
                    <div class=""><a href="#"><img src="${ doc.image_url }"  style="width: 196px;height: 237px;margin: 2px;border-radius: 10px"/></a>
                    <div style="width: 350px;height: 235px;float: right;background: #f4efea;margin:2px;border-radius: 10px">
                      <div style="width: 100%;height: 40px;background: #f4efea;line-height: 40px;border-radius: 10px;text-align: center;margin-top: 10px"><span style="font-size: 20px;cursor: pointer;text-decoration:none;"><a style="text-decoration:none;color: black">${ doc.title }</a></span></div>
                      <div style="width: 330px;height: 100px;background:#f4efea;border-radius: 10px;margin-top: 15px;margin-left: 10px;font-size: 16px">${ doc.digest }</div>
                      <div style="width: 100%;height: 40px;background:#f4efea;border-radius: 10px;margin-top: 15px;line-height: 40px"><span style="font-size: 18px;margin-left: 250px"><a href="/doc/${doc.id}/" style="color: red;text-decoration:none;cursor: pointer">免费下载</a></span></div>
                    </div>
                    </div>
                  </div>`;
            $(".tab-content1").append(content)


          });

          $(".tab004").append($('<li style="background-color:#f4efea;border-radius:25px;text-align: center;line-height: 30px;list-style-type:none;border: 2px solid #5bc0de ;width: 200px;margin-left: 470px;margin-top: 50px" class="tab003"><a href="#tab02" class="tab002"  style="width: 50px;text-decoration:none;">滚动加载更多</a></li></div>'));
          // 数据加载完毕，设置正在加载数据的变量为false，表示当前没有在加载数据
          bIsLoadData = false;

        } else {
          // 登录失败，打印错误信息
          message.showError(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });
  }


});