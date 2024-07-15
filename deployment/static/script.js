function handleSubmit(event, form){
    event.preventDefault()
    var formdata = new FormData(form);

    var object = {};
    formdata.forEach(function(value, key){
        object[key] = parseFloat(value);
    });
    var json = JSON.stringify([object]);
    console.log("SENT: ", json);
    showLoader();
    fetch("/predict",{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: json,
    }).then(res=>res.json())
    .then(res=>{
        console.log("RECEIVED: ", res);
        updateResult(res[0]);
    })
}

function showLoader(){
    result_elem = document.querySelector(".result_container__result");
    result_elem.innerText = "the model is thinking";
}
function updateResult(result_value){
    result_elem = document.querySelector(".result_container__result");
    prefix = "The Model says: ";
    if (result_value==0){
        result_elem.innerText = prefix + "\"🌿 no smoke detected\"";
    }
    else if(result_value==1){
        result_elem.innerText = prefix + "💨 smoke detected";
    }
    else{
        result_elem.innerText = "something unexpected happened";
    }
}
