var G = {
    getXsrf: function(){
        var name = "_xsrf"
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    },
    getCurrentUrl: function(){
        var url = [location.protocol, "//", location.host, location.pathname].join("");
        return url;
    }
}
