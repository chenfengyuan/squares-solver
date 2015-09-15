/**
 * Created by chenfengyuan on 9/15/15.
 */
angular.module('main', [])
  .controller('board', function() {
        this.squares=[];
        this.colors=["red", "pink", "blue", "gray"];
        this.max_type=4;
        this.current_color=this.colors[0];
        this.square_click = function(square){
            square.color = this.current_color;
            if(square.type == 2 || square.type == 3){
                square.dir = (square.dir + 1)% 4;
                if(square.dir == 0){
                    square.type = (square.type + 1)% this.max_type;
                }
            }else{
                square.type = (square.type + 1) % this.max_type;
            }
        };
        var i;
        this.dir_css_map=["triangle-up", "triangle-right", "triangle-down", "triangle-left"];
        this.arrow_dir_css_map=["black-triangle-up", "black-triangle-right", "black-triangle-down", "black-triangle-left"];
        for(i=0;i<100;i++){
            this.squares.push({type:0, dir:0, color:"red"});
        }
        console.log(this.squares);
    });