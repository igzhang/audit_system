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

    //更改上传下载方式
    $("#file_mode_choice").change(function () {
        if($(this).val()=="upload"){
            $("#demo-dropzone").show();
            $("#download_button").addClass("hide");
        }else {
            $("#demo-dropzone").hide();
            $("#download_button").removeClass("hide");
        }

    });

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

    //根据task_id获取执行结果
    var percent;
    function getCMDLog(task_id) {
        var percent_num="";
        var done_num=0;
        $.ajax({
            url:"/api/cmdresult",
            data:{"task_id":task_id},
            type:"GET",
            dataType:"json",
            success:function (args) {
                if(args.status){
                    $("#cmd_result").empty();
                    $.each(args.msg,function (i,row) {
                        if(row.status!=3){
                            done_num+=1;
                        }
                        var $p1=$("<p>");
                        $p1.text(
                            "IP："+row.connect__server__ip+
                            "   用户名："+row.connect__account__username+
                            "   状态："+row.status
                        );
                        var $pre=$("<pre></pre>");
                        $pre.text(row.result);
                        $("#cmd_result").append($p1).append($pre);
                    });
                    percent_num=done_num/host_submit_num*100+"%";
                    if(percent_num=="100%"){
                        clearInterval(getting);
                    }
                    $("#process_bar").css("width",percent_num).text(percent_num);
                }else {
                    console.log(args.msg)
                }
            }
        })
    }

    //批量命令提交按钮
    var host_submit_num;
    var getting;
    $("#cmd_run").click(function () {
        var mode=$("#file_mode_choice").val();
        var host_id_list=[];
        $("#group_list ul :checked").each(function () {
           host_id_list.push($(this).val());
        });
        var server_path=$.trim($("#server_path").val());
        host_submit_num=host_id_list.length;
        if(host_submit_num==0){
            alert("请选择要执行的主机");
        }else {
            if(server_path){
                $.ajax({
                    url:"/api/multirun",
                    type:"POST",
                    data:{"host_id_list":host_id_list,"cmd":server_path,"type":mode,"uid":$("#uid").val(),
                        "csrfmiddlewaretoken":$("input[name='csrfmiddlewaretoken']").val()},
                    dataType:"json",
                    success:function (ret) {
                        if(ret.status){
                            $("#download_button").prop("href","/api/filedownload?taskid="+ret.msg);
                            getCMDLog(ret.msg);
                            getting=setInterval(getCMDLog,2000,ret.msg);
                        }else {
                            console.log(ret.msg)
                        }
                    }
                })
            }else {
                alert("请输入服务器路径");
            }
        }
    });
});