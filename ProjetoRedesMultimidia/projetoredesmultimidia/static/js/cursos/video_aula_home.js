/**
 * Created by anderson on 14/11/15.
 */
$(document).ready(function(){
    $("#accordion .panel-body").find("a").on("click", function(e){ selectVideo(e); });
    function selectVideo(event){
        var a = $(event.target);
        var source = $("#area_home_video").find("source");
        var video = $("#area_home_video").find("video");

        console.log($(a));
        console.log($(source));
        path = "../../static/video/" + $(a).attr("id");
        console.log(path);
        $(source).attr("src", path);
        $(video).attr("src", path);
        console.log($(video).attr("src"))
    }
});