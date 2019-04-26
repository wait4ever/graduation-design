<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD//XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <title>微博情感倾向分析</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="css/bootstrap.css">
    <link rel="stylesheet" href="css/style.css">

    <style type="text/css">
        .background {
            display: block;
            width: 100%;
            height: 100%;
            opacity: 0.4;
            filter: alpha(opacity=40);
            background:while;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 2000;
        }
        .progressBar {
            border: solid 2px #86A5AD;
            background: white url(${pageContext.request.contextPath}/static/image/progressBar_m.gif) no-repeat 10px 10px;
        }
        .progressBar {
            display: block;
            width: 160px;
            height: 28px;
            position: fixed;
            top: 50%;
            left: 50%;
            margin-left: -74px;
            margin-top: -14px;
            padding: 10px 10px 10px 50px;
            text-align: left;
            line-height: 27px;
            font-weight: bold;
            position: absolute;
            z-index: 2001;
        }
    </style>


</head>
<body>




<!--Processbar-->
<div class="modal fade" id="loading" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" data-backdrop='static'>
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title" id="myModalLabel">提示</h4>
            </div>
            <div class="modal-body">
                正在获取微博评论信息，请稍后...<span id="result"></span>
            </div>
        </div>
    </div>
</div>

<div id="top-image">
    <div id="content" class="container center-block">
        <div class="jumbotron">
            <div class="container">
                <h1>新浪微博数据分析</h1>
                <p>请输入微博ID号，点击搜索即可获得该微博的信息。</p>
                <div class="input-group input-group-lg"> <span class="input-group-addon" id="sizing-addon1"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span></span>
                    <input id="weiboId" name="weiboId" type="text" class="form-control" placeholder="输入微博id" aria-describedby="sizing-addon1">
                    <span class="input-group-btn">
          <button class="btn btn-default" type="button" onclick=get_data()>搜 索</button>
          </span>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="js/jquery.min.js"></script>
<script src="js/ios-parallax.js"></script>
<script src="http://cdn.bootcss.com/bootstrap/3.3.0/js/bootstrap.min.js"></script>
<script type="text/javascript">

    function get_data(){
        var weiboId = $('#weiboId').val();
        var reg =/^\d{16}$/;
        if(!reg.test(weiboId)){
            alert("输入的格式不正确！（正确格式为16位数字）");
            return;
        }
        $.ajax({
            type:'get',
            url:'/analyser/test',
            data:{'weiboId':weiboId},
            beforeSend: function (xhr) {
                $('#loading').modal('show');    // 数据加载成功之前，使用loading组件
            },
            success:function(data) {
                console.log(data);
                if(data=="success"){
                    $('#loading').modal('hide');    // 成功后，隐藏loading组件
                    alert("Success!Please wait for the result for a few minutes.");


                }else{
                    $('#loading').modal('hide');    // 成功后，隐藏loading组件
                    alert("There are some errors with your input,please check the information you input.");
                }
            },
            error:function(e){
                $('#loading').modal('hide');
                console.log(e);
            }
        });

    }

    $(document).ready(function() {
        $('#top-image').iosParallax({
            movementFactor: 50
        });
    });
</script>
</body>
</html>
