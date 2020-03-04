let $ = django.jQuery;
var trixObj = $("trix-editor");
var idInput = trixObj.attr('input');
console.log(trixObj);
var dataValues = $(`#${idInput.data()}`);

if("trixToolbarHide" in dataValues){
    $("trix-toolbar").hide();
    delete dataValues.trixToolbarHide;
}

for (let key in dataValues){
    if (key.startsWith("trix")){
        let attrName = key.replace("trix", "").toLowerCase();
        trixObj.attr(attrName, dataValues[key]);
    }
}