var MAP = null;
var MARKERS = [];
var InfoWindow = null;

Vue.config.prefix = "data-v-";
Vue.config.delimiters = ["[[", "]]"];

var agent = new Vue({
    el: "#agent",
    data: {
        MESSAGES: ["いい感じね", "私は、ここ好きよ", "うーん、どうかしら？", "たまにはいいかもね", "ちょっと休憩するわ", "好きな人は好きかもね"],
        AGENT_URL: G.getCurrentUrl() + "/train",
        MAX_HISTORY: 3,
        index: 0,
        selected: null,
        tourIndex: 0,
        images: {},
        candidates: [],
        evaluated: [],
        comment: "それじゃあ行くわよ！"
    },
    created: function(){
        var self = this;
        $.getJSON(self.AGENT_URL).done(function(data){
            self.showCandidates(data);
        });
    },
    methods: {
        showCandidates: function(data){
            var candidates = data.candidates;
            if(candidates.length > 0){
                this.candidates = candidates;
                this.setIndex(0);
                this.comment = this.sampleComment();
            }
        },
        sampleComment: function(){
            var index = Math.floor(Math.random() * (this.MESSAGES.length - 1));
            var c = this.MESSAGES[index];
            return c
        },
        next: function(){
            var i = (this.index + 1 == this.candidates.length ? 0 : this.index + 1);
            this.setIndex(i);
        },
        prev: function(){
            var i = (this.index == 0 ? this.candidates.length - 1 : this.index - 1);
            this.setIndex(i);
        },
        setIndex: function(i){
            this.index = i;
            this.selected = this.candidates[this.index];
            this.setTourIndex(0);
            if(MAP != null){
                showSpots(this.selected);
            }
        },
        setImages: function(){
            var i = (this.tourIndex == this.selected.tours.length ? 0 : this.tourIndex);
            var images = {};
            for(var m = 0; m < this.selected.tours[i].img.length; m++){
                images["img_" + (m + 1)] = this.selected.tours[i].img[m];
            }
            this.images = images;
        },
        setTourIndex: function(i){
            if(arguments.length > 0){
                this.tourIndex = i;
            }else{
                this.tourIndex = (this.tourIndex < this.selected.tours.length ? this.tourIndex + 1 : 0);
            }
            this.setImages();
        },
        feedback: function(isLike){
            var self = this;
            var params = {
              "_xsrf": G.getXsrf(),
              "candidate_id": self.selected.city.code,
              "is_like": isLike
            };
            // $("#spot").hide("slide", {direction: "left"}, "slow");
            $.post(self.AGENT_URL, params).done(function(data){
                self.showCandidates(data);
                // $("#spot").show("slide", {direction: "right"}, "slow");
            });
        },
        decide: function(){
            var url = G.getCurrentUrl() + "/result" + location.search;
            location.href = url;
        }
    }
})

function initMap(){
    MAP = new google.maps.Map(document.getElementById('map'), {
        zoom: 6
    });
    if(agent.selected != null){
        showSpots(agent.selected);
    }
}

function setMarkers(map){
    for(var m = 0; m < MARKERS.length; m++){
        MARKERS[m].setMap(map);
    }
}

function showSpots(selected){
    setMarkers(null);
    MARKERS = [];
    for(var s = 0; s < selected.spots.length; s++){
        var spot = selected.spots[s];
        var loc = new google.maps.LatLng(parseFloat(spot.lat),parseFloat(spot.lng));
        if(s == 0){
            MAP.setCenter(loc);
        }
        var m = new google.maps.Marker({
            position: loc,
            map: MAP,
            spot: spot
        });
        m.addListener("click", function(){
            if(InfoWindow != null){
                InfoWindow.close();
            }

            var $content = $("<div class='infowindow'><a href='#' class='info-title' target='spot_info_view'></a><div class='info-desc'></div></div>")
            $($content.find(".info-title")[0]).text(this.spot.name);
            $($content.find(".info-title")[0]).attr("href", this.spot.url);
            $($content.find(".info-desc")[0]).text(this.spot.description);

            InfoWindow = new google.maps.InfoWindow({
                content: $content.get(0).outerHTML
            });
            InfoWindow.open(MAP, this);
        })

        MARKERS.push(m);
    }
}
