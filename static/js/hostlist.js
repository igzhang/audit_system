$(function () {

    //获取主机组数据
    $.ajax({
        url:"/api/grouplist",
        type:"GET",
        dataType:"json",
        success:function (args) {
           var group_list=$("#group_list");
           if(args.status){
               $.each(args.msg.group_list,function (k,row) {
                   var $li=$("<li>");
                   $li.prop("class","list-group-item").attr("group_id",row.servergroup__id).text(row.servergroup__groupname);
                   var $span=$("<span>");
                   $span.prop("class","badge badge-success").text(row.num);
                   $li.append($span);
                   group_list.append($li);
               });
               var $li=$("<li>");
               $li.prop("class","list-group-item").attr("group_id",-1).text("未分组主机");
               var $span=$("<span>");
               $span.prop("class","badge badge-success").text(args.msg.ungroup_num);
               $li.append($span);
               group_list.append($li);
           }else {
               console.log(args.msg);
           }
       }
    });

    //点击所选择的主机组
    $("#group_list").on("click","li",function () {
        var group_id=$(this).attr("group_id");
        $(this).addClass("list-group-item-pink").siblings("li").removeClass("list-group-item-pink");
        $.ajax({
            url:"/api/hostlist",
            type:"GET",
            data:{"group_id":group_id},
            dataType:"json",
            success:function (args) {
                if(args.status){
                    var host_list=$("#host_list");
                    host_list.empty();
                    $.each(args.msg,function (k,row) {
                        var $tr=$("<tr>");
                        var $icon=$("<td class=\"text-center\"><i class=\"demo-pli-monitor-2 icon-2x\"></i></td>");

                        var $td1=$("<td>");
                        var $span1=$("<span>");
                        $span1.prop("class","text-main text-semibold").text(row.server__ip);
                        var $small=$("<small>");
                        $small.prop("class","text-muted").text("用户名："+row.account__username+" 端口："+row.server__port);
                        $td1.append($span1).append($("<br>")).append($small);

                        var $td2=$("<td>");
                        var $span2=$("<span>");
                        $span2.prop("class","text-semibold").text(row.server__nickname);
                        $td2.prop("class","text-center").append($span2);

                        var $td3=$("<td class=\"text-center\"><span class=\"text-danger text-semibold\">登陆</span></td>");

                        $tr.append($icon).append($td1).append($td2).append($td3);
                        host_list.append($tr);
                    })
                }else {
                    console.log(args.msg);
                }
            }
        })
    })
});