Vue.config.prefix = "data-v-";
Vue.config.delimiters = ["[[", "]]"];

var agent = new Vue({
    el: "#agent",
    data: {
        MESSAGES: ["いい感じね", "私は、ここ好きよ", "うーん、どうかしら？", "たまにはいいかもね", "ちょっと休憩するわ", "好きな人は好きかもね"],
        AGENT_URL: G.getCurrentUrl() + "/train",
        MAX_HISTORY: 3,
        selected: "",
        suggestions: [],
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
                this.selected = candidates[0].candidate_id;
                this.suggestions.push(data);
                if(this.suggestions.length > this.MAX_HISTORY){
                    this.suggestions.shift();
                }
                this.comment = this.sampleComment();
            }
        },
        sampleComment: function(){
            var index = Math.floor(Math.random() * (this.MESSAGES.length - 1));
            var c = this.MESSAGES[index];
            return c
        },
        select: function(c){
            this.selected = c.candidate_id;
        },
        feedback: function(isLike){
            var self = this;
            var params = {
              "_xsrf": G.getXsrf(),
              "candidate_id": self.candidate_id,
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
