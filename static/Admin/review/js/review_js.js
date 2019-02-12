
var survey = []; //Bidimensional array: [ [1,3], [2,4] ]

//Switcher function:
$(".rb-tab").click(function(){
  //Spot switcher:
  $(this).parent().find(".rb-tab").removeClass("rb-tab-active");
  $(this).addClass("rb-tab-active");
});

//Save data:
$(".trigger").click(function(){
  //Empty array:
  survey = [];
  //Push data:
  for (i=1; i<=$(".rb").length; i++) {
    var rb = "rb" + i;
    var rbValue = parseInt($("#rb-"+i).find(".rb-tab-active").attr("data-value"));
    //Bidimensional array push:
    survey.push([i, rbValue]); //Bidimensional array: [ [1,3], [2,4] ]
  };
  //Debug:
  debug();
});

//Debug:
function debug(){
  var debug = "";
  for (i=0; i<survey.length; i++) {
      alert(survey[i][0])
    debug += "N" + survey[i][0] + " = " + survey[i][1] + "\n";
  };
          $.ajax({data:{'data':debug},url: "/student_review", success: function(result) {
              }
              });
};
