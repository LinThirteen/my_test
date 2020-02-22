$(function () {

  fn_load_banner_category();
  fn_index_categroy();
  function fn_load_banner_category() {
    $.ajax({
      // 请求地址
      url: "/index/banner/",  // url尾部需要添加/
      // 请求方式
      type: "GET",
      async: false
    })
      .done(function (res) {
        if (res.errno === "0") {
          let content = ``;
          res.data.banner.forEach(function (one_banner, index) {
            if (index === 0){
              if(one_banner.stories_price){
                 content = `
                    <div class="item active"><a href="/buy_index/${one_banner.stories_id}">
                                    <img src="${one_banner.image_url}" alt="${one_banner.stories_title}" style="width: 100%">
                                    <div class="carousel-caption">
                                        <h3>...</h3>
                                        <p>...</p>
                                    </div>
                                </div>
              `;

              }else{
              content = `
                    <div class="item active"><a href="/read/${one_banner.stories_id}">
                                    <img src="${one_banner.image_url}" alt="${one_banner.stories_title}" style="width: 100%">
                                    <div class="carousel-caption">
                                        <h3>...</h3>
                                        <p>...</p>
                                    </div>
                                </div>
              `;}
            } else {
              if(one_banner.stories_price){
              content = `
              <div class="item"><a href="/buy_index/${one_banner.stories_id}">
                                    <img src="${one_banner.image_url}" alt="${one_banner.stories_title}" style="width: 100%">
                                    <div class="carousel-caption">
                                        <h3>...</h3>
                                        <p>...</p>
                                    </div>
                                </div>
              `;}else{

                 content = `
              <div class="item"><a href="/read/${one_banner.stories_id}">
                                    <img src="${one_banner.image_url}" alt="${one_banner.stories_title}" style="width: 100%">
                                    <div class="carousel-caption">
                                        <h3>...</h3>
                                        <p>...</p>
                                    </div>
                                </div>
              `;
              }

            }
            $("#carousel-inner").append(content);
          });
          res.data.tag.forEach(function (one_tag, index) {
            if (index === 0){
              content = `<li class="active" role="presentation" id="ac">
                            <a href="/read/chapter/${one_tag.tag_id}" aria-controls="tab${one_tag.tag_id}" role="tab" data-toggle="tab" id ="${one_tag.tag_id}" >${one_tag.tag_name}</a>
                        </li>`;
              tb_content = `<div class="tab-pane fade in active" role="tabpanel" id="tab${one_tag.tag_id}"></div><div class="row" id="categroy"></div>`;
            } else if((index === 1)){
              content = ` <li role="presentation">
                            <a href="/read/chapter/${one_tag.tag_id}" aria-controls="tab${one_tag.tag_id}" role="tab" data-toggle="tab" id ="${one_tag.tag_id}" >${one_tag.tag_name}</a>
                        </li>`;
                tb_content = `<div class="tab-pane fade " role="tabpanel" id="tab${one_tag.tag_id}"></div><div class="row"></div>`;

            }else if((index === 2)){
              content = ` <li role="presentation">
                            <a href="/read/chapter/${one_tag.tag_id}" aria-controls="tab${one_tag.tag_id}" role="tab" data-toggle="tab" id ="${one_tag.tag_id}" >${one_tag.tag_name}</a>
                        </li>`;
                tb_content = `<div class="tab-pane fade " role="tabpanel" id="tab${one_tag.tag_id}"></div><div class="row"></div>`;


            }else if((index === 3)){
              content = ` <li role="presentation">
                            <a href="/read/chapter/${one_tag.tag_id}" aria-controls="tab${one_tag.tag_id}" role="tab" data-toggle="tab" id ="${one_tag.tag_id}" >${one_tag.tag_name}</a>
                        </li>`;
                tb_content = `<div class="tab-pane fade " role="tabpanel" id="tab${one_tag.tag_id}"></div><div class="row"></div>`;

            }
            $("#myTab").append(content);
            $("#tab_first").append(tb_content);
          });

        } else {
          // 登录失败，打印错误信息
          message.showError(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });
  }

  // 首次展示分类内容
  function fn_index_categroy() {
    let $active = $('#ac').children('a').attr('id');

     let sDataParams = {
      "tag_id": $active,

    };
      $.ajax({
      // 请求地址
      url: "/category/",  // url尾部需要添加/
      // 请求方式
      type: "GET",
      data: sDataParams,
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          res.data.category_stories.forEach(function (one_story) {
            let content = ` <div class="col-md-3 col-xs-6">
                                    <a href="/read/${one_story.stories_id}" id="${one_story.stories_id}"><img src="${one_story.stories_image}" width="100%" height="245px"/></a>
                                    <h5 class="h-title">${one_story.stories_title}</h5>                               
                            </div>
                        `;

            $("#categroy").append(content)
          });


        } else {
          // 登录失败，打印错误信息
          message.showError(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });
  }


  let $categoryLi = $("#carousels ul li");
  let sCurrentTagId = 0;
  let iPage = 1;  //默认第1页
  let iTotalPage = 2; //默认总页数为2
  let bIsLoadData = false;   // 是否正在向后台加载数据


  $categoryLi.click(function () {
    // 点击分类标签，则为点击的标签加上一个class属性为active
    // 并移除其它兄弟元素上的，值为active的class属性
    $(this).addClass('active').siblings('li').removeClass('active');
    // 获取绑定在当前选中分类上的data-id属性值
    let sClickTagId = $(this).children('a').attr('id');

    if (sClickTagId !== sCurrentTagId) {
            sCurrentTagId = sClickTagId;  // 记录当前分类id
            // 重置分页参数

            fn_load_category()
        }
  });
  function fn_load_category() {
    let sDataParams = {
      "tag_id": sCurrentTagId,

    };

    // 创建ajax请求
    $.ajax({
      // 请求地址
      url: "/category/",  // url尾部需要添加/
      // 请求方式
      type: "GET",
      data: sDataParams,
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          $("#categroy").children('div').remove();
          res.data.category_stories.forEach(function (one_story) {
            let content = ` <div class="col-md-3 col-xs-6">
                                    <a href="/read/${one_story.stories_id}" id="${one_story.stories_id}"><img src="${one_story.stories_image}" width="100%" height="245px"/></a>
                                    <h5 class="h-title">${one_story.stories_title}</h5>                               
                            </div>
                        `;

            $("#categroy").append(content)
          });


        } else {
          // 登录失败，打印错误信息
          message.showError(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  }

    let showHeight = $(window).height();                    //1903

    // 整个网页的高度
    let pageHeight = $(document).height();             //1914

    // 页面可以滚动的距离
    let canScrollHeight = pageHeight - showHeight + 1100;


 $(window).scroll(function () {
    // 浏览器窗口高度
    // let showHeight = $(window).height();                    //1903
    //
    // // 整个网页的高度
    // let pageHeight = $(document).height();             //1914
    //
    // // 页面可以滚动的距离
    // let canScrollHeight = pageHeight - showHeight + 1100;

    // 页面滚动了多少,这个是随着页面滚动实时变化的
    let nowScroll = $(document).scrollTop();
                                                               // 1173
    if ((canScrollHeight - nowScroll) < 100) {
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
          $(".tab004").append($('<li style="background-color:white;border-radius:25px;line-height: 30px;list-style-type:none;border: 1px solid #2593a2;width: 230px;margin-left: 300px" class="tab003">\n' +
              '                              <a href="#tab02" class="tab002"  style="width: 30px;padding-left:30px">已全部加载，没有更多内容！</a></li>'))

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
      url: "/index_story/",  // url尾部需要添加/
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

          res.data.stories.forEach(function (storys) {
            if(storys.price == 0){
            let content = ` <div class="thumbnail col-md-3 col-xs-6">
                                        <a href="/read/${storys.id}"><img src="${storys.image_url}" style="width: 100%;height: 245px"/></a>
                                        <h5 class="h-title">${storys.title}</h5>
                                        <p class="price">
                                          <div style="float: left">
                                            <span style="margin-left: 5px;">价格:</span>
                                            <span style="color: red;"><strong>免费</strong></span>
                                    </div>
                                      
                                        <div style="float: right">
                                            <span style="font-size: 13px;">点击量:</span>
                                          <del class="text-muted" style="text-decoration:none;font-size: 13px;margin-right: 5px;">${storys.clicks}</del></div>
                                        </p>
                                    </div>`;
            $("#tab001").append(content)
        }else{


          let content = ` <div class="thumbnail col-md-3 col-xs-6">
                                        <a href="/buy_index/${storys.id}/"><img src="${storys.image_url}" style="width: 100%;height: 245px"/></a>
                                        <h5 class="h-title">${storys.title}</h5>
                                        <p class="price">
                                          <div style="float: left">
                                            <span style="margin-left: 5px;">价格:</span>
                                            <span style="color: red;"><strong>${storys.price}元</strong></span>
                                    </div>
                                      
                                        <div style="float: right">
                                            <span style="font-size: 13px;">点击量:</span>
                                          <del class="text-muted" style="text-decoration:none;font-size: 13px;margin-right: 5px;">${storys.clicks}</del></div>
                                        </p>
                                    </div>`;

          $("#tab001").append(content)
            }

          });

          $(".tab004").append($('<li style="background-color:white;border-radius:25px;line-height: 30px;list-style-type:none;border: 1px solid #2593a2;width: 150px;margin-left: 350px" class="tab003">\n' +
              '                              <a href="#tab02" class="tab002"  style="width: 30px;padding-left:30px">滚动加载更多</a></li>'));
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