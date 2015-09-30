$(function(){
    createUrl = function(){
        var budget = $(this).data("value");
        $.post("/group", {
                "_xsrf": G.getXsrf(),
                "budget": budget,
                "deadline": moment().add(1, "m").format("YYYY/MM/DD HH:mm:ss")
            }
        ).done(bindUrl);
    }
    bindUrl = function(data){
        $("#share").show();
        $("#url").attr("href", data.url);
        $("#message").text("これから飛ぶから、行きたい場所が見えたら教えてね。");
    }
    $(".submit").click(createUrl)
})
