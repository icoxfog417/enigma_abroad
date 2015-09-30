$(function(){
    var resultUrl = G.getCurrentUrl();
    var showResult = function(){
        var params = {
            "_xsrf": G.getXsrf()
        };
        $.post(resultUrl, params).done(function(data){
            var result = data.result;
            if(result !== undefined){
                console.log(result);
            }
       });
    }

    showResult();
})
