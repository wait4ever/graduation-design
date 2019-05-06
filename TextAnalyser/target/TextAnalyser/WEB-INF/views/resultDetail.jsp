<%--
  Created by IntelliJ IDEA.
  User: lenovo-pc
  Date: 2019/5/4
  Time: 16:55
  To change this template use File | Settings | File Templates.
--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <meta name="viewport" content="width=device-width" />
    <title>历史</title>
    <script src="../../js/jquery.min.js"></script>


    <script src="../../js/bootstrap.js"></script>
    <link href="../../css/bootstrap.css" rel="stylesheet" />


    <script src="/js/bootstrap-table.js"></script>
    <link href="/css/bootstrap-table.css" rel="stylesheet" />
    <script src="/js/bootstrap-table-zh-CN.js"></script>

    <%--@*4、页面Js文件的引用*@--%>
    <%--<script src="~/Scripts/Home/Index.js"></script>--%>
</head>
<body onload="load()">

    <div>
        <img name="fm_plot" id="fm_plot" >
    </div>

<script>
    function load(){
        weiboId = getQueryVariable("weiboId");
        url = "/images/dataVisualization/"+weiboId+"_fm.jpg";
        $('#fm_plot').attr('src',url);


    }

    function getQueryVariable(variable)
    {
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        for (var i=0;i<vars.length;i++) {
            var pair = vars[i].split("=");
            if(pair[0] == variable){return pair[1];}
        }
        return(false);
    }
</script>

</body>
</html>
