$(function () {

    function makeHosts(row) {
        var $li=$("<li>");
        var $checkbox=$("<input>");
        $checkbox.prop("type","checkbox").val(row.id);
        var $span=$("<span>");
        $span.text(row.server__ip+"---"+row.account__username);
        $li.append($checkbox).append($span);
        return $li
    }

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
                   $li.prop("class","list-group-item").attr("group_id",row.servergroup__id);
                   var $checkbox=$("<input>");
                   $checkbox.prop("type","checkbox");
                   var $span1=$("<span>");
                   $span1.text(row.servergroup__groupname);
                   var $span=$("<span>");
                   $span.prop("class","badge badge-success").text(row.num);
                   $li.append($checkbox).append($span1).append($span);
                   group_list.append($li);
               });
               var $li=$("<li>");
               $li.prop("class","list-group-item").attr("group_id",-1);
               var $checkbox=$("<input>");
               $checkbox.prop("type","checkbox");
               var $span1=$("<span>");
               $span1.text("未分组主机");
               var $span=$("<span>");
               $span.prop("class","badge badge-success").text(args.msg.ungroup_num);
               $li.append($checkbox).append($span1).append($span);
               group_list.append($li);

               $.ajax({
                   url:"/api/hostlistall",
                   type:"GET",
                   dataType:"json",
                   success:function (ret) {
                       if(ret.status){
                           $.each(ret.msg,function (key,value) {
                               if(key==-1){
                                   var $ul=$("<ul>");
                                   $ul.prop("style","display:none");
                                   $.each(value,function (k,row) {
                                       $ul.append(makeHosts(row));
                                   });
                                   $("#group_list li[group_id='-1']").append($ul);
                               }else {
                                   var $ul=$("<ul>");
                                   $ul.prop("style","display:none");
                                   $.each(value,function (k,row) {
                                       $ul.append(makeHosts(row));
                                   });
                                   $("#group_list li[group_id="+key+"]").append($ul);

                               }
                           });
                       }else {
                           console.log(ret.msg);
                       }
                   }
               })
           }else {
               console.log(args.msg);
           }
       }
    });

    function hostCount() {
        var num=$("#group_list ul :checked").length;
        $("#host_num").text(num);
    }

    //点击所选择的主机组
    $("#group_list").on("click","li.list-group-item",function () {
        $(this).find("ul").toggle();
    });

    //主机名前的checkbox
    $("#group_list").on("click","ul :checkbox",function (event) {
        hostCount();
        event.stopPropagation();
    });

    //全选checkbox
    $("#group_list").on("click",".list-group-item>:checkbox",function (event) {
        $(this).siblings("ul").find(":checkbox").prop("checked",$(this).prop("checked"));
        hostCount();
        event.stopPropagation();
    });

});